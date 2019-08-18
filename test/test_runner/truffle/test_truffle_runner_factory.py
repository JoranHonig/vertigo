from eth_vertigo.test_runner.truffle.truffle_runner_factory import TruffleRunnerFactory, TruffleRunner
from unittest.mock import MagicMock


def test_init():
    # Arrange
    truffle_tester = MagicMock()

    # Act
    factory = TruffleRunnerFactory(truffle_tester)

    # Assert
    assert truffle_tester == factory.truffle_tester


def test_create():
    # Arrange
    truffle_tester = MagicMock()
    factory = TruffleRunnerFactory(truffle_tester)

    # Act
    truffle_runner = factory.create("project_dir")

    # Assert
    assert isinstance(truffle_runner, TruffleRunner)
    assert truffle_tester == truffle_runner.truffle_tester
    assert "project_dir" == truffle_runner.project_directory
