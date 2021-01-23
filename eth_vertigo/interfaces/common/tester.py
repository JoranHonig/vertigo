from abc import ABC, abstractmethod

from pathlib import Path
from tempfile import mkdtemp
from distutils.dir_util import copy_tree
import shutil

from eth_vertigo.core import Mutation
from eth_vertigo.test_runner.file_editor import FileEditor
from eth_vertigo.interfaces.generics import Tester
from json import loads, JSONDecodeError
from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile
from typing import Dict, Union
from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut
from eth_vertigo.test_runner import TestResult

from eth_vertigo.test_runner.exceptions import EquivalentMutant

from typing import List, Dict, Union


def normalize_mocha(mocha_json: dict) -> Dict[str, TestResult]:
    tests = {}
    for failure in mocha_json["failures"]:
        tests[failure["fullTitle"]] = TestResult(failure["title"], failure["fullTitle"], failure["duration"], False)
    for success in mocha_json["passes"]:
        tests[success["fullTitle"]] = TestResult(success["title"], success["fullTitle"], success["duration"], True)
    return tests


def make_temp_directory(original_dir: str):
    td = mkdtemp()
    copy_tree(original_dir, td, preserve_symlinks=1)
    return td


def clean_build_directory(project_path: str, build_directory: str = "build"):
    build_dir = Path(project_path) / build_directory
    if build_dir.is_dir():
        shutil.rmtree(build_dir)


def rm_temp_directory(temp_dir: str):
    shutil.rmtree(temp_dir)


def apply_mutation(mutation: Mutation, working_directory):
    target_file_name = working_directory + '/' + mutation.relative_path
    FileEditor.edit(target_file_name, mutation.location, mutation.value)


class MochaStdoutTester(Tester):
    def run_tests(
            self,
            coverage: bool = False,
            mutation: Mutation = None,
            timeout=None,
            network: str = None,
            original_bytecode: Dict[str, str] = None,
            keep_test_names: List[str] = None,
    ) -> dict:
        """
        Runs all the tests in the truffle project in a clean environment
        :param coverage: Whether to run the tests with coverage
        :param mutation: List indicating edits that need to be performed on mutator files
        :param timeout: Maximum duration that the test is allowed to take
        :param network: Name of the network that the test should be using
        :param original_bytecode: A dict of the original bytecodes (before mutation)
        :param keep_test_names: Only execute the tests in this list
        :return: Test results
        """
        if coverage:
            raise NotImplementedError

        temp_dir = make_temp_directory(self.project_directory)
        clean_build_directory(temp_dir)

        self.instrument_configuration(temp_dir, keep_test_names)

        if mutation:
            apply_mutation(mutation, temp_dir)
        try:
            if original_bytecode is not None and original_bytecode != {}:
                if self.compiler.check_bytecodes(temp_dir, original_bytecode):
                    raise EquivalentMutant
            test_command = self.build_test_command(network)
            result = self.run_test_command(test_command, temp_dir, timeout=timeout)
        finally:
            rm_temp_directory(temp_dir)

        return result

    @abstractmethod
    def instrument_configuration(self, directory, keep_test_names):
        pass

    @abstractmethod
    def build_test_command(self, network: str):
        pass

    @staticmethod
    def run_test_command(
            command: str,
            working_directory: str,
            timeout=None
    ) -> Union[Dict[str, TestResult], None]:
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