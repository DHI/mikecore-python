import pytest

from mikecore.DfsDLL import DfsDLL
from mikecore.DfsFile import DfsFile, DfsFileMode, TimeAxisType
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


def test_error_reporting():

    print(DfsDLL.dfsErrorString(1000))
    try:
        DfsDLL.CheckReturnCode(2007)
    except Exception as e:
        print("Exception:", e)


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
