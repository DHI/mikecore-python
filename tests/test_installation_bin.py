"""MIKECORE_PYTHON_BIN: mikecore uses a MIKE installation's native libraries."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGES = Path(__file__).parents[1] / "packages"
RUNTIME = "win-x64" if os.name == "nt" else "linux-x64"

# Each run is a new process: mikecore loads its native libraries once, at import.
READ_ORESUND = """
import mikecore
from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.Projections import Cartography

dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfs2")
item = dfs.ItemInfo[0]
data = dfs.ReadItemTimeStep(1, 0).Data
x, y = Cartography(dfs.FileInfo.Projection.WKTString).Geo2Proj(12.6, 55.7)
print(mikecore.mikebin)
print(item.Name, item.Quantity.Item, item.Quantity.Unit)
print(data[:5].tolist(), round(x, 3), round(y, 3))
"""


def run_read(installation_bin: Path | None) -> list[str]:
    env = dict(os.environ)
    env.pop("MIKECORE_PYTHON_BIN", None)
    if installation_bin is not None:
        env["MIKECORE_PYTHON_BIN"] = str(installation_bin)
    result = subprocess.run(
        [sys.executable, "-c", READ_ORESUND],
        cwd=Path(__file__).parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


@pytest.fixture
def installation_bin(tmp_path: Path) -> Path:
    """A folder of MIKE Core's libraries under their own names, laid out like a
    MIKE installation's bin, from the NuGet packages the build downloads."""
    natives = list(PACKAGES.glob(f"*/runtimes/{RUNTIME}/native"))
    if not natives:
        pytest.skip("needs the NuGet packages that building a checkout downloads")
    for native in natives:
        shutil.copytree(native, tmp_path, dirs_exist_ok=True)
    return tmp_path


def test_installation_libraries_read_like_the_bundled_ones(installation_bin):
    mikebin, *results = run_read(installation_bin)

    assert Path(mikebin) == installation_bin
    assert results == run_read(None)[1:]
