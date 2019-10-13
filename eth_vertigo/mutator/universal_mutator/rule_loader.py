from eth_vertigo.mutator.universal_mutator.rule import Rule
from pathlib import Path
from typing import Generator


class RuleLoader:
    """ RuleLoader

    This class implements the logic to load universal mutator style mutation rules
    """

    def load_from_file(self, file: Path) -> Generator[Rule]:
        """Load mutation rules from file"""
        file_contents = file.read_text(encoding='utf-8')
        return self.load_from_txt(file_contents)

    def load_from_txt(self, rule_txt: str) -> Generator[Rule]:
        """Load mutation rules from text"""
        pass
