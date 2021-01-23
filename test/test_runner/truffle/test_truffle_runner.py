import shutil
from pathlib import Path
import pytest

from unittest.mock import MagicMock

from eth_vertigo.core import Mutation
from eth_vertigo.mutator.source_file import SourceFile
from eth_vertigo.interfaces.truffle.compiler import TruffleCompiler
from eth_vertigo.interfaces.truffle.tester import TruffleTester, _set_reporter, _set_include_tests
from eth_vertigo.interfaces.common.tester import make_temp_directory, rm_temp_directory, apply_mutation


def test_mk_tmp_truffle_directory(tmp_path: Path):
    # Arrange
    file = tmp_path / "file.txt"  # type: Path
    file.write_text("example text")

    # Act
    created_dir = make_temp_directory(str(tmp_path))
    created_path = Path(created_dir)
    copied_file = created_path / "file.txt"

    # Assert
    try:
        assert file.read_text("utf-8") == copied_file.read_text('utf-8')
    finally:
        # Cleanup
        shutil.rmtree(created_dir)


def test_rm_truffle_directory(tmp_path):
    # Arrange
    directory = make_temp_directory(str(tmp_path))
    dir_path = Path(directory)

    # Act
    rm_temp_directory(directory)

    # Assert
    assert dir_path.exists() is False


def test_set_reporter(tmp_path: Path):
    # Arrange
    pre_text = "text_that was here before;"
    truffle_js = tmp_path / "truffle.js"  # type: Path
    truffle_js.write_text(pre_text)

    # Act
    _set_reporter(str(tmp_path))

    # Assert
    expected = pre_text + \
           "\nmodule.exports.mocha = {reporter: \"json\"};\n" + \
           "\nmodule.exports.solc = {optimizer: { enabled: true, runs: 200}};\n"
    actual = truffle_js.read_text("utf-8")
    assert expected == actual


def test_apply_mutation(tmp_path):
    # Arrange
    file_path = tmp_path / "mutator.sol"  # type: Path
    file_path.touch()
    source_file = SourceFile(file_path)
    src_field = (1, 1, 0)

    mutation = Mutation(location=src_field, source=source_file, value="value", project_directory=tmp_path)

    # Act
    apply_mutation(mutation, str(tmp_path))

    # Assert
    assert "value" == file_path.read_text("utf-8")



def test_truffle_runner_run_tests(tmp_path):
    # Arrange
    truffle_js = tmp_path / "truffle.js"  # type: Path
    truffle_js.touch()

    expected_test_result = {"test_result": True}
    truffle_tester = TruffleTester(str(truffle_js), str(tmp_path), TruffleCompiler(str(truffle_js)))
    truffle_tester.run_test_command = MagicMock(return_value=expected_test_result)

    # Act
    test_result = truffle_tester.run_tests()

    # Assert
    assert expected_test_result == test_result


def test_truffle_runner_run_coverage(tmp_path):
    # Arrange
    truffle_js = tmp_path / "truffle.js"  # type: Path
    truffle_js.touch()

    expected_test_result = {"test_result": True}
    truffle_tester = TruffleTester(str(truffle_js), str(tmp_path), TruffleCompiler(str(truffle_js)))
    truffle_tester.run_test_command = MagicMock(return_value=expected_test_result)

    # Act and Assert
    with pytest.raises(NotImplementedError):
        truffle_tester.run_tests(coverage=True)


def test_truffle_runner_run_test_with_mutation(tmp_path):
    # Arrange
    file_path = tmp_path / "mutator.sol"  # type: Path
    file_path.touch()
    source_file = SourceFile(file_path)
    src_field = (1, 1, 0)

    mutation = Mutation(location=src_field, source=source_file, value="value", project_directory=tmp_path)

    truffle_js = tmp_path / "truffle.js"  # type: Path
    truffle_js.touch()

    expected_test_result = {"test_result": True}
    truffle_tester = TruffleTester(str(truffle_js), str(tmp_path), TruffleCompiler(str(truffle_js)))
    truffle_tester.run_test_command = MagicMock(return_value=expected_test_result)

    # Act
    test_result = truffle_tester.run_tests(mutation=mutation)

    # Assert
    assert expected_test_result == test_result
