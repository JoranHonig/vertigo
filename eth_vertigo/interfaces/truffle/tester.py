from json import loads, JSONDecodeError
from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile
from typing import Dict, Union

from eth_vertigo.interfaces.generics import Tester
from eth_vertigo.interfaces.truffle.core import TruffleCore
from eth_vertigo.interfaces.common import normalize_mocha

from eth_vertigo.test_runner import TestResult
from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut

from eth_vertigo.test_runner import Runner
from eth_vertigo.test_runner.file_editor import FileEditor
from eth_vertigo.interfaces.generics import Compiler
from eth_vertigo.test_runner.exceptions import EquivalentMutant
from eth_vertigo.core import Mutation
from typing import Generator, List

from pathlib import Path
from tempfile import mkdtemp
from distutils.dir_util import copy_tree
import shutil
from typing import Dict


def _make_temp_truffle_directory(original_dir: str):
    td = mkdtemp()
    copy_tree(original_dir, td, preserve_symlinks=1)
    return td


def _clean_build_directory(project_path: str):
    build_dir = Path(project_path) / "build"
    if build_dir.is_dir():
        shutil.rmtree(build_dir)


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


def _rm_temp_truffle_directory(temp_dir: str):
    shutil.rmtree(temp_dir)


def _apply_mutation(mutation: Mutation, working_directory):
    target_file_name = working_directory + '/' + mutation.relative_path
    FileEditor.edit(target_file_name, mutation.location, mutation.value)


class TruffleTester(TruffleCore, Tester):
    def __init__(self, truffle_location, project_directory, compiler: Compiler):
        self.project_directory = project_directory
        self.compiler = compiler
        TruffleCore.__init__(self, truffle_location)

    def run_tests(
            self,
            coverage: bool = False,
            mutation: Mutation = None,
            timeout=None,
            network: str = None,
            original_bytecode: Dict[str, str] = None,
            suggestions: List[str] = None,
    ) -> dict:
        """
        Runs all the tests in the truffle project in a clean environment
        :param coverage: Whether to run the tests with coverage
        :param mutation: List indicating edits that need to be performed on mutator files
        :param timeout: Maximum duration that the test is allowed to take
        :param network: Name of the network that the test should be using
        :param original_bytecode: A dict of the original bytecodes (before mutation)
        :param suggestions: a list of tests to try first, before commencing analysis with the entire test suite
        :return: Test results
        """
        if coverage:
            raise NotImplementedError

        temp_dir = _make_temp_truffle_directory(self.project_directory)
        _clean_build_directory(temp_dir)
        _set_reporter(temp_dir)
        if suggestions:
            _set_include_tests(temp_dir, suggestions)

        if mutation:
            _apply_mutation(mutation, temp_dir)
        try:
            if original_bytecode is not None and original_bytecode != {}:
                if self.compiler.check_bytecodes(temp_dir, original_bytecode):
                    raise EquivalentMutant
            result = self._run_test_command(temp_dir, network_name=network, timeout=timeout)
        finally:
            _rm_temp_truffle_directory(temp_dir)

        return result

    def _run_test_command(self, working_directory: str, network_name: str = None, timeout=None) -> Union[Dict[str, TestResult], None]:
        command = [
            self.truffle_location, 'test'
        ]

        if network_name:
            command += ['--network', network_name]

        with TemporaryFile() as stdin, TemporaryFile() as stdout:
            stdin.seek(0)
            proc = Popen(command, stdin=stdin, stdout=stdout, stderr=stdout, cwd=working_directory)
            try:
                proc.wait(timeout=timeout)
            except TimeoutExpired:
                proc.kill()
                raise TimedOut

            stdout.seek(0)
            output = stdout.read()

        split = output.decode('utf-8').split("\n")
        errors = []
        test_result = []
        preamble = True
        for line in split:
            if line.startswith("Error"):
                errors.append(line)
            if line.startswith("{"):
                preamble = False
            if preamble:
                continue
            test_result.append(line)

        test_result = "\n".join(test_result)

        if errors:
            raise TestRunException("\n".join(errors))
        try:
            return normalize_mocha(loads(test_result))
        except JSONDecodeError:
            raise TestRunException("Encountered error during test output analysis")


