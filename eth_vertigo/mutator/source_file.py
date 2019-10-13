from pathlib import Path
from typing import Tuple


class SourceFile:
    """ SourceFile objects represent contract files

    Specifically it stores information on the file it represents and it exposes functions that
    allow other components to find specific interesting locations in the mutator file.
    This is mostly used by the different Mutator implementations
    """

    def __init__(self, file: Path):
        self.file = file

    def get_binary_op_locations(self) -> Tuple[str, Tuple[int, int, int]]:
        """Gets locations for all the binary operations in the sourcefile
        :returns tuple with (original_operation, src)
        """
        raise NotImplementedError

    def get_if_statement_binary_ops(self) -> Tuple[str, Tuple[int, int, int]]:
        """Gets locations for all the binary operations in the sourcefile

        Specifically those supplied as an argument to an if statement
        :returns tuple with (original_operation, src)
        """
        raise NotImplementedError

    def get_assignments(self) -> Tuple[str, Tuple[int, int, int]]:
        """Gets locations for all the assignments in the sourcefile
        :returns tuple with (original_operation, src)
        """
        raise NotImplementedError

    def get_void_calls(self) -> Tuple[str, Tuple[int, int, int]]:
        """Gets locations for all the void calls in the sourcefile
        :returns tuple with (original_operation, src)
        """
        raise NotImplementedError
