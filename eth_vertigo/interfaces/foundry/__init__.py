from eth_vertigo.core.campaign import BaseCampaign
from typing import List
from eth_vertigo.mutator.mutator import Mutator
from pathlib import Path
from eth_vertigo.core.network import NetworkPool
from json import loads


class FoundryCampaign(BaseCampaign):
    def __init__(
            self,
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

        cache_dir = self.project_directory / "cache"
        if not cache_dir.exists():
            self.compiler.run_compilation(str(self.project_directory))

        cache = loads(Path(f"{cache_dir}/solidity-files-cache.json").read_text("utf-8"))
        files = cache["files"]
        
        for file in files:
            if file.startswith("src/"):
                contract = files[file]
                basename = Path(contract["sourceName"]).name
                stem      = Path(contract["sourceName"]).stem

                build_info_file = contracts_dir/basename/(stem + ".json")
                build_info = loads(build_info_file.read_text("utf-8"))

                ast = build_info["ast"]
                absolute_path = self.project_directory / ast["absolutePath"]

                yield self.source_file_builder(ast, absolute_path)
