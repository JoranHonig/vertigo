from typing import List
from eth_vertigo.core.mutation import Mutation
from eth_vertigo.core.filter import MutationFilter
from random import sample


class ExcludeFilter(MutationFilter):
    """ A exclusion filter to ignore files from specific directories """

    def __init__(self, prefixes: List[str]):
        """ Creates an exclusion filter """
        self.prefixes = prefixes
        super().__init__()

    def apply(self, mutations: List[Mutation]) -> List[Mutation]:
        """ Apply this filter to a list of mutations

        :param mutations: The mutations to filter
        :return: The resulting list
        """

        def should_not_filter(mutation):
            for prefix in self.prefixes:
                if str(mutation.relative_path).startswith(prefix) or str(mutation.relative_path).startswith("/" + prefix):
                    return False
            return True

        return list(filter(should_not_filter, mutations))
