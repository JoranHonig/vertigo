from eth_vertigo.mutator.source_file import SourceFile
from pathlib import Path


class Mutator:
    """ Mutator

    A mutator implements the logic to generate mutants
    """
    def mutate(self, source_file: SourceFile, project_directory: Path):
        raise NotImplementedError
