import logging
from abc import abstractmethod, ABC
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import time
from typing import List, Callable

from jinja2 import PackageLoader, Environment

from eth_vertigo.core import Mutation, MutationResult
from eth_vertigo.core import TestSuggester
from eth_vertigo.core.filter import MutationFilter
from eth_vertigo.core.network import NetworkPool
from eth_vertigo.interfaces.generics import Compiler, Tester
from eth_vertigo.mutator.mutator import Mutator
from eth_vertigo.mutator.solidity.solidity_mutator import SolidityMutator
from eth_vertigo.mutator.source_file import SourceFile
from eth_vertigo.test_runner.exceptions import EquivalentMutant
from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut

environment = Environment(
        loader=PackageLoader("eth_vertigo.core"), trim_blocks=True
    )


class CampaignReport:
    def __init__(self, mutations):
        """
        Constructs a campaign report object
        :param mutations: Mutations for this campaign
        """
        self.mutations = mutations

    @property
    def mutation_count(self):
        """ Amount of mutations in this report """
        return len(self.mutations)

    @property
    def nr_killed(self):
        """ Amount of killed mutations in this report"""
        return len([e for e in self.mutations if e.result == MutationResult.KILLED])

    @property
    def nr_alive(self):
        """ Amount of alive mutations in this report"""
        return len([e for e in self.mutations if e.result == MutationResult.LIVED])

    def render(self, with_mutations=False):
        template = environment.get_template("report_template.jinja2")
        return template.render(
            nr_mutations=len(self.mutations),
            nr_killed=self.nr_killed,
            mutations=self.mutations,
            with_mutations=with_mutations
        )


class Campaign:
    """
    A core campaign class orchestrates and manages a core testing run
    """

    def __init__(self, filters: List[MutationFilter] = None , suggesters=None):
        self.sources = []
        self.project_directory = None
        self.mutations = []
        self.is_set_up = False
        self.filters = filters or []
        self.suggesters = suggesters or []  # type: List[TestSuggester]

    def setup(self):
        """ Sets up the campaign for execution"""
        raise NotImplementedError

    def run(self, progress_callback: Callable, threads=1):
        """ Starts a core testing campaign"""
        if not self.is_set_up:
            raise ValueError("This campaign is not setup yet")

        report = CampaignReport(self.mutations)
        with ThreadPoolExecutor(max_workers=threads) as e:
            for mutation in self.mutations:
                e.submit(self.test_mutation, mutation, progress_callback)
            e.shutdown()
        return report

    def test_mutation(self, mutation: Mutation, done_callback: Callable):
        """ Run the test suite using a core and check for murders """
        raise NotImplementedError

    def valid(self):
        """ Checks whether the current project is valid """
        raise NotImplementedError

    def store_compilation_results(self):
        """ Stores compilation results for trivial compiler equivalence"""
        raise NotImplementedError


class BaseCampaign(ABC, Campaign):
    def __init__(
            self,
            project_directory: Path,
            mutators: List[Mutator],
            network_pool: NetworkPool,

            compiler: Compiler,
            tester: Tester,
            source_file_builder: Callable[[Path, str], SourceFile],

            filters=None,
            suggesters=None
    ):
        super().__init__(filters=filters, suggesters=suggesters)

        self.project_directory = project_directory
        self.source_directory = project_directory / "build" / "contracts"

        self.compiler = compiler
        self.tester = tester
        self.source_file_builder = source_file_builder

        self.sources = list(self._get_sources())
        self.base_run_time = None
        self.network_pool = network_pool
        self.bytecodes = {}

        self.mutators = mutators
        self.mutators.append(SolidityMutator())

    @abstractmethod
    def _get_sources(self, dir=None):
        """ Implements basic mutator file discovery """
        pass

    def valid(self):
        """ Checks whether the current project is valid """
        begin = time()

        network = None
        try:
            network = self.network_pool.claim()
        except ValueError:
            return False

        try:
            test_result = self.tester.run_tests(network=network)
        finally:
            self.network_pool.yield_network(network)

        self.base_run_time = time() - begin
        if test_result is None:
            return False

        return all([result.success for result in test_result.values()])

    def setup(self):
        for source in self.sources:
            for mutator in self.mutators:
                self.mutations += mutator.mutate(source, self.project_directory)
        for f in self.filters:
            self.mutations = f.apply(self.mutations)
        self.is_set_up = True


    def test_mutation(self, mutation: Mutation, done_callback: Callable):
        """ Run the test suite using a core and check for murders """
        mutation.result = MutationResult.LIVED
        try:
            network = self.network_pool.claim()
        except ValueError:
            mutation.result = MutationResult.ERROR
            return
        suggestions = []
        for suggester in self.suggesters:
            if suggester.is_strict:
                # Not yet Implemented
                continue
            suggestions.extend(suggester.suggest_tests(mutation))

        try:
            try:
                test_result = self.tester.run_tests(
                    mutation=mutation,
                    timeout=int(self.base_run_time) * 2,
                    network=network,
                    original_bytecode=self.bytecodes,
                    keep_test_names=suggestions if suggestions else None
                )
                killers = [test for test in test_result.values() if not test.success]
                if killers:
                    mutation.result = MutationResult.KILLED
                    mutation.crime_scenes = [killer.full_title for killer in killers]
                elif suggestions:
                    # If the suggestions didn't lead to a killer
                    test_result = self.tester.run_tests(
                        mutation=mutation,
                        timeout=int(self.base_run_time) * 2,
                        network=network,
                        original_bytecode=self.bytecodes,
                    )
                    killers = [test for test in test_result.values() if not test.success]
                    if killers:
                        mutation.result = MutationResult.KILLED
                        mutation.crime_scenes = [killer.full_title for killer in killers]
            except EquivalentMutant:
                mutation.result = MutationResult.EQUIVALENT
        except TimedOut:
            mutation.result = MutationResult.TIMEDOUT
        except TestRunException as e:
            logging.warning(str(e))
            mutation.result = MutationResult.ERROR
        except Exception as e:
            print(e)
        finally:
            self.network_pool.yield_network(network)
            done_callback()
            return

    def store_compilation_results(self):
        """ Stores compilation results for trivial compiler equivalence"""
        self.bytecodes = self.compiler.get_bytecodes(working_directory=str(self.project_directory))
