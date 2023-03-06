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
        with TemporaryFile() as stdin, TemporaryFile() as stdout,  TemporaryFile() as stderr:
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
        w_dir = Path(working_directory)
        self.run_compilation(working_directory)
        if not (w_dir / "out").is_dir():
            logger.error("Compilation did not create build directory")

        # Foundry doesn't separate "src" compiled outputs from the rest of the
        # test environment like truffle and hardhat do. We need to iterate on the 
        # src/ directory to get the names of the "actual"
        
        # TODO: someone might change the name `src` and break this tool, so we
        # should probably make this configurable
        contracts_dir = w_dir / "out"
        if not contracts_dir.is_dir():
            logger.error("No contracts directory found in src directory")

        contract_directories = []

        # directory is the out/ directory
        # src_files is the list of files in the src directory
        def explore_contracts(directory: Path):
            src_files = [f.name for f in (w_dir / "src").iterdir() if f.is_file()]
            for item in directory.iterdir():
                if item.name in src_files and item.name.endswith(".sol"):
                    contract_directories.append(item)
                elif item.is_dir():
                    explore_contracts(item)

        explore_contracts(contracts_dir)

        current_bytecode = {}

        for contract_dir in contract_directories:
            break
            #TODO: Equivalence testing is currently broken and needs to be debugged.
            for contract in [c for c in contract_dir.iterdir()]:
                try:
                    contract_compilation_result = json.loads(contract.read_text('utf-8'))["bytecode"]["object"]
                except json.JSONDecodeError:
                    logger.warning(f"Could not read compilation result for {contract.name}")
                    continue

                current_bytecode[contract] = \
                    strip_metadata(contract_compilation_result)

        return current_bytecode
