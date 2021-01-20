from eth_vertigo.interfaces.generics import Compiler, Tester
from eth_vertigo.interfaces.truffle.core import TruffleCore
from eth_vertigo.interfaces.common import strip_metadata
from eth_vertigo.test_runner.exceptions import TestRunException, TimedOut
from eth_vertigo.test_runner import TestResult
from json import loads, JSONDecodeError
from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile
from pathlib import Path
from typing import Dict, Union
from loguru import logger
import json
import re


class TruffleCompiler(TruffleCore, Compiler):
    def run_compilation(self, working_directory: str) -> None:
        command = [
            self.truffle_location, 'compile'
        ]

        with TemporaryFile() as stdin, TemporaryFile() as stdout:
            stdin.seek(0)
            proc = Popen(command, stdin=stdin, stdout=stdout, cwd=working_directory)
            proc.wait()
            stdout.seek(0)
            output = stdout.read()

        split = output.decode('utf-8').split("\n")

        errors = []
        for line in split:
            if line.startswith("Error"):
                errors.append(line)

        if errors:
            raise Exception("Encountered compilation error: \n" + "\n".join(errors))

    def get_bytecodes(self, working_directory: str) -> Dict[str, str]:
        """ Returns the bytecodes in the compilation result of the current directory

        :param working_directory: The truffle directory for which we retreive the bytecodes
        :return: bytecodes in the shape {'contractName': '0x00'}
        """
        w_dir = Path(working_directory)
        self.run_compilation(working_directory)
        if not (w_dir / "build").is_dir():
            logger.error("Compilation did not create build directory")

        contracts_dir = w_dir / "build" / "contracts"
        if not contracts_dir.is_dir():
            logger.error("No contracts directory found in build directory")

        current_bytecode = {}

        for contract in contracts_dir.iterdir():
            try:
                contract_compilation_result = json.loads(contract.read_text('utf-8'))
            except json.JSONDecodeError:
                logger.warning(f"Could not read compilation result for {contract.name}")
                continue

            current_bytecode[contract_compilation_result["contractName"]] = \
                strip_metadata(contract_compilation_result["bytecode"])
        return current_bytecode

