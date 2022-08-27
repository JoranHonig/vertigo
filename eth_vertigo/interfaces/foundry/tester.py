from pathlib import Path
from typing import List, Optional

from eth_vertigo.interfaces.common.tester import MochaStdoutTester
from eth_vertigo.interfaces.generics import Compiler
from eth_vertigo.interfaces.foundry.core import FoundryCore


def _set_reporter(directory: str):
    pass


def _set_include_tests(directory: str, test_names: List[str]):
    pass


class FoundryTester(FoundryCore, MochaStdoutTester):
    def __init__(self, foundry_location, project_directory, compiler: Compiler):
        self.project_directory = project_directory
        self.compiler = compiler
        self.foundry_location = foundry_location
        FoundryCore.__init__(self, foundry_location)

    def instrument_configuration(self, working_directory, keep_test_names: Optional[List[str]]):
        _set_reporter(working_directory)
        if keep_test_names:
            _set_include_tests(working_directory, keep_test_names)

    def build_test_command(self, network: Optional[str]) -> List[str]:
        result = self.foundry_location + ['test','-j']
        if network:
            result.extend(['--fork-url', network])
        return result