from eth_vertigo.test_runner.truffle.truffle_tester import TruffleTester
import pytest


def test_run_test_command():
    # Arrange
    tester = TruffleTester()

    # Act and Assert
    with pytest.raises(NotImplementedError):
        tester.run_test_command(
            working_directory="/",
            file_name=None,
            network_name=None,
            timeout=10
        )
