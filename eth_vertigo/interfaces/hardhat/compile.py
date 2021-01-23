from eth_vertigo.interfaces.hardhat.core import HardhatCore
from eth_vertigo.interfaces.common import strip_metadata
from eth_vertigo.interfaces.generics import Compiler
from typing import Dict

from subprocess import Popen, TimeoutExpired
from tempfile import TemporaryFile
from pathlib import Path

from loguru import logger
import json


class HardhatCompiler(Compiler, HardhatCore):
    def run_compilation(self, working_directory: str) -> None:
        with TemporaryFile() as stdin, TemporaryFile() as stdout,  TemporaryFile() as stderr:
            stdin.seek(0)
            proc = Popen(
                self.hardhat_command + ['compile'],
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
        w_dir = Path(working_directory)
        self.run_compilation(working_directory)

        if not (w_dir / "artifacts").is_dir():
            logger.error("Compilation did not create build directory")

        contracts_dir = w_dir / "artifacts" / "contracts"
        if not contracts_dir.is_dir():
            logger.error("No contracts directory found in build directory")

        contract_directories = []

        def explore_contracts(directory: Path):
            for item in directory.iterdir():
                if item.name.endswith(".sol"):
                    contract_directories.append(item)
                elif item.is_dir():
                    explore_contracts(item)

        explore_contracts(contracts_dir)

        current_bytecode = {}

        for contract_dir in contract_directories:
            for contract in [c for c in contract_dir.iterdir() if "dbg.json" not in c.name]:
                try:
                    contract_compilation_result = json.loads(contract.read_text('utf-8'))
                except json.JSONDecodeError:
                    logger.warning(f"Could not read compilation result for {contract.name}")
                    continue

                current_bytecode[contract_compilation_result["contractName"]] = \
                    strip_metadata(contract_compilation_result["bytecode"])

        return current_bytecode
