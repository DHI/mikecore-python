import ctypes

import numpy as np
import pytest

from mikecore.DfsDLL import DfsDLL
from mikecore.DfsFile import DfsDLLUtil, DfsFile, DfsFileMode, TimeAxisType
from mikecore.DfsFileFactory import DfsFileFactory


def test_timeaxis():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/TemporalEqCal.dfs0")
    timeaxistype = dfs.FileInfo.TimeAxis.TimeAxisType
    dfs.Close()

    assert timeaxistype == TimeAxisType.CalendarEquidistant


def test_iteminfo():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/TemporalEqCal.dfs0")
    # iinfo1 = dfs.GetItemInfo(1)  # Note 1-based
    iinfo1 = dfs.ItemInfo[0]

    dfs.Close()
    assert iinfo1.Name == "WaterLevel item"


def test_read_itemtimestepnext():

    dfs = DfsFileFactory.DfsGenericOpen("testdata/TemporalEqCal.dfs0")
    dfs.Reset()

    data = dfs.ReadItemTimeStepNext()

    dfs.Close()

    assert data.Data.shape == (1,)


def test_read_itemtimestep():

    dfs = DfsFileFactory.DfsGenericOpen("testdata/TemporalEqCal.dfs0")
    dfs.Reset()

    data = None
    for _ in range(2 * 5):
        data = dfs.ReadItemTimeStepNext()

    dfs.Close()

    assert data is not None
    assert data.Data[0] == 104


@pytest.mark.parametrize(
    "opener, filename, reshape",
    [
        ("DfsGenericOpen", "testdata/TemporalNeqCal.dfs0", False),
        ("Dfs2FileOpen", "testdata/OresundHD.dfs2", False),
        ("Dfs2FileOpen", "testdata/OresundHD.dfs2", True),
        ("Dfs3FileOpen", "testdata/OresundHD.dfs3", True),
        ("DfsGenericOpen", "testdata/OdenseHD2D.dfsu", False),
    ],
    ids=["dfs0", "dfs2", "dfs2-reshape", "dfs3-reshape", "dfsu"],
)
def test_read_itemtimestep_into_given_itemdata(opener, filename, reshape):
    """ReadItemTimeStep(itemData, j) fills and returns the itemData it is given,
    with the same values as ReadItemTimeStep(itemNumber, j) allocates."""
    dfs = getattr(DfsFileFactory, opener)(filename)
    numberOfTimeSteps = dfs.FileInfo.TimeAxis.NumberOfTimeSteps
    assert numberOfTimeSteps > 1

    changed = False
    for itemNumber in range(1, len(dfs.ItemInfo) + 1):
        itemData = dfs.ReadItemTimeStep(itemNumber, numberOfTimeSteps - 1, reshape)
        buffer = itemData.Data
        # Backwards, so the buffer holds another timestep's values before each read
        for j in reversed(range(numberOfTimeSteps)):
            expected = dfs.ReadItemTimeStep(itemNumber, j, reshape)
            before = itemData.Data.copy()

            assert dfs.ReadItemTimeStep(itemData, j, reshape) is itemData
            assert np.shares_memory(itemData.Data, buffer)
            assert itemNumber == itemData.ItemNumber
            assert j == itemData.TimeStepIndex
            assert expected.Time == itemData.Time
            np.testing.assert_array_equal(expected.Data, itemData.Data)
            changed = changed or not np.array_equal(before, itemData.Data)
    dfs.Close()

    assert changed, "every read left the buffer as it was"


def test_error_reporting():

    print(DfsDLL.dfsErrorString(1000))
    try:
        DfsDLL.CheckReturnCode(2007)
    except Exception as e:
        print("Exception:", e)


def test_item_value_type_reports_dfs_error():
    with pytest.raises(Exception, match="DFS error code 1000"):
        DfsDLLUtil.dfsGetItemValueType(ctypes.c_void_p())


def test_open_with_integer_mode():
    dfs = DfsFile()

    dfs.Open("testdata/TemporalEqCal.dfs0", 0)
    names = [item.Name for item in dfs.ItemInfo]
    dfs.Close()

    assert ["WaterLevel item", "WaterDepth item"] == names


def test_open_in_closed_mode_fails():
    dfs = DfsFile()

    with pytest.raises(ValueError, match="Cannot open a file in mode"):
        dfs.Open("testdata/TemporalEqCal.dfs0", DfsFileMode.Closed)


def test_read_static_item_next_returns_each_static_item_once():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

    names = []
    item = dfs.ReadStaticItemNext()
    while item is not None:
        names.append(item.Name)
        item = dfs.ReadStaticItemNext()
    dfs.Close()

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


def test_read_static_item_after_read_static_item_next():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")
    dfs.ReadStaticItemNext()
    dfs.ReadStaticItemNext()

    item = dfs.ReadStaticItem(1)
    dfs.Close()

    assert item is not None
    assert "Node id" == item.Name


def test_read_static_item_past_the_last_item():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

    item = dfs.ReadStaticItem(10)
    dfs.Close()

    assert item is None


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Suspected bug: ReadStaticItem does not check the item number and ignores "
        "the return code of dfsFindItemStatic, so ReadStaticItem(0) returns the "
        "first static item ('Node id') with ItemNumber 0. Static item numbers start "
        "at 1. Correct: reject numbers below 1 with a ValueError, as "
        "__DynamicItemInfoReadAndCreate does for dynamic items."
    ),
)
def test_read_static_item_zero():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

    try:
        with pytest.raises(ValueError):
            dfs.ReadStaticItem(0)
    finally:
        dfs.Close()


def test_item_quantity_descriptions():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/TemporalEqCal.dfs0")
    quantities = [item.Quantity for item in dfs.ItemInfo]
    dfs.Close()

    assert ["Water Level", "Water Depth"] == [q.ItemDescription for q in quantities]
    assert ["meter", "meter"] == [q.UnitDescription for q in quantities]
