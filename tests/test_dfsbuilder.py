from datetime import datetime

import numpy as np
from mikecore.DfsBuilder import (
    DfsBuilder,
    DfsSimpleType,
    DataValueType,
    DfsStaticItemBuilder,
)
from mikecore.DfsFactory import DfsFactory
from mikecore.eum import eumUnit, eumQuantity, eumItem

import pytest


@pytest.fixture
def landuse():
    builder = DfsBuilder.Create()

    factory = DfsFactory()

    # Set up the header
    builder.SetDataType(0)
    builder.SetGeographicalProjection(
        factory.CreateProjectionGeoOrigin("NON-UTM", 0, 0, 0)
    )
    builder.SetTemporalAxis(
        factory.CreateTemporalEqCalendarAxis(
            eumUnit.eumUsec, datetime(2000, 1, 1, 10, 0, 0), 0, 1
        )
    )
    builder.SetSpatialAxis(
        factory.CreateAxisEqD2(eumUnit.eumUmeter, 62, 0, 500, 70, 0, 500)
    )
    builder.DeleteValueFloat = -2

    # Set up dynamic items
    builder.AddCreateDynamicItem(
        "Landuse",
        eumQuantity.Create(eumItem.eumIIntegerCode, eumUnit.eumUintCode),
        DfsSimpleType.Float,
        DataValueType.Instantaneous,
    )

    return builder


def test_validate_empty_builder():

    builder = DfsBuilder("filetitle")

    errors = builder.Validate(dieOnError=False)

    assert len(errors) > 0


def test_empty_title(landuse: DfsBuilder, tmp_path):
    # Create and get file
    landuse.CreateFile(str(tmp_path / "notused.dfs2"))
    file = landuse.GetFile()


def test_getfile_not_possible_if_not_created(landuse: DfsBuilder):
    builder = landuse

    # Create and get file
    # builder.CreateFile("notused.dfs2") # this is an important step
    with pytest.raises(Exception, match="CreateFile has not yet been called"):
        builder.GetFile()


def test_getfiletwice_not_allowed(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    file = builder.GetFile()

    with pytest.raises(Exception, match="File has been returned"):
        builder.GetFile()


def test_filetitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    file = builder.GetFile()

    with pytest.raises(Exception, match="File has been returned"):
        builder.SetFileTitle("too late")


def test_apptitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    file = builder.GetFile()

    with pytest.raises(Exception, match="File has been returned"):
        builder.SetApplicationTitle("too late")


@pytest.mark.parametrize(
    "delete_value",
    [
        "DeleteValueFloat",
        "DeleteValueDouble",
        "DeleteValueByte",
        "DeleteValueInt",
        "DeleteValueUnsignedInt",
    ],
)
def test_delete_value_after_create_not_possible(
    landuse: DfsBuilder, tmp_path, delete_value
):
    builder = landuse

    builder.CreateFile(str(tmp_path / "notused.dfs2"))

    with pytest.raises(Exception, match="CreateFile has been called"):
        setattr(builder, delete_value, 0)


def test_validate_reports_encode_key_outside_axis():
    builder = DfsBuilder.Create("title", "app", 1)
    factory = DfsFactory()
    builder.SetDataType(0)
    builder.SetGeographicalProjection(
        factory.CreateProjectionGeoOrigin("NON-UTM", 0, 0, 0)
    )
    builder.SetTemporalAxis(
        factory.CreateTemporalEqCalendarAxis(
            eumUnit.eumUsec, datetime(2000, 1, 1), 0, 1
        )
    )
    builder.SetSpatialAxis(
        factory.CreateAxisEqD3(eumUnit.eumUmeter, 4, 0, 1, 3, 0, 1, 2, 0, 1)
    )
    builder.AddCreateDynamicItem(
        "Item",
        eumQuantity.Create(eumItem.eumIIntegerCode, eumUnit.eumUintCode),
        DfsSimpleType.Float,
        DataValueType.Instantaneous,
    )
    # The second x key is past the 4 cells along x
    builder.SetEncodingKey([0, 4], [0, 0], [0, 0])

    errors = builder.Validate(dieOnError=False)

    assert errors == [
        "Encode key values are not valid for axis of dynamic item number 1"
    ]


def test_static_item_builder_reports_missing_data_and_axis():
    errors = DfsStaticItemBuilder().Validate()

    assert "Spatial axis has not been set." in errors
    assert "Data has not been set." in errors


def test_delete_value_double_is_written(landuse: DfsBuilder, tmp_path):
    landuse.DeleteValueDouble = -7.5
    landuse.CreateFile(str(tmp_path / "deletevalue.dfs2"))
    file = landuse.GetFile()

    assert -7.5 == file.FileInfo.DeleteValueDouble
    file.Close()


@pytest.mark.parametrize("itemNumber, timestepIndex", [(2, 0), (1, 1)])
def test_first_write_to_created_file_must_be_first_item_timestep(
    landuse: DfsBuilder, tmp_path, itemNumber, timestepIndex
):
    landuse.AddCreateDynamicItem(
        "Second",
        eumQuantity.Create(eumItem.eumIIntegerCode, eumUnit.eumUintCode),
        DfsSimpleType.Float,
        DataValueType.Instantaneous,
    )
    landuse.CreateFile(str(tmp_path / "firstwrite.dfs2"))
    file = landuse.GetFile()
    data = np.zeros(62 * 70, dtype=np.float32)

    with pytest.raises(Exception, match="No dynamic items have been written"):
        file.WriteItemTimeStep(itemNumber, timestepIndex, 0, data)
    file.Close()


def test_static_item_builder_reports_data_not_matching_axis():
    builder = DfsStaticItemBuilder()
    builder.Set(
        "Static",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    builder.SetAxis(DfsFactory().CreateAxisEqD1(eumUnit.eumUmeter, 3, 0, 1))
    builder.SetData(np.array([1.0, 2.0], dtype=np.float32))

    errors = builder.Validate()

    assert ["Size of data (2) does not match spatial axis size (3)."] == errors


def _dfs0_with_associated_static_item(staticItemNumber):
    factory = DfsFactory()
    builder = DfsBuilder.Create("title", "application", 1)
    builder.SetDataType(0)
    builder.SetGeographicalProjection(factory.CreateProjectionUndefined())
    builder.SetTemporalAxis(factory.CreateTemporalEqTimeAxis(eumUnit.eumUsec, 0, 1))
    item = builder.CreateDynamicItemBuilder()
    item.Set(
        "Value",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    item.SetValueType(DataValueType.Instantaneous)
    item.SetAxis(factory.CreateAxisEqD0())
    item.SetAssociatedStaticItem(staticItemNumber)
    builder.AddDynamicItem(item.GetDynamicItemInfo())
    return builder


def test_associated_static_item_number_is_checked(tmp_path):
    # mikecore does not read associated static items back; the native
    # library checks the number when the file is created
    builder = _dfs0_with_associated_static_item(1)
    builder.CreateFile(str(tmp_path / "associated.dfs0"))
    builder.GetFile().Close()

    builder = _dfs0_with_associated_static_item(-1)
    with pytest.raises(Exception, match="An item number is out of range"):
        builder.CreateFile(str(tmp_path / "invalid.dfs0"))


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Suspected bug: GetDynamicItemInfo replaces ItemInfo with a blank "
        "DfsDynamicItemInfo but leaves the builder's 'is set' flags True. A reused "
        "builder then passes Validate and returns an item with an empty name, no "
        "quantity and no ValueType, which fails later when added to a file. Its "
        "comment says it means to store a clone so the builder can be reused. "
        "Correct: the second item keeps the name, quantity and value type set "
        "before the first GetDynamicItemInfo call."
    ),
)
def test_dynamic_item_builder_can_be_reused():
    factory = DfsFactory()
    quantity = eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUmeter)
    item = DfsBuilder.Create().CreateDynamicItemBuilder()
    item.Set("Value", quantity, DfsSimpleType.Float)
    item.SetValueType(DataValueType.Instantaneous)
    item.SetAxis(factory.CreateAxisEqD0())
    first = item.GetDynamicItemInfo()

    item.SetAxis(factory.CreateAxisEqD0())
    second = item.GetDynamicItemInfo()

    assert first is not second
    assert "Value" == second.Name
    assert second.Quantity is not None
    assert eumItem.eumIWaterLevel == second.Quantity.Item
    assert eumUnit.eumUmeter == second.Quantity.Unit
    assert DataValueType.Instantaneous == second.ValueType
