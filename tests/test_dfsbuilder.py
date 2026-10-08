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
    with pytest.raises(Exception):
        builder.GetFile()


def test_getfiletwice_not_allowed(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    file = builder.GetFile()

    with pytest.raises(Exception):
        builder.GetFile()


def test_filetitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    file = builder.GetFile()

    with pytest.raises(Exception):
        builder.SetFileTitle("too late")


def test_apptitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    file = builder.GetFile()

    with pytest.raises(Exception):
        builder.SetApplicationTitle("too late")


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
