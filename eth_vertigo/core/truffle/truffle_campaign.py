from eth_vertigo.mutator.mutator import Mutator
from eth_vertigo.mutator.truffle.solidity_file import SolidityFile
from eth_vertigo.mutator.solidity.solidity_mutator import SolidityMutator
from eth_vertigo.test_runner.truffle import TruffleRunnerFactory
from eth_vertigo.test_runner.exceptions import EquivalentMutant
from eth_vertigo.core import Mutation, MutationResult
from eth_vertigo.core.campaign import Campaign
from eth_vertigo.core.truffle.truffle_compiler import TruffleCompiler
from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut
from eth_vertigo.core.network import NetworkPool
from typing import List, Callable
from time import time
from pathlib import Path
import logging
from queue import Queue


class TruffleCampaign(Campaign):
    """
    A TruffleCampaign class

    Implements specific campaign logic for the truffle framework
    """
    def __init__(
            self,
            project_directory: Path,
            truffle_compiler: TruffleCompiler,
            truffle_runner_factory: TruffleRunnerFactory,
            mutators: List[Mutator],
            network_pool: NetworkPool,
            filters=None,
            suggesters=None
    ):
        super().__init__(filters=filters, suggesters=suggesters)
        self.project_directory = project_directory
        self.source_directory = project_directory / "build" / "contracts"
        self.truffle_compiler = truffle_compiler

        self.sources = list(self._get_sources())
        self.base_run_time = None
        self.network_pool = network_pool
        self.bytecodes = {}

        self.truffle_runner_factory = truffle_runner_factory
        self.mutators = mutators
        self.mutators.append(SolidityMutator())

    def _get_sources(self, dir=None):
        """ Implements basic mutator file discovery """
        if not (self.project_directory / "build").exists():
            self.truffle_compiler.run_compile_command(str(self.project_directory))

        dir = dir or self.source_directory
        for source_file in dir.iterdir():
            if source_file.name == "Migrations.json":
                continue
            if not source_file.name.endswith(".json"):
                continue
            yield SolidityFile(source_file)

    def valid(self):
        """ Checks whether the current project is valid """
        tr = self.truffle_runner_factory.create(str(self.project_directory))

        begin = time()

        network = None
        try:
            network = self.network_pool.claim()
        except ValueError:
            return False

        try:
            test_result = tr.run_tests(network=network)
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
        tr = self.truffle_runner_factory.create(str(self.project_directory))
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
                test_result = tr.run_tests(
                    mutation=mutation,
                    timeout=int(self.base_run_time) * 2,
                    network=network,
                    original_bytecode=self.bytecodes,
                    suggestions=suggestions if suggestions else None
                )
                killers = [test for test in test_result.values() if not test.success]
                if killers:
                    mutation.result = MutationResult.KILLED
                    mutation.crime_scenes = [killer.full_title for killer in killers]
                elif suggestions:
                    # If the suggestions didn't lead to a killer
                    test_result = tr.run_tests(
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
        finally:
            self.network_pool.yield_network(network)
            done_callback()
            return

    def store_compilation_results(self):
        """ Stores compilation results for trivial compiler equivalence"""
        self.bytecodes = self.truffle_compiler.get_bytecodes(working_directory=str(self.project_directory))
