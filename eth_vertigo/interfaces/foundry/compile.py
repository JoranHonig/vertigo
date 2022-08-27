from eth_vertigo.interfaces.foundry.core import FoundryCore
from eth_vertigo.interfaces.common import strip_metadata
from eth_vertigo.interfaces.generics import Compiler
from typing import Dict

from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile
from pathlib import Path

from loguru import logger
import json

class FoundryCompiler(Compiler, FoundryCore):
    def run_compilation(self, working_directory: str) -> None:
        with TemporaryFile() as stdin, TemporaryFile() as stdout, TemporaryFile() as stderr:
            stdin.seek(0)
            proc = Popen(
                self.foundry_command + ['build'],
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                cwd=working_directory
            )
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
        contracts_dir = w_dir / "out"

        if not (contracts_dir).is_dir():
            logger.error("Compilation did not create out directory")

        current_bytecode = {}

        for contract in contracts_dir.iterdir():
            if not contract.name.endswith(".t.sol") and not contract.name.endswith(".s.sol"):
                try:
                    contract = contract/ (contract.stem+".json")
                    contract_compilation_result = json.loads(contract.read_text('utf-8'))
                except json.JSONDecodeError:
                    logger.warning(f"Could not read compilation result for {contract.name}")
                    continue
                
                current_bytecode[contract.stem] = strip_metadata(contract_compilation_result["bytecode"]["object"])

        return current_bytecode

