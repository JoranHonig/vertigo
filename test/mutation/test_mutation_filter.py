from eth_vertigo.core.filter import MutationFilter
import pytest


def test_mutation_filter_interface():
    # Arrange
    filter = MutationFilter()

    # Act
    with pytest.raises(NotImplementedError):
        filter.apply(None)
