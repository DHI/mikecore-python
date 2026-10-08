import shutil
import unittest

import pytest

from miketools.Dfs0ToAscii import *
from miketools.DfsShowInfo import DfsShowInfo


class Test_miketools(unittest.TestCase):
    def test_Dfs0ToAscii(self):
        Dfs0ToAscii(
            "testdata/Rain_accumulated.dfs0", "testdata/testtmp/Rain_accumulated.txt"
        )
        Dfs0ToAscii(
            "testdata/Rain_backwardStep.dfs0", "testdata/testtmp/Rain_backwardStep.txt"
        )
        Dfs0ToAscii(
            "testdata/Rain_forwardStep.dfs0", "testdata/testtmp/Rain_forwardStep.txt"
        )
        Dfs0ToAscii(
            "testdata/Rain_instantaneous.dfs0",
            "testdata/testtmp/Rain_instantaneous.txt",
        )
        Dfs0ToAscii(
            "testdata/Rain_stepaccumulated.dfs0",
            "testdata/testtmp/Rain_stepaccumulated.txt",
        )
        Dfs0ToAscii("testdata/TemporalEqCal.dfs0", "testdata/testtmp/TemporalEqCal.txt")
        Dfs0ToAscii(
            "testdata/TemporalEqTime.dfs0", "testdata/testtmp/TemporalEqTime.txt"
        )
        Dfs0ToAscii(
            "testdata/TemporalNeqCal.dfs0", "testdata/testtmp/TemporalNeqCal.txt"
        )
        Dfs0ToAscii(
            "testdata/TemporalNeqTime.dfs0", "testdata/testtmp/TemporalNeqTime.txt"
        )


def _data_lines(txtFileName):
    with open(txtFileName) as txt:
        # Four header lines, then one line per timestep
        return txt.read().splitlines()[4:]


def test_Dfs0ToAscii_writes_calendar_times(tmp_path):
    txtFileName = str(tmp_path / "TemporalEqCal.txt")

    Dfs0ToAscii("testdata/TemporalEqCal.dfs0", txtFileName)

    lines = _data_lines(txtFileName)
    assert 10 == len(lines)
    assert ["2010-01-04", "12:34:04.000", 0.0, 100.0] == [
        *lines[0].split()[:2],
        *map(float, lines[0].split()[2:]),
    ]
    assert ["2010-01-04", "12:34:14.000", 1.0, 101.0] == [
        *lines[1].split()[:2],
        *map(float, lines[1].split()[2:]),
    ]


def test_Dfs0ToAscii_writes_relative_times(tmp_path):
    txtFileName = str(tmp_path / "TemporalEqTime.txt")

    Dfs0ToAscii("testdata/TemporalEqTime.dfs0", txtFileName)

    lines = _data_lines(txtFileName)
    assert 10 == len(lines)
    assert [3.0, 0.0, 100.0] == [float(v) for v in lines[0].split()]
    assert [13.0, 1.0, 101.0] == [float(v) for v in lines[1].split()]


def test_Dfs0ToAscii_truncated_file(tmp_path):
    dfs0FileName = str(tmp_path / "truncated.dfs0")
    shutil.copyfile("testdata/TemporalEqCal.dfs0", dfs0FileName)
    with open(dfs0FileName, "r+b") as dfs0:
        # Remove the end of the file, part-way into timestep index 8
        dfs0.truncate(dfs0.seek(0, 2) - 40)

    with pytest.raises(Exception, match="Could not read item 1 at timestep index 8"):
        Dfs0ToAscii(dfs0FileName, str(tmp_path / "truncated.txt"))


def test_DfsShowInfo_lists_static_items(capsys):
    DfsShowInfo("testdata/OresundHD.dfsu")

    output = capsys.readouterr().out
    staticItems = output.split("---- Static items  ---- \n")[1].split(
        "---- Dynamic items ---- \n"
    )[0]
    names = [line.split(":")[1].strip() for line in staticItems.splitlines()]
    assert [
        "Node id",
        "X-coord",
        "Y-coord",
        "Z-coord",
        "Code",
        "Element id",
        "Element type",
        "No of nodes",
        "Connectivity",
    ] == names
