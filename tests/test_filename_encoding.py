import os
import shutil

import pytest

from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.DfsuFile import DfsuFile
from tests.examples_dfsu import ExamplesDfsu


def _representable(name):
    if os.name != "nt":
        return True
    try:
        name.encode("mbcs")
        return True
    except UnicodeEncodeError:
        return False


# The Danish name is representable in cp1252 (the code page on GitHub's
# Windows runners); the Chinese one only on a Chinese code page, or on Linux.
NAMES = ["Øresund æøå", "项目 合界数模"]


@pytest.mark.parametrize("name", NAMES)
def test_open_non_ascii_path(tmp_path, name):
    if not _representable(name):
        pytest.skip("not representable in this machine's ANSI code page")
    folder = tmp_path / name
    folder.mkdir()
    filename = folder / (name + ".dfsu")
    shutil.copy("testdata/OresundHD.dfsu", filename)

    dfs = DfsuFile.Open(str(filename))
    assert dfs.NumberOfElements == 3636
    dfs.Close()


@pytest.mark.parametrize("name", NAMES)
def test_create_non_ascii_path(tmp_path, name):
    if not _representable(name):
        pytest.skip("not representable in this machine's ANSI code page")
    folder = tmp_path / name
    folder.mkdir()
    filename = folder / (name + ".dfsu")

    ExamplesDfsu.CreateDfsuFile("testdata/OresundHD.dfsu", str(filename), True)

    assert filename.exists()
    dfs = DfsFileFactory.DfsuFileOpen(str(filename))
    assert dfs.NumberOfElements == 3636
    dfs.Close()


@pytest.mark.skipif(os.name != "nt", reason="Windows ANSI code page only")
def test_unrepresentable_path_gives_clear_error(tmp_path):
    name = next((n for n in NAMES if not _representable(n)), None)
    if name is None:
        pytest.skip("every test name is representable in this code page")
    filename = tmp_path / (name + ".dfsu")
    shutil.copy("testdata/OresundHD.dfsu", filename)
    with pytest.raises(ValueError, match="ANSI code page"):
        DfsuFile.Open(str(filename))
