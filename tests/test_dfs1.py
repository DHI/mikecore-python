import numpy as np
import pytest
from mikecore.DfsBuilder import DataValueType, DfsBuilder, DfsSimpleType
from mikecore.DfsFactory import DfsFactory
from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.eum import eumItem, eumQuantity, eumUnit

# There is no dfs1 file in testdata, so the tests create one


@pytest.fixture
def dfs1File(tmp_path):
    factory = DfsFactory()
    builder = DfsBuilder.Create("title", "application", 1)
    builder.SetDataType(0)
    builder.SetGeographicalProjection(factory.CreateProjectionUndefined())
    builder.SetTemporalAxis(factory.CreateTemporalEqTimeAxis(eumUnit.eumUsec, 0, 60))
    builder.SetSpatialAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 5, 0, 10))
    for name in ("Level", "Depth"):
        item = builder.CreateDynamicItemBuilder()
        item.Set(
            name,
            eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
            DfsSimpleType.Float,
        )
        item.SetValueType(DataValueType.Instantaneous)
        item.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 5, 0, 10))
        builder.AddDynamicItem(item.GetDynamicItemInfo())
    filename = str(tmp_path / "test.dfs1")
    builder.CreateFile(filename)
    builder.AddCreateStaticItem(
        "Bathymetry",
        eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter),
        np.arange(5, dtype=np.float32),
        factory.CreateAxisEqD1(eumUnit.eumUmeter, 5, 0, 10),
    )
    file = builder.GetFile()
    for _ in range(2):
        file.WriteItemTimeStepNext(0, np.zeros(5, dtype=np.float32))
    file.Close()
    return filename


def test_modify_item_info(dfs1File):
    # Check existing data
    file = DfsFileFactory.Dfs1FileOpen(dfs1File)
    assert "Level" == file.ItemInfo[0].Name
    assert eumItem.eumIWaterLevel == file.ItemInfo[0].Quantity.Item
    assert eumUnit.eumUmeter == file.ItemInfo[0].Quantity.Unit
    assert "Depth" == file.ItemInfo[1].Name
    file.Close()

    file = DfsFileFactory.Dfs1FileOpenEdit(dfs1File)
    file.ItemInfo[0].Name = "WL"
    file.ItemInfo[0].Quantity = eumQuantity(eumItem.eumIWaterDepth, eumUnit.eumUfeet)
    file.Close()

    # The name is padded to the old length
    file = DfsFileFactory.Dfs1FileOpen(dfs1File)
    assert "WL   " == file.ItemInfo[0].Name
    assert eumItem.eumIWaterDepth == file.ItemInfo[0].Quantity.Item
    assert eumUnit.eumUfeet == file.ItemInfo[0].Quantity.Unit
    assert "Depth" == file.ItemInfo[1].Name
    file.Close()


def axisValues(axis):
    assert axis is not None
    return (axis.X0, axis.Dx)


def test_modify_axis(dfs1File):
    # Check existing data
    file = DfsFileFactory.Dfs1FileOpen(dfs1File)
    assert (0, 10) == axisValues(file.SpatialAxis)
    for itemInfo in file.ItemInfo:
        assert (0, 10) == axisValues(itemInfo.SpatialAxis)
    staticItem = file.ReadStaticItemNext()
    assert staticItem is not None
    assert (0, 10) == axisValues(staticItem.SpatialAxis)
    assert file.ReadStaticItemNext() is None
    file.Close()

    file = DfsFileFactory.Dfs1FileOpenEdit(dfs1File)
    axis = file.SpatialAxis
    assert axis is not None
    axis.X0 = 55
    axis.Dx = 905
    file.Close()

    # Check all dynamic and static items
    file = DfsFileFactory.Dfs1FileOpen(dfs1File)
    assert (55, 905) == axisValues(file.SpatialAxis)
    for itemInfo in file.ItemInfo:
        assert (55, 905) == axisValues(itemInfo.SpatialAxis)
    staticItem = file.ReadStaticItemNext()
    assert staticItem is not None
    assert (55, 905) == axisValues(staticItem.SpatialAxis)
    # Writing the axis keeps the static item data
    np.testing.assert_equal(np.arange(5, dtype=np.float32), staticItem.Data)
    file.Close()
