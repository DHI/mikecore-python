import datetime
import shutil
import unittest

import numpy as np
import pytest

from mikecore.DfsBuilder import DfsBuilder
from mikecore.DfsFactory import DfsFactory
from mikecore.DfsFile import DataValueType, DfsSimpleType
from mikecore.eum import eumItem, eumQuantity, eumUnit
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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Suspected bug: Dfs0ToAscii adds itemData.Time to the start as seconds "
        "(its own TODO says the time unit is not always seconds), but "
        "ReadItemTimeStepNext returns times in the time axis unit. With a "
        "10 minute step the second row is stamped 00:00:10. Correct: convert "
        "with the time axis's ToSeconds, giving 00:10:00."
    ),
)
def test_Dfs0ToAscii_writes_calendar_times_in_minutes(tmp_path):
    dfs0FileName = str(tmp_path / "minutes.dfs0")
    factory = DfsFactory()
    builder = DfsBuilder.Create("title", "application", 1)
    builder.SetDataType(0)
    builder.SetGeographicalProjection(factory.CreateProjectionUndefined())
    builder.SetTemporalAxis(
        factory.CreateTemporalEqCalendarAxis(
            eumUnit.eumUminute, datetime.datetime(2020, 1, 1), 0, 10
        )
    )
    item = builder.CreateDynamicItemBuilder()
    item.Set(
        "Value",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    item.SetValueType(DataValueType.Instantaneous)
    item.SetAxis(factory.CreateAxisEqD0())
    builder.AddDynamicItem(item.GetDynamicItemInfo())
    builder.CreateFile(dfs0FileName)
    dfs0 = builder.GetFile()
    for value in (1.0, 2.0):
        dfs0.WriteItemTimeStepNext(0, np.array([value], dtype=np.float32))
    dfs0.Close()
    txtFileName = str(tmp_path / "minutes.txt")

    Dfs0ToAscii(dfs0FileName, txtFileName)

    lines = _data_lines(txtFileName)
    assert [["2020-01-01", "00:00:00.000"], ["2020-01-01", "00:10:00.000"]] == [
        line.split()[:2] for line in lines
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
