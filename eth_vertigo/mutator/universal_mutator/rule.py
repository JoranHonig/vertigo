from pathlib import Path
from typing import Generator
from eth_vertigo.core import Mutation
from eth_vertigo.mutator.source_file import SourceFile
from re import finditer


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

    def generate_mutants(self, source: SourceFile, project_directory: Path) -> Generator[Mutation, None, None]:
        if self.replace in ("DO_NOT_MUTATE", ):
            return

        file = source.file
        file_content = file.read_text(encoding="utf-8")

        for occurrence in finditer(self.match, file_content):
            start = occurrence.start()
            end = occurrence.end() - 1
            size = end - start
            yield Mutation((start, size, 0), source, self.replace, project_directory)
