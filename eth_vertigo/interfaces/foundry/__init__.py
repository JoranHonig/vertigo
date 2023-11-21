from eth_vertigo.core.campaign import BaseCampaign
from typing import List
from eth_vertigo.mutator.mutator import Mutator
from pathlib import Path
from eth_vertigo.core.network import NetworkPool
from json import loads
import glob
import os
import re


class FoundryCampaign(BaseCampaign):
    def __init__(
            self,
            src_dir: str,
            exclude_regex: str,
            scope_file: str,
            foundry_command: List[str],
            project_directory: Path,
            mutators: List[Mutator],
            network_pool: NetworkPool,
            filters=None,
            suggesters=None
    ):
        from eth_vertigo.interfaces.foundry.tester import FoundryTester
        from eth_vertigo.interfaces.foundry.compile import FoundryCompiler
        from eth_vertigo.interfaces.foundry.mutator import FoundrySourceFile

        self.src_dir = src_dir
        self.exclude_regex = exclude_regex
        self.scope_file = scope_file
        compiler = FoundryCompiler(foundry_command)
        tester = FoundryTester(foundry_command, str(project_directory), compiler)
        source_file_builder = lambda ast, full_path: FoundrySourceFile(ast, full_path)
        super().__init__(
            project_directory=project_directory,
            mutators=mutators,
            network_pool=network_pool,

            compiler=compiler,
            tester=tester,
            source_file_builder=source_file_builder,

            filters=filters,
            suggesters=suggesters
        )

    def _get_sources(self):
        """ Implements basic mutator file discovery """
        contracts_dir = self.project_directory / "out"
        if not contracts_dir.exists():
            self.compiler.run_compilation(str(self.project_directory))

        if self.scope_file and not self.scope_file.isspace():
            with open(self.scope_file, 'r') as file:
                full_names = file.read().splitlines()
        else:
            # TODO: This might not be the most reliable way to find the source files
            #       but it works for now. Glob the source directory, then find the set intersection
            #       between the files in src and the files in the out directory
            if str(self.src_dir).endswith('/'):
                self.src_dir = self.src_dir[:-1]
            full_names = glob.glob(self.src_dir + '/**/*.sol', recursive=True) 

        exclude_object = re.compile(self.exclude_regex)

        full_names = set(filter(lambda name: not exclude_object.search(name), full_names))
        src_file_names = set(map(os.path.basename, full_names))
        contract_directories = []
        def explore_contracts(directory: Path):
            for item in directory.iterdir():
                if item.name in src_file_names and item.name.endswith(".sol"):
                    contract_directories.append(item)
                elif item.is_dir():
                    explore_contracts(item)

        explore_contracts(contracts_dir)

        for contract_dir in contract_directories:
            for contract in [c for c in contract_dir.iterdir()]:
                contract = loads(contract.read_text("utf-8"))

                ast = contract["ast"]
                absolute_path = self.project_directory / ast["absolutePath"]
                yield self.source_file_builder(ast, absolute_path)
            #for contract in [c for c in contract_dir.iterdir() if "dbg.json" not in c.name]:

                #yield self.source_file_builder(ast, absolute_path)
                '''
                dbg_json = contract_dir / contract.name.replace('.json', '.dbg.json')

                contract = loads(contract.read_text("utf-8"))
                dbg = loads(dbg_json.read_text("utf-8"))

                source_name = contract["sourceName"]
                build_info_file = contract_dir / dbg["buildInfo"]
                build_info = loads(build_info_file.read_text("utf-8"))

                ast = build_info["output"]["sources"][source_name]["ast"]
                absolute_path = self.project_directory / ast["absolutePath"]

                yield self.source_file_builder(ast, absolute_path)
                '''
