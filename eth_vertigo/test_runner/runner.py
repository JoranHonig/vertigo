class Runner:

    @property
    def tests(self) -> list:
        """ Returns a list of the tests """
        raise NotImplementedError

    def run_tests(self, coverage: bool):
        """ Runs all the tests that are available"""
        raise NotImplementedError

    def run_test(self, name: str, coverage: bool):
        """ Runs the test with the given name """
        raise NotImplementedError
