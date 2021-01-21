from eth_vertigo.core.campaign import BaseCampaign
from typing import List
from eth_vertigo.mutator.mutator import Mutator
from pathlib import Path
from eth_vertigo.core.network import NetworkPool


class TruffleCampaign(BaseCampaign):
    def __init__(
            self,
            truffle_location: str,
            project_directory: Path,
            mutators: List[Mutator],
            network_pool: NetworkPool,
            filters=None,
            suggesters=None
    ):
        from eth_vertigo.interfaces.truffle.tester import TruffleTester
        from eth_vertigo.interfaces.truffle.compiler import TruffleCompiler
        from eth_vertigo.interfaces.truffle.mutator import SolidityFile

        compiler = TruffleCompiler(truffle_location)
        tester = TruffleTester(truffle_location, str(project_directory), compiler)
        source_file_builder = lambda path: SolidityFile(path)

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

    def _get_sources(self, dir=None):
        """ Implements basic mutator file discovery """
        if not (self.project_directory / "build").exists():
            self.compiler.run_compilation(str(self.project_directory))

        dir = dir or self.source_directory
        for source_file in dir.iterdir():
            if source_file.name == "Migrations.json":
                continue
            if not source_file.name.endswith(".json"):
                continue
            yield self.source_file_builder(source_file)