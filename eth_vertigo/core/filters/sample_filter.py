from typing import List
from eth_vertigo.core.mutation import Mutation
from eth_vertigo.core.filter import MutationFilter
from random import sample


class SampleFilter(MutationFilter):
    """ A sample filter which takes a random subset of the mutations along a defined ratio"""

    def __init__(self, ratio: float = 0.1):
        """ Creates a sample filter

        :param ratio: ratio of mutations to select
        """
        self.ratio = ratio
        super().__init__()

    def apply(self, mutations: List[Mutation]) -> List[Mutation]:
        """ Apply this filter to a list of mutations

        :param mutations: The mutations to filter
        :return: The resulting list
        """
        return sample(mutations, int(self.ratio * len(mutations)))
