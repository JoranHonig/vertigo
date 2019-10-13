from eth_vertigo.mutator.solidity.solidity_file import SolidityFile
from eth_vertigo.mutator.source_mutator import SourceMutator
from eth_vertigo.core.mutation import Mutation
from pathlib import Path

conditional_boundary_mutator = {
    "==": " != ",
    "<": " <= ",
    "<=": " < ",
    ">": " >= "
}

conditional_negation_mutator = {
    "==": " != ",
    "!=": " == ",
    "<=": " > ",
    ">=": " < ",
    "<": " >= ",
    ">": " <= "
}

increments_mutator = {
    "+=": " -= ",
    "-=": " += "
}

math_mutants = {
    "+": " - ",
    "-": " + ",
    "*": " / ",
    "/": " * ",
    "&": " | ",
    "|": " & ",
    "^": " & ",
    "~": "",
    "<<": " >> ",
    ">>": " << "
}

mirror_mutants = {
    "-=": "=-",
    "+=": "=+"
}


def _mutate_binary_op(
    mutate_dict: dict, source_file: SolidityFile, project_directory: Path
):
    interesting_locs = source_file.get_binary_op_locations()

    for original_operator, src in interesting_locs:
        if original_operator not in mutate_dict.keys():
            continue
        yield Mutation(
            src, source_file, mutate_dict[original_operator], project_directory
        )


def _mutate_assignment(
    mutate_dict: dict, source_file: SolidityFile, project_directory: Path
):
    interesting_locs = source_file.get_assignments()

    for original_operator, src in interesting_locs:
        if original_operator not in mutate_dict.keys():
            continue
        yield Mutation(
            src, source_file, mutate_dict[original_operator], project_directory
        )


class SolidityMutator(SourceMutator):
    @staticmethod
    def mutate_boundary_conditionals(source_file: SolidityFile, project_directory: Path):
        return _mutate_binary_op(conditional_boundary_mutator, source_file, project_directory)

    @staticmethod
    def mutate_negated_conditionals(source_file: SolidityFile, project_directory: Path):
        return _mutate_binary_op(conditional_negation_mutator, source_file, project_directory)

    @staticmethod
    def mutate_math_ops(source_file: SolidityFile, project_directory: Path):
        return _mutate_binary_op(math_mutants, source_file, project_directory)

    @staticmethod
    def mutate_increments(source_file: SolidityFile, project_directory: Path):
        return _mutate_assignment(increments_mutator, source_file, project_directory)

    @staticmethod
    def mutate_mirror(source_file: SolidityFile, project_directory: Path):
        return _mutate_assignment(mirror_mutants, source_file, project_directory)

    @staticmethod
    def mutate_voids(source_file: SolidityFile, project_directory: Path):
        void_calls = list(source_file.get_void_calls())
        for _, src in void_calls:
            src[1] += 1
            yield Mutation(src, source_file, "", project_directory)

    @staticmethod
    def mutate_modifier(source_file: SolidityFile, project_directory: Path):
        modifier_invocations = list(source_file.get_modifier_invocations())
        for _, src in modifier_invocations:
            yield Mutation(src, source_file, "", project_directory)
