import pytest

from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut, DidNotCompile


def test_exception():
    # Yet another coverage unit test
    with pytest.raises(TestRunException):
        raise TestRunException

    with pytest.raises(TimedOut):
        raise TimedOut

    with pytest.raises(DidNotCompile):
        raise DidNotCompile
