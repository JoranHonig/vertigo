from pathlib import Path
from typing import Generator
from eth_vertigo.core import Mutation


class Rule:
    """ Rule

    This class represents a single universal mutator style mutation rule.

    Additionally the class provides logic to apply the rule to smart contracts.
    """

    def __init__(self, match, replace: str):
        """ Instantiate a new Rule

        :param match: The regex expression that specifies which parts of a program to replace
        :param replace: The string with which to replace the matches
        """
        self.match = match
        self.replace = replace

    def generate_mutants(self, file: Path) -> Generator[Mutation]:
        pass
