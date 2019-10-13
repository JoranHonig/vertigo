from eth_vertigo.mutator.mutator import Mutator
from eth_vertigo.mutator.truffle.solidity_file import SolidityFile
from eth_vertigo.mutator.solidity.solidity_mutator import SolidityMutator
from eth_vertigo.test_runner.truffle import TruffleRunnerFactory
from eth_vertigo.test_runner.exceptions import EquivalentMutant
from eth_vertigo.core import Mutation, MutationResult
from eth_vertigo.core.campaign import Campaign
from eth_vertigo.core.truffle.truffle_compiler import TruffleCompiler
from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut

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
            networks: List[str] = (),
            filters=None
    ):
        super().__init__(filters=filters)
        self.project_directory = project_directory
        self.source_directory = project_directory / "build" / "contracts"
        self.truffle_compiler = truffle_compiler

        self.sources = list(self._get_sources())
        self.base_run_time = None
        self.networks = networks
        self.networks_queue = Queue(maxsize=len(networks))
        self.bytecodes = {}

        self.truffle_runner_factory = truffle_runner_factory
        self.mutators = mutators
        self.mutators.append(SolidityMutator())

        for network in networks:
            self.networks_queue.put(network)

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
        if self.networks:
            network = self.networks_queue.get()
        try:
            test_result = tr.run_tests(network=network)
        finally:
            if self.networks:
                self.networks_queue.put(network)

        self.base_run_time = time() - begin
        if test_result is None:
            return False

        return True

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
        network = None
        if self.networks:
            network = self.networks_queue.get()
        try:
            try:
                test_result = tr.run_tests(
                    mutation=mutation,
                    timeout=int(self.base_run_time) * 2,
                    network=network,
                    original_bytecode=self.bytecodes
                )
                if any(map(lambda t: not t.success, test_result.values())):
                    mutation.result = MutationResult.KILLED
            except EquivalentMutant:
                mutation.result = MutationResult.EQUIVALENT
        except TimedOut:
            mutation.result = MutationResult.TIMEDOUT
        except TestRunException as e:
            logging.warning(str(e))
            mutation.result = MutationResult.ERROR
        finally:
            if self.networks:
                self.networks_queue.put(network)
            done_callback()
            return

    def store_compilation_results(self):
        """ Stores compilation results for trivial compiler equivalence"""
        self.bytecodes = self.truffle_compiler.get_bytecodes(working_directory=str(self.project_directory))
