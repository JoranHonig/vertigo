from eth_vertigo.test_runner.test_result import TestResult
from typing import Dict, Union


class TruffleTester:
    """Truffle tester interface exposes testing functionality from truffle"""
    def run_test_command(self, working_directory: str, file_name: str = None, network_name: str = None, timeout=None) \
            -> Union[None, Dict[str, TestResult]]:
        """ Runs truffle's test command

        :param working_directory: The directory which will be tested
        :param file_name: Filename of the test that should be executed
        :param network_name: Name of the network to execute the tests on
        :param timeout: The maximum duration that the tests are allowed to take
        :return: The test results
        """
        raise NotImplementedError

    def check_bytecodes(self, working_directory:str, original_bytecode: Dict[str, str]) -> bool:
        """ Returns whether any of the bytecodes differ from the original bytecodes

        :param working_directory: The truffle directory for which we should check the bytecodes
        :param original_bytecode: The original bytecodes {'contractName': '0x00'}
        :return: Whether the bytecodes match up
        """
        raise NotImplementedError
