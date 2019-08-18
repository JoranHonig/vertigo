class TruffleCompiler:
    """Truffle compiler interface exposes compiling functionality from truffle"""
    def run_compile_command(self, working_directory: str) -> None:
        """ Runs truffle's test command

        :param working_directory: The truffle project directory to compile
        """
        raise NotImplementedError
