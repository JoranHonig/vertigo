import yaml
from typing import List, Dict
from pathlib import Path


class IncrementalMutationStore:
    def __init__(self):
        self.known_mutations = []  # type: List[MutationRecord]

    @property
    def yaml(self):
        return yaml.dump({"known_mutations": [m.as_dict for m in self.known_mutations]})

    @staticmethod
    def from_yaml(data):
        values = yaml.safe_load(data)
        result = IncrementalMutationStore()
        result.known_mutations = [MutationRecord.from_dict(record) for record in values.get("known_mutations", [])]
        return result

    @staticmethod
    def from_file(file: Path):
        if not file.is_file():
            raise ValueError("Passed path is not a file")

        content = file.read_text('utf-8')
        return IncrementalMutationStore.from_yaml(content)

    def to_file(self, file: Path):
        if file.exists() and not file.is_file():
            raise ValueError("Passed path already exists and is not a file")

        file.write_text(self.yaml, "utf-8")


class MutationRecord:
    def __init__(self):
        self.location = None
        self.original_text = None
        self.line_number = None
        self.source_file_name = None
        self.new_text = None
        self.crime_scenes = []  # type: List[str]

    @staticmethod
    def from_dict(data: Dict):
        result = MutationRecord()
        result.location = data.get("location", "")
        result.original_text = data.get("original_text", "")
        result.line_number = data.get("line_number", "")
        result.source_file_name = data.get("source_file_name", "")
        result.new_text = data.get("new_text", "")
        result.crime_scenes = data.get("crime_scenes", [])
        return result

    @property
    def as_dict(self):
        return self.__dict__

