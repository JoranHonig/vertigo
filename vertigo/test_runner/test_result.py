class TestResult:
    def __init__(self, title: str, full_title: str, duration: int, success: bool):
        """ Initialize test result object

        :param title: Title of the test
        :param full_title: Full title of the test
        :param duration: Duration of the test
        :param success: Whether the test has succeeded
        """
        self.title = title
        self.full_title = full_title
        self.duration = duration
        self.success = success
