from eth_vertigo.test_runner.truffle.truffle_tester import TruffleTester
from eth_vertigo.mutation.truffle.truffle_compiler import TruffleCompiler

from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut
from eth_vertigo.test_runner import TestResult
from json import loads, JSONDecodeError
from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile

from typing import Dict, Union


class Truffle(TruffleTester, TruffleCompiler):
    """ Truffle interface object, deals with the ugly commandline details"""

    def __init__(self, truffle_location: str = "truffle") -> None:
        """ Initializes a new truffle object

        :param truffle_location: Location where the truffle cli can be found
        """
        self.truffle_location = truffle_location

    def run_compile_command(self, working_directory: str) -> None:
        command = [
            self.truffle_location, 'compile'
        ]

        with TemporaryFile() as stdin, TemporaryFile() as stdout:
            stdin.seek(0)
            proc = Popen(command, stdin=stdin, stdout=stdout, cwd=working_directory)
            proc.wait()
            stdout.seek(0)
            output = stdout.read()

        split = output.decode('utf-8').split("\n")

        errors = []
        for line in split:
            if line.startswith("Error"):
                errors.append(line)

        if errors:
            raise Exception("Encountered compilation error: \n" + "\n".join(errors))

    def run_test_command(self, working_directory: str, file_name: str = None, network_name: str = None, timeout=None) -> Union[Dict[str, TestResult], None]:
        command = [
            self.truffle_location, 'test'
        ]

        if file_name:
            command.append(file_name)
        if network_name:
            command += ['--network', network_name]

        with TemporaryFile() as stdin, TemporaryFile() as stdout:
            stdin.seek(0)
            proc = Popen(command, stdin=stdin, stdout=stdout, cwd=working_directory)
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
            return self._normalize_mocha(loads(test_result))
        except JSONDecodeError:
            raise TestRunException("Encountered error during test output analysis")

    @staticmethod
    def _normalize_mocha(mocha_json: dict) -> Dict[str, TestResult]:
        tests = {}
        for failure in mocha_json["failures"]:
            tests[failure["fullTitle"]] = TestResult(failure["title"], failure["fullTitle"], failure["duration"], False)
        for success in mocha_json["passes"]:
            tests[success["fullTitle"]] = TestResult(success["title"], success["fullTitle"], success["duration"], True)
        return tests
