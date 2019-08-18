from eth_vertigo.test_runner.truffle.truffle_tester import TruffleTester
from eth_vertigo.test_runner.truffle.truffle_runner import TruffleRunner


class TruffleRunnerFactory:
    """ Factory for TestRunner objects """
    def __init__(self, truffle_tester: TruffleTester) -> None:
        """Initializes a truffle runner factory"""
        self.truffle_tester = truffle_tester

    def create(self, project_directory: str) -> TruffleRunner:
        """ Create a new TruffleRunner

        :param project_directory: Project directory that the test runner should be aimed at
        :return: the brand new truffle runner
        """
        return TruffleRunner(
            project_directory=project_directory,
            truffle_tester=self.truffle_tester
        )
