from eth_vertigo.core import Mutation, TestSuggester

from typing import List, Tuple
from eth_vertigo.incremental.store import IncrementalMutationStore, MutationRecord


class IncrementalSuggester(TestSuggester):
    def __init__(self, store: IncrementalMutationStore):
        self._store = store

    @property
    def is_strict(self) -> bool:
        return False

    def suggest_tests(self, mutation: Mutation) -> List:
        same_file = lambda record: record.source_file_name == mutation.source_file_name
        same_original = lambda record: record.original_text == mutation.original_value
        same_new = lambda record: record.new_text == mutation.value
        same_line = lambda record: record.line_number == mutation.line_number

        relevant_records = filter(same_file,
                                  filter(same_original,
                                         filter(same_new,
                                                filter(same_line, self._store.known_mutations))))
        tests = []
        for r in relevant_records:
            tests.extend(r.crime_scenes)
        return list(set(tests))


