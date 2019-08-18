from pathlib import Path
from eth_vertigo.test_runner.file_editor import FileEditor
import pytest

CONTENT = u"aaaaa"

def test_edit_in_range(tmp_path):
    # Arrange
    p: Path = tmp_path / "target.txt"
    p.write_text(CONTENT)

    file_editor = FileEditor()

    # Act
    file_editor.edit(str(p.absolute()), (1, 2, 0), 'bb')

    # Assert
    assert "abbaa" == p.read_text()


def test_edit_outside_range(tmp_path):
    # Arrange
    p: Path = tmp_path / "target.txt"
    p.write_text(CONTENT)

    file_editor = FileEditor()

    # Act
    file_editor.edit(str(p.absolute()), (10, 2, 0), 'bb')

    # Assert
    assert "aaaaabb" == p.read_text()

def test_edit_negative(tmp_path):
    # Arrange
    p: Path = tmp_path / "target.txt"
    p.write_text(CONTENT)

    file_editor = FileEditor()

    # Act and assert
    with pytest.raises(ValueError):
        file_editor.edit(str(p.absolute()), (-10, 2, 0), 'b')

