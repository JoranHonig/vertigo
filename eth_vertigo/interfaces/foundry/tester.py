from abc import ABC
from eth_vertigo.interfaces.foundry.core import FoundryCore
from eth_vertigo.interfaces.common.tester import MochaStdoutTester
from eth_vertigo.interfaces.generics import Tester, Compiler

from typing import Optional, List
from pathlib import Path


def _set_reporter(directory: str):
    #config = Path(directory) / "hardhat.config.js"
    #content = config.read_text("utf-8")
    #content += "\nmodule.exports.mocha = {reporter: \"json\"};\n"
    #content += "\nmodule.exports.solc = {optimizer: { enabled: true, runs: 200 }};\n"
    #config.write_text(content, "utf-8")
    pass


def _set_include_tests(directory: str, test_names: List[str]):
    #config = Path(directory) / "hardhat.config.js"

    #content = config.read_text("utf-8")

    #test_regex = "({})".format("|".join(test_names))
    #content += "\nmodule.exports.mocha.grep= \"" + test_regex + "\";\n"
    #config.write_text(content, "utf-8")
    pass


class FoundryTester(FoundryCore, MochaStdoutTester):
    def __init__(self, foundry_command: List[str], project_directory, compiler: Compiler):
        self.project_directory = project_directory
        self.compiler = compiler
        FoundryCore.__init__(self, foundry_command)

    def instrument_configuration(self, directory, keep_test_names: Optional[List[str]]):
        _set_reporter(directory)
        if keep_test_names:
            _set_include_tests(self.directory, keep_test_names)

    def build_test_command(self, network: Optional[str]) -> List[str]:
        result = self.foundry_command + ['test', '--json']
        # if network:
        #     result.extend(['--network', network])
        return result
