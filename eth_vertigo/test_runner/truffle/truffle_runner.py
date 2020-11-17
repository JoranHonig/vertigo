from eth_vertigo.test_runner import Runner
from eth_vertigo.test_runner.file_editor import FileEditor
from eth_vertigo.test_runner.truffle.truffle_tester import TruffleTester
from eth_vertigo.test_runner.exceptions import EquivalentMutant
from eth_vertigo.core import Mutation, MutationResult
from typing import Generator, List

from pathlib import Path
from tempfile import mkdtemp
from distutils.dir_util import copy_tree
import shutil
from typing import Dict


def _make_temp_truffle_directory(original_dir: str):
    td = mkdtemp()
    copy_tree(original_dir, td, preserve_symlinks=1)
    return td


def _clean_build_directory(project_path: str):
    build_dir = Path(project_path) / "build"
    if build_dir.is_dir():
        shutil.rmtree(build_dir)


def _set_reporter(directory: str):
    config = Path(directory) / "truffle.js"
    if not config.is_file():
        config = Path(directory) / "truffle-config.js"
    content = config.read_text("utf-8")
    content += "\nmodule.exports.mocha = {reporter: \"json\"};\n"
    content += "\nmodule.exports.solc = {optimizer: { enabled: true, runs: 200}};\n"
    config.write_text(content, "utf-8")


def _set_include_tests(directory: str, test_names: List[str]):
    config = Path(directory) / "truffle.js"
    if not config.is_file():
        config = Path(directory) / "truffle-config.js"

    content = config.read_text("utf-8")

    test_regex = "({})".format("|".join(test_names))
    content += "\nmodule.exports.mocha.grep= \"" + test_regex + "\";\n"
    config.write_text(content, "utf-8")


def _rm_temp_truffle_directory(temp_dir: str):
    shutil.rmtree(temp_dir)


def _apply_mutation(mutation: Mutation, working_directory):
    target_file_name = working_directory + '/' + mutation.relative_path
    FileEditor.edit(target_file_name, mutation.location, mutation.value)


class TruffleRunner(Runner):

    def __init__(self, project_directory, truffle_tester: TruffleTester):
        self.project_directory = project_directory
        self.truffle_tester = truffle_tester

    @property
    def tests(self) -> Generator[str, None, None]:
        raise NotImplementedError

    def run_tests(
            self,
            coverage: bool = False,
            mutation: Mutation = None,
            timeout=None,
            network: str = None,
            original_bytecode: Dict[str, str] = None,
            suggestions: List[str] = None,
    ) -> dict:
        """
        Runs all the tests in the truffle project in a clean environment
        :param coverage: Whether to run the tests with coverage
        :param mutation: List indicating edits that need to be performed on mutator files
        :return: Test results
        """
        if coverage:
            raise NotImplementedError

        temp_dir = _make_temp_truffle_directory(self.project_directory)
        _clean_build_directory(temp_dir)
        _set_reporter(temp_dir)
        if suggestions:
            _set_include_tests(temp_dir, suggestions)

        if mutation:
            _apply_mutation(mutation, temp_dir)
        try:
            if original_bytecode is not None and original_bytecode != {}:
                if self.truffle_tester.check_bytecodes(temp_dir, original_bytecode):
                    raise EquivalentMutant
            result = self.truffle_tester.run_test_command(temp_dir, timeout=timeout, network_name=network)
        finally:
            _rm_temp_truffle_directory(temp_dir)

        return result

    def run_test(self, name: str, coverage: bool = False):
        """
        Runs test with specific name (useless for now since truffle doesn't really support this
        This command will run all the tests to get results!
        :param name: Name of the test to run
        :param coverage: Whether to run the test with coverage
        :return: test result for the requested test
        """
        test_result = self.run_tests()
        if name in test_result.keys():
            return test_result[name]
        return None
