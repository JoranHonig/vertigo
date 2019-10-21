import pytest
from pathlib import Path
from eth_vertigo.mutator.source_file import SourceFile

from eth_vertigo.core.mutation import Mutation, MutationResult


def test_create_mutation(tmp_path: Path):
    # Arrange
    location = (1, 1, 0)
    source = None
    value = "replacement"
    project_directory = tmp_path

    # Act
    mutation = Mutation(location, source, value, project_directory)

    # Assert
    assert location == mutation.location
    assert source == mutation.source
    assert value == mutation.value
    assert project_directory == mutation.project_directory

    assert mutation.result is None
    assert mutation.crime_scenes == []


def test_relative_path(tmp_path):
    # Arrange
    (tmp_path / "testdir").mkdir()
    sf_file: Path = tmp_path / "testdir" / "sf.txt"
    sf_file.write_text("some text", encoding="utf-8")

    sf = SourceFile(sf_file)

    mutation = Mutation(None, sf, None, tmp_path)

    # Act
    relative_path = mutation.relative_path

    # Assert
    assert Path("testdir/sf.txt") == Path(relative_path)


def test_get_mutated_line(tmp_path):
    # Arrange
    file = tmp_path / "sf.txt"
    file.write_text("yeah\ngood", encoding="utf-8")

    sf = SourceFile(file)
    mutation = Mutation(None, None, None, None)

    # Act
    mutated_line = mutation._get_mutated_line(6, sf.file.read_text(encoding="utf-8"))

    # Assert
    assert mutated_line == (1, "good")


def test_repr(tmp_path):
    # Arrange
    file = tmp_path / "sf.txt"
    file.write_text("yeah\ngood", encoding="utf-8")

    sf = SourceFile(file)
    mutation = Mutation((6, 1, 0), sf, "b", tmp_path)
    mutation.result = MutationResult.LIVED
    # Act
    repr_ = str(mutation)
    print(repr_)
    # Assert
    assert repr_ == \
        "Mutation:\n"\
        "    File: " + str(file) + "\n" \
        "    Line nr: 1\n" \
        "    Result: Lived\n" \
        "    Original line:\n" \
        "         good\n" \
        "    Mutated line:\n" \
        "         gbod"
