from eth_vertigo.mutator.source_file import SourceFile
from pathlib import Path
from eth_vertigo.mutator.mutator import Mutator


class SourceMutator(Mutator):
    def mutate(self, source_file: SourceFile, project_directory: Path):
        if not source_file.file.exists():
            return []

        result = []

        result += list(self.mutate_boundary_conditionals(source_file, project_directory))
        result += list(self.mutate_negated_conditionals(source_file, project_directory))
        result += list(self.mutate_math_ops(source_file, project_directory))
        result += list(self.mutate_increments(source_file, project_directory))
        result += list(self.mutate_voids(source_file, project_directory))
        result += list(self.mutate_modifier(source_file, project_directory))

        return result

    @staticmethod
    def mutate_boundary_conditionals(source_file: SourceFile, project_directory: Path):
        raise NotImplementedError

    @staticmethod
    def mutate_negated_conditionals(source_file: SourceFile, project_directory: Path):
        raise NotImplementedError

    @staticmethod
    def mutate_math_ops(source_file: SourceFile, project_directory: Path):
        raise NotImplementedError

    @staticmethod
    def mutate_increments(source_file: SourceFile, project_directory: Path):
        raise NotImplementedError

    @staticmethod
    def mutate_voids(source_file: SourceFile, project_directory: Path):
        raise NotImplementedError

    @staticmethod
    def mutate_modifier(source_file: SourceFile, project_directory: Path):
        raise NotImplementedError
