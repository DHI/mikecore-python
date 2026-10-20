import ctypes

import pytest
from numpy.testing import assert_array_equal

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


# Numbers that do not fit in the native int32 are past the last item too
@pytest.mark.parametrize("staticItemNo", [2**31 - 1, 2**31, 2**32 + 1, 2**64])
def test_read_static_item_past_int32(staticItemNo):
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

    item = dfs.ReadStaticItem(staticItemNo)
    first = dfs.ReadStaticItem(1)
    dfs.Close()

    assert item is None
    assert first is not None
    assert "Node id" == first.Name


@pytest.mark.parametrize("staticItemNo", [0, -1])
def test_read_static_item_below_one(staticItemNo):
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

    try:
        with pytest.raises(ValueError):
            dfs.ReadStaticItem(staticItemNo)
    finally:
        dfs.Close()


# ReadStaticItemNext is the oracle for which item each number from 1 up gives
def test_read_static_item_reads_every_item_by_number():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")
    expected = []
    while (item := dfs.ReadStaticItemNext()) is not None:
        expected.append(item.Name)

    # Backwards, so each read has to find its item rather than take the next
    names = {}
    for n in range(len(expected), 0, -1):
        item = dfs.ReadStaticItem(n)
        assert item is not None
        assert n == item.ItemNumber
        names[n] = item.Name
    dfs.Close()

    assert 9 == len(expected)
    assert expected == [names[n] for n in range(1, len(expected) + 1)]


def test_item_quantity_descriptions():
    dfs = DfsFileFactory.DfsGenericOpen("testdata/TemporalEqCal.dfs0")
    quantities = [item.Quantity for item in dfs.ItemInfo]
    dfs.Close()

    assert ["Water Level", "Water Depth"] == [q.ItemDescription for q in quantities]
    assert ["meter", "meter"] == [q.UnitDescription for q in quantities]


@pytest.mark.parametrize(
    "filename, openTyped",
    [
        ("testdata/OresundHD.dfs2", DfsFileFactory.Dfs2FileOpen),
        ("testdata/OresundHD.dfs3", DfsFileFactory.Dfs3FileOpen),
    ],
)
def test_generic_read_reshapes_like_dfs123(filename, openTyped):
    typed = openTyped(filename)
    expected = typed.ReadItemTimeStep(1, 0, reshape=True).Data
    typed.Close()

    dfs = DfsFileFactory.DfsGenericOpen(filename)
    shape = dfs.ItemInfo[0].SpatialAxis.Shape
    nextItemData = dfs.ReadItemTimeStepNext(reshape=True)
    itemData = dfs.ReadItemTimeStep(1, 0, reshape=True)
    dfs.Close()

    assert len(shape) >= 2
    assert shape == expected.shape
    assert nextItemData is not None
    assert_array_equal(expected, nextItemData.Data)
    assert itemData is not None
    assert_array_equal(expected, itemData.Data)


# A 0-D axis has Shape (0,) but holds one value, and a 1-D axis is already flat
@pytest.mark.parametrize(
    "filename, size",
    [("testdata/TemporalEqCal.dfs0", 1), ("testdata/OresundHD.dfsu", 3636)],
)
def test_generic_read_does_not_reshape_0d_or_1d(filename, size):
    dfs = DfsFileFactory.DfsGenericOpen(filename)
    itemData = dfs.ReadItemTimeStep(1, 0, reshape=True)
    dfs.Close()

    assert itemData is not None
    assert (size,) == itemData.Data.shape


@pytest.mark.parametrize(
    "filename", ["testdata/OresundHD.dfs2", "testdata/OresundHD.dfs3"]
)
def test_generic_read_stays_flat_without_reshape(filename):
    dfs = DfsFileFactory.DfsGenericOpen(filename)
    size = dfs.ItemInfo[0].ElementCount
    nextItemData = dfs.ReadItemTimeStepNext()
    itemData = dfs.ReadItemTimeStep(1, 0)
    dfs.Close()

    assert nextItemData is not None
    assert (size,) == nextItemData.Data.shape
    assert itemData is not None
    assert (size,) == itemData.Data.shape
