from eth_vertigo.core import Mutation, TestSuggester

from typing import List, Tuple
from eth_vertigo.incremental.store import IncrementalMutationStore, MutationRecord


class IncrementalSuggester(TestSuggester):
    def __init__(self, store: IncrementalMutationStore):
        self._store = store

    @property
    def is_strict(self) -> bool:
        return False

    def _equivalent(self, mutation: Mutation, record: MutationRecord):
        return record.source_file_name == mutation.source_file_name \
               and record.original_text == mutation.original_value \
               and record.new_text == mutation.value \
               and record.line_number == mutation.line_number

    def suggest_tests(self, mutation: Mutation) -> List:
        records = self._store.known_mutations
        relevant_records = [r for r in records if self._equivalent(mutation, r)]
        tests = []
        for r in relevant_records:
            tests.extend(r.crime_scenes)
        return list(set(tests))


