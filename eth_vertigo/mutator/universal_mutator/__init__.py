from pathlib import Path
from typing import List

from eth_vertigo.mutator.universal_mutator.rule import Rule
from eth_vertigo.mutator.universal_mutator.rule_loader import RuleLoader
from eth_vertigo.mutator.mutator import Mutator
from eth_vertigo.mutator.source_file import SourceFile
from eth_vertigo.core.mutation import Mutation


class UniversalMutator(Mutator):
    """Mutator  based on Universal Mutator

    Props to the design of universal mutator style mutation rules and evaluation of the approach go to Alex Groce et al.
    Repository:
        https://github.com/agroce/universalmutator
    Paper:
        An Extensible, Regular-Expression-Based Tool for Multi-Language Mutant Generation - Alex Groce et al.
    """

    def __init__(self):
        self.rule_sets = {}

    def load_rule(self, rule_file: Path):
        """Load rule from rule files"""
        loader = RuleLoader()
        rules = list(loader.load_from_file(rule_file))
        self.rule_sets[str(rule_file.name)] = rules

    def mutate(self, source_file: SourceFile, project_directory: Path) -> List[Mutation]:
        """Generate mutants

        Generates mutants based on loaded universal mutator rules
        """
        mutants = []
        for rule_file, rules in self.rule_sets.items():
            for rule in rules:
                mutants.extend(list(rule.generate_mutants(source_file, project_directory)))
        return mutants
