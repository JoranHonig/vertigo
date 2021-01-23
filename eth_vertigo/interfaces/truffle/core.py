class TruffleCore:
    """ Truffle interface object, deals with the ugly commandline details"""

    def __init__(self, truffle_location: str = "truffle") -> None:
        """ Initializes a new truffle object

        :param truffle_location: Location where the truffle cli can be found
        """
        self.truffle_location = truffle_location
