from pathlib import Path
from typing import List, Optional

from eth_vertigo.interfaces.common.tester import MochaStdoutTester
from eth_vertigo.interfaces.generics import Compiler
from eth_vertigo.interfaces.truffle.core import TruffleCore


def _set_reporter(directory: str):
    config = Path(directory) / "truffle.js"
    if not config.is_file():
        config = Path(directory) / "truffle-config.js"
    content = config.read_text("utf-8")
    content += "\nmodule.exports.mocha = {reporter: \"json\"};\n"
    content += "\nmodule.exports.solc = {optimizer: { enabled: true, runs: 200}};\n"
    config.write_text(content, "utf-8")


def _set_include_tests(directory: str, test_names: List[str]):
    config = Path(directory) / "truffle.js"
    if not config.is_file():
        config = Path(directory) / "truffle-config.js"

    content = config.read_text("utf-8")

    test_regex = "({})".format("|".join(test_names))
    content += "\nmodule.exports.mocha.grep= \"" + test_regex + "\";\n"
    config.write_text(content, "utf-8")


class TruffleTester(TruffleCore, MochaStdoutTester):
    def __init__(self, truffle_location, project_directory, compiler: Compiler):
        self.project_directory = project_directory
        self.compiler = compiler
        TruffleCore.__init__(self, truffle_location)

    def instrument_configuration(self, working_directory, keep_test_names: Optional[List[str]]):
        _set_reporter(working_directory)
        if keep_test_names:
            _set_include_tests(working_directory, keep_test_names)

    def build_test_command(self, network: Optional[str]) -> List[str]:
        result = [self.truffle_location, 'test']
        if network:
            result.extend(['--network', network])
        return result
