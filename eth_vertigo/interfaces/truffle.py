from eth_vertigo.test_runner.truffle.truffle_tester import TruffleTester
from eth_vertigo.core.truffle.truffle_compiler import TruffleCompiler

from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut
from eth_vertigo.test_runner import TestResult
from json import loads, JSONDecodeError
from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile
from pathlib import Path
from typing import Dict, Union
from loguru import logger
import json
import re

swarm_hash_regex = re.compile("((a165)(.*)(5820)[a-f0-9]{64}(0029))$")


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
            print("Test output:")
            print(output.decode('utf-8'))
            raise TestRunException("\n".join(errors))
        try:
            return self._normalize_mocha(loads(test_result))
        except JSONDecodeError:
            print("Test output:")
            print(output.decode('utf-8'))
            raise TestRunException("Encountered error during test output analysis")

    def check_bytecodes(self, working_directory: str, original_bytecode: Dict[str, str]) -> bool:
        """ Returns whether none of the bytecodes differ from the original bytecodes

        :param working_directory: The truffle directory for which we should check the bytecodes
        :param original_bytecode: The original bytecodes {'contractName': '0x00'}
        :return: Whether the bytecodes match up
        """
        current_bytecodes = self.get_bytecodes(working_directory)
        for contractName, bytecode in current_bytecodes.items():
            if original_bytecode[contractName] != bytecode:
                return False
        return True

    def get_bytecodes(self, working_directory: str) -> Dict[str, str]:
        """ Returns the bytecodes in the compilation result of the current directory

        :param working_directory: The truffle directory for which we retreive the bytecodes
        :return: bytecodes in the shape {'contractName': '0x00'}
        """
        w_dir = Path(working_directory)
        self.run_compile_command(working_directory)
        if not (w_dir / "build").is_dir():
            logger.error("Compilation did not create build directory")

        contracts_dir = w_dir / "build" / "contracts"
        if not contracts_dir.is_dir():
            logger.error("No contracts directory found in build directory")

        current_bytecode = {}

        for contract in contracts_dir.iterdir():
            try:
                contract_compilation_result = json.loads(contract.read_text('utf-8'))
            except json.JSONDecodeError:
                logger.warning(f"Could not read compilation result for {contract.name}")
                continue

            current_bytecode[contract_compilation_result["contractName"]] = \
                self._strip_metadata(contract_compilation_result["bytecode"])
        return current_bytecode

    @staticmethod
    def _strip_metadata(bytecode: str) -> str:
        return swarm_hash_regex.sub("", bytecode)

    @staticmethod
    def _normalize_mocha(mocha_json: dict) -> Dict[str, TestResult]:
        tests = {}
        for failure in mocha_json["failures"]:
            tests[failure["fullTitle"]] = TestResult(failure["title"], failure["fullTitle"], failure["duration"], False)
        for success in mocha_json["passes"]:
            tests[success["fullTitle"]] = TestResult(success["title"], success["fullTitle"], success["duration"], True)
        return tests
