from eth_vertigo.interfaces.truffle.tester import TruffleTester
import pytest


def test_run_test_command():
    # Arrange
    tester = TruffleTester()

    # Act and Assert
    with pytest.raises(NotImplementedError):
        tester._run_test_command(
            working_directory="/",
            network_name=None,
            timeout=10
        )
