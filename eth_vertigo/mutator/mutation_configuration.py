from enum import Enum


class MutationStrategy(Enum):
    """
    Mutation strategy enum that signifies the different strategies that are available
    """
    BoundaryConditionals = 1
    NegatedConditionals = 2
    MathOperations = 3
    MutateIncrements = 4
    MutateVoidCalls = 5


class MutationConfiguration:
    """This class is used to convey information to the Mutator instances

    Selecting core profiles:
    This configuration object lets you configure a Mutator instance to only execute specific mutations strategies
    and leave others
    """

    def __init__(self, enabled_strategies=None):
        """ Initialize core configuration object

        :param enabled_strategies:
        """
        self.enabled_strategies = enabled_strategies or []

    @property
    def all_enabled(self):
        """ Returns whether all strategies are enabled at this moment"""
        return len(self.enabled_strategies) in (0, 5)

    def is_enabled(self, strategy: MutationStrategy):
        """ Returns whether the given strategy is enabled in this configuration"""
        return strategy in self.enabled_strategies
