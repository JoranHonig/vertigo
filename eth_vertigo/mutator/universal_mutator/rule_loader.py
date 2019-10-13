from eth_vertigo.mutator.universal_mutator.rule import Rule
from pathlib import Path
from typing import Generator
from re import compile, error
from loguru import logger


class RuleLoader:
    """ RuleLoader

    This class implements the logic to load universal mutator style mutation rules
    """

    def load_from_file(self, file: Path) -> Generator[Rule, None, None]:
        """Load mutation rules from file"""
        file_contents = file.read_text(encoding='utf-8')
        return self.load_from_txt(file_contents)

    def load_from_txt(self, rule_txt: str) -> Generator[Rule, None, None]:
        """Load mutation rules from text"""
        for line in rule_txt.split("\n"):
            # Deal with non mutation rule lines
            if "==>" not in line:
                if line.startswith("#"):
                    continue
                if line == "":
                    continue
                logger.warning(f"Error while parsing Universal Mutator rules:\n{line}")
                continue

            split_line = line.split("==>")
            if len(line) < 2:
                logger.warning(f"Error while parsing Universal Mutator rules:\n{line}")
                continue

            match = split_line[0]
            replace = split_line[1]

            # compile regex
            try:
                match = compile(match)
            except error:
                logger.warning(f"Error while parsing Universal Mutator rules.\nInvalid regular expression:\n{line}")

            # drop return char if present
            if replace and replace[-1] == '\n':
                replace = replace[:-1]
                replace.strip(' ')
            yield Rule(match, replace)
