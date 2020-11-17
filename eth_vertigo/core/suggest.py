from abc import ABC, abstractmethod
from typing import Tuple, List
from eth_vertigo.core.mutation import Mutation


class TestSuggester(ABC):
    """ TestSuggester interface definition

    A TestSuggester is used to provide suggestions for which tests to run to the mutation testing campaign.
    """

    @property
    @abstractmethod
    def is_strict(self) -> bool:
        """ Returns whether this suggester provides strict suggestions

        A strict suggestion is one where only the suggested tests should be ran.

        A non-strict suggestions is one where the suggested tests should be ran first, before executing
        the remainder of the test suite.
        """
        pass

    @abstractmethod
    def suggest_tests(self, mutation: Mutation) -> List:
        """ Request list of test from the suggester as to which tests should be ran on the mutation

        :param mutation: The subject mutation

        :return List of tests to run
        """
        pass
