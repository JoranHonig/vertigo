from pathlib import Path
from eth_vertigo.mutator.source_file import SourceFile
from typing import Tuple
from enum import Enum
from jinja2 import PackageLoader, Environment

environment = Environment(
        loader=PackageLoader("eth_vertigo.core"), trim_blocks=True
    )

class MutationResult(Enum):
    KILLED = 1
    LIVED = 2
    TIMEDOUT = 3
    ERROR = 4
    EQUIVALENT = 5


_mutationresult_string = {
    MutationResult.KILLED: "Killed",
    MutationResult.LIVED: "Lived",
    MutationResult.TIMEDOUT: "Timeout",
    MutationResult.ERROR: "Error",
    MutationResult.EQUIVALENT: "Equivalent",
    None: "None"
}


class Mutation:
    """
    A core class contains specific information on a single core
    """

    def __init__(
            self,
            location: Tuple[int, int, int],
            source: SourceFile,
            value: str,
            project_directory: Path
    ):
        """
        Initializes a core
        :param location: Location of the core, in the src format (offset, length, file_index)
        :param source: Source file for which the core is to be applied
        :param value: New value that the location should take on
        :param project_directory: Project directory Path of the project directory that eth_vertigo is working in
        """
        self.location = location
        self.source = source
        self.project_directory = project_directory
        self.value = value

        # The following parameters are used to track how and when this core was killed
        self.result = None
        self.crime_scenes = []

    @property
    def relative_path(self):
        """ Gets the relative path of the mutator wrt the project directory """
        r_path = self.source.file.relative_to(self.project_directory)
        return str(r_path)

    @staticmethod
    def _get_mutated_line(offset, text):
        cursor = 0
        for i, line in enumerate(text.splitlines(keepends=True)):
            if len(line) + cursor > offset:
                return i, line.replace("\t", "")
            cursor += len(line)

    @property
    def source_file_name(self):
        return self.source.file.name

    @property
    def original_value(self):
        source_content = self.source.file.read_text('utf-8')
        return source_content[self.location[0]: self.location[0] + self.location[1]]

    @property
    def line_number(self):
        source_content = self.source.file.read_text('utf-8')
        line_nr, _ = self._get_mutated_line(self.location[0], source_content)
        return line_nr

    def __repr__(self) -> str:
        """ Prints information that can be used to triage a core """
        template = environment.get_template("mutation_template.jinja2")
        source_content = self.source.file.read_text('utf-8')
        line_nr, og_line = self._get_mutated_line(self.location[0], source_content)

        mutated = source_content[:self.location[0]] \
                  + self.value + \
                  source_content[self.location[0] + self.location[1]:]

        _, mut_line = self._get_mutated_line(self.location[0], mutated)

        return template.render(
            file_name=str(self.source.file),
            line_number=line_nr,
            original_line=og_line,
            mutated_line=mut_line,
            result=_mutationresult_string[self.result]
        )
