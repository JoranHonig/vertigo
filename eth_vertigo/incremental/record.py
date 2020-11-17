from typing import List

from eth_vertigo.incremental.store import MutationRecord, IncrementalMutationStore
from eth_vertigo.core import Mutation


class IncrementalRecorder:
    def record(self, mutations: List[Mutation]) -> IncrementalMutationStore:
        store = IncrementalMutationStore()
        store.known_mutations = list(
            map(
                self._mutation_to_record,
                [m for m in mutations if m.crime_scenes]
            )
        )
        return store

    @staticmethod
    def _mutation_to_record(mutation: Mutation) -> MutationRecord:
        result = MutationRecord()
        result.new_text = mutation.value
        result.original_text = mutation.original_value
        result.source_file_name = mutation.source_file_name
        result.location = ":".join(map(str, mutation.location))
        result.line_number = mutation.line_number
        result.crime_scenes = mutation.crime_scenes
        return result
