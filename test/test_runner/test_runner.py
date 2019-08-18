from eth_vertigo.test_runner.runner import Runner
import pytest

# This test is only here for coverage


def test_abstract_methods():
    # Arrange
    runner = Runner()

    # Act and Assert
    with pytest.raises(NotImplementedError):
        runner.run_test(None, None)

    with pytest.raises(NotImplementedError):
        runner.run_tests(None)

    with pytest.raises(NotImplementedError):
        _ = runner.tests
