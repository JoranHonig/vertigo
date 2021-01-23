from typing import Dict, Union, List
from eth_vertigo.test_runner.test_result import TestResult
from abc import ABC, abstractmethod
from eth_vertigo.core import Mutation


class Compiler:
    """Compiler test framework interface"""
    def run_compilation(self, working_directory: str) -> None:
        """ Executes compilation

        :param working_directory: The project directory to compile
        """
        raise NotImplementedError

    def get_bytecodes(self, working_directory: str) -> Dict[str, str]:
        """ Returns the bytecodes in the compilation result of the current directory

        :param working_directory: The truffle directory for which we retrieve the bytecodes
        :return: bytecodes in the shape {'contractName': '0x00'}
        """
        raise NotImplementedError

    def check_bytecodes(self, working_directory: str, original_bytecode: Dict[str, str]) -> bool:
        """ Returns whether any of the bytecodes differ from the original bytecodes

        :param working_directory: The truffle directory for which we should check the bytecodes
        :param original_bytecode: The original bytecodes {'contractName': '0x00'}
        :return: Whether the bytecodes match up
        """
        current_bytecodes = self.get_bytecodes(working_directory)
        for contractName, bytecode in current_bytecodes.items():
            if original_bytecode[contractName] != bytecode:
                return False
        return True


class Tester(ABC):
    """Tester interface exposes testing functionality from testing frame work"""

    @abstractmethod
    def run_tests(
            self,
            coverage: bool = False,
            mutation: Mutation = None,
            timeout=None,
            network: str = None,
            original_bytecode: Dict[str, str] = None,
            keep_test_names: List[str] = None,
    ) -> Union[None, Dict[str, TestResult]]:
        pass

