from typing import Dict


class TruffleCompiler:
    """Truffle compiler interface exposes compiling functionality from truffle"""
    def run_compile_command(self, working_directory: str) -> None:
        """ Runs truffle's test command

        :param working_directory: The truffle project directory to compile
        """
        raise NotImplementedError

    def get_bytecodes(self, working_directory: str) -> Dict[str, str]:
        """ Returns the bytecodes in the compilation result of the current directory

        :param working_directory: The truffle directory for which we retreive the bytecodes
        :return: bytecodes in the shape {'contractName': '0x00'}
        """
        raise NotImplementedError
