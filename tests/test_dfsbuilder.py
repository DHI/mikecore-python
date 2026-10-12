from datetime import datetime

import numpy as np
from numpy.testing import assert_array_equal
from mikecore.DfsBuilder import (
    DfsBuilder,
    DfsSimpleType,
    DataValueType,
    DfsStaticItemBuilder,
)
from mikecore.DfsFactory import DfsFactory
from mikecore.DfsFile import UnitConversionType
from mikecore.DfsFileFactory import DfsFileFactory
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
    landuse.GetFile()


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
    builder.GetFile()

    with pytest.raises(Exception, match="File has been returned"):
        builder.GetFile()


def test_filetitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    builder.GetFile()

    with pytest.raises(Exception, match="File has been returned"):
        builder.SetFileTitle("too late")


def test_apptitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
    builder = landuse

    # Create and get file
    builder.CreateFile(str(tmp_path / "notused.dfs2"))
    builder.GetFile()

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


def compressed_builder_for(axis):
    """A builder with one float item on the given spatial axis."""
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
    builder.SetSpatialAxis(axis)
    builder.AddCreateDynamicItem(
        "Item",
        eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
        DfsSimpleType.Float,
        DataValueType.Instantaneous,
    )
    return builder


@pytest.fixture(params=[1, 2, 3], ids=["dfs1", "dfs2", "dfs3"])
def compressed_builder(request):
    """A builder for 4 cells, a 4 x 3 grid or a 4 x 3 x 2 grid, ready for an encode key.

    Returns the builder and its cell counts along x, y and z. A dfs1 axis is
    one row and a dfs2 axis one layer, so their missing counts are 1.
    """
    dims = request.param
    factory = DfsFactory()
    unit = eumUnit.eumUmeter
    if dims == 1:
        axis = factory.CreateAxisEqD1(unit, 4, 0, 1)
    elif dims == 2:
        axis = factory.CreateAxisEqD2(unit, 4, 0, 1, 3, 0, 1)
    else:
        axis = factory.CreateAxisEqD3(unit, 4, 0, 1, 3, 0, 1, 2, 0, 1)
    counts = (4, 3, 2)[:dims] + (1,) * (3 - dims)
    return compressed_builder_for(axis), counts


def test_validate_accepts_encode_key_inside_axis(compressed_builder):
    builder, (nx, ny, nz) = compressed_builder
    # The first cell and the last cell of the grid
    builder.SetEncodingKey([0, nx - 1], [0, ny - 1], [0, nz - 1])

    assert builder.Validate(dieOnError=False) == []


@pytest.mark.parametrize("axis", ["x", "y", "z"])
def test_validate_reports_encode_key_outside_axis(compressed_builder, axis):
    builder, (nx, ny, nz) = compressed_builder
    # The second entry is one cell past the axis along x, y or z
    past = {"x": nx, "y": ny, "z": nz}
    key = {name: [0, past[name] if name == axis else 0] for name in past}
    builder.SetEncodingKey(key["x"], key["y"], key["z"])

    errors = builder.Validate(dieOnError=False)

    assert errors == [
        "Encode key values are not valid for axis of dynamic item number 1"
    ]


def test_compressed_file_stores_only_the_key_cells(compressed_builder, tmp_path):
    builder, (nx, ny, nz) = compressed_builder
    cells = nx * ny * nz
    # Keep the first cell and the last cell of the grid
    builder.SetEncodingKey(
        np.array([0, nx - 1], dtype=np.int32),
        np.array([0, ny - 1], dtype=np.int32),
        np.array([0, nz - 1], dtype=np.int32),
    )
    dims = builder.DynamicItems[0].SpatialAxis.Dimension
    filename = str(tmp_path / f"compressed.dfs{dims}")
    builder.CreateFile(filename)
    dfs = builder.GetFile()
    dfs.WriteItemTimeStepNext(0, np.arange(cells, dtype=np.float32))
    dfs.Close()

    dfs = DfsFileFactory.DfsGenericOpen(filename)
    item = dfs.ReadItemTimeStepNext()
    delete = dfs.FileInfo.DeleteValueFloat
    dfs.Close()

    assert item is not None
    assert item.Data[0] == 0
    assert item.Data[-1] == cells - 1
    assert np.all(item.Data[1:-1] == np.float32(delete))


def test_validate_ignores_encode_key_of_dfs0(tmp_path):
    builder = compressed_builder_for(DfsFactory().CreateAxisEqD0())
    # A dfs0 axis has a single value and no cells to key. The native library
    # ignores the key, so even one past the axis is accepted and does no harm.
    builder.SetEncodingKey(
        np.array([1], dtype=np.int32),
        np.array([0], dtype=np.int32),
        np.array([0], dtype=np.int32),
    )

    assert builder.Validate(dieOnError=False) == []

    filename = str(tmp_path / "compressed.dfs0")
    builder.CreateFile(filename)
    dfs = builder.GetFile()
    dfs.WriteItemTimeStepNext(0, np.array([7], dtype=np.float32))
    dfs.Close()

    dfs = DfsFileFactory.DfsGenericOpen(filename)
    item = dfs.ReadItemTimeStepNext()
    dfs.Close()

    assert item is not None
    assert item.Data.tolist() == [7]


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


def test_write_reports_data_shorter_than_item(landuse: DfsBuilder, tmp_path):
    landuse.CreateFile(str(tmp_path / "shortdata.dfs2"))
    file = landuse.GetFile()
    data = np.zeros(10, dtype=np.float32)

    with pytest.raises(
        Exception,
        match="Data is of wrong size. Item has 4340 elements, data is 10 long.",
    ):
        file.WriteItemTimeStepNext(0, data)
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


def test_reused_dynamic_item_builder_leaves_earlier_items_alone():
    factory = DfsFactory()
    item = DfsBuilder.Create().CreateDynamicItemBuilder()
    item.Set(
        "First",
        eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
        DfsSimpleType.Float,
    )
    item.SetValueType(DataValueType.Instantaneous)
    item.SetAxis(factory.CreateAxisEqD0())
    item.SetAssociatedStaticItem(1)
    first = item.GetDynamicItemInfo()

    item.Set(
        "Second",
        eumQuantity(eumItem.eumIWaterDepth, eumUnit.eumUfeet),
        DfsSimpleType.Double,
    )
    item.SetValueType(DataValueType.Accumulated)
    item.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 2, 0, 1))
    item.SetReferenceCoordinates(1, 2, 3)
    item.SetAssociatedStaticItem(2)
    second = item.GetDynamicItemInfo()

    assert "First" == first.Name
    assert first.Quantity is not None
    assert eumItem.eumIWaterLevel == first.Quantity.Item
    assert DfsSimpleType.Float == first.DataType
    assert DataValueType.Instantaneous == first.ValueType
    assert 1 == first.ElementCount
    assert np.float32(-1e-35) == first.ReferenceCoordinateX
    assert [1] == first.AssociatedStaticItemNumbers
    assert "Second" == second.Name
    assert DataValueType.Accumulated == second.ValueType
    assert 2 == second.ElementCount
    assert [1, 2] == second.AssociatedStaticItemNumbers


def test_reused_static_item_builder_leaves_earlier_items_alone():
    factory = DfsFactory()
    staticItem = DfsStaticItemBuilder()
    staticItem.Set(
        "First",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    staticItem.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 2, 0, 1))
    staticItem.SetData(np.array([1.0, 2.0], dtype=np.float32))
    first = staticItem.GetStaticItem()

    staticItem.Set(
        "Second",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    staticItem.SetReferenceCoordinates(5, 6, 7)
    data = staticItem.ItemInfo.Data
    assert data is not None
    data[0] = 10.0
    second = staticItem.GetStaticItem()

    assert first is not second
    assert "First" == first.Name
    assert np.float32(-1e-35) == first.ReferenceCoordinateX
    assert_array_equal([1.0, 2.0], first.Data)
    assert "Second" == second.Name
    assert 5 == second.ReferenceCoordinateX
    assert_array_equal([10.0, 2.0], second.Data)

    staticItem.SetData(np.array([3.0, 4.0], dtype=np.float32))
    third = staticItem.GetStaticItem()

    assert_array_equal([10.0, 2.0], second.Data)
    assert_array_equal([3.0, 4.0], third.Data)


def _dynamic_item_builder():
    factory = DfsFactory()
    builder = DfsBuilder.Create().CreateDynamicItemBuilder()
    builder.Set(
        "First",
        eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
        DfsSimpleType.Float,
    )
    builder.SetValueType(DataValueType.Instantaneous)
    builder.SetAxis(factory.CreateAxisEqD0())
    builder.SetAssociatedStaticItem(1)
    setters = [
        lambda: builder.SetValueType(DataValueType.Accumulated),
        lambda: builder.SetAssociatedStaticItem(2),
    ]
    return builder, builder.GetDynamicItemInfo, setters


def _static_item_builder():
    builder = DfsStaticItemBuilder()
    builder.Set(
        "First",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    builder.SetAxis(DfsFactory().CreateAxisEqD1(eumUnit.eumUmeter, 2, 0, 1))
    builder.SetData(np.array([1.0, 2.0], dtype=np.float32))

    def changeData():
        data = builder.ItemInfo.Data
        assert data is not None
        data[0] = 10.0

    setters = [
        lambda: builder.SetData(np.array([3.0, 4.0], dtype=np.float32)),
        changeData,
    ]
    return builder, builder.GetStaticItem, setters


# Every setter of either builder, then the getter again, must leave each
# attribute of the item returned first as the same object with the same contents
@pytest.mark.parametrize("makeBuilder", [_dynamic_item_builder, _static_item_builder])
def test_no_builder_setter_changes_a_returned_item(makeBuilder):
    factory = DfsFactory()
    builder, getItem, setters = makeBuilder()
    first = getItem()
    before = {
        name: (value, np.array(value) if isinstance(value, list | np.ndarray) else None)
        for name, value in vars(first).items()
    }

    builder.Set(
        "Second",
        eumQuantity(eumItem.eumIWaterDepth, eumUnit.eumUfeet),
        DfsSimpleType.Double,
    )
    builder.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 2, 0, 1))
    builder.SetReferenceCoordinates(1, 2, 3)
    builder.SetOrientation(4, 5, 6)
    builder.SetUnitConversion(UnitConversionType.UbgConversion, eumUnit.eumUfeet)
    builder.SetAxisUnitConversion(UnitConversionType.UbgConversion, eumUnit.eumUfeet)
    for setter in setters:
        setter()
    getItem()

    assert before.keys() == vars(first).keys()
    for name, (value, contents) in before.items():
        assert value is getattr(first, name), name
        if contents is not None:
            assert_array_equal(contents, value, err_msg=name)


def test_reference_coordinates_and_orientation_are_read_back(tmp_path):
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
    item.SetReferenceCoordinates(1.5, 2.5, 3.5)
    item.SetOrientation(10, 20, 30)
    builder.AddDynamicItem(item.GetDynamicItemInfo())
    filename = str(tmp_path / "refcoords.dfs0")
    builder.CreateFile(filename)
    staticItem = DfsStaticItemBuilder()
    staticItem.Set(
        "Static",
        eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined),
        DfsSimpleType.Float,
    )
    staticItem.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 2, 0, 1))
    staticItem.SetData(np.array([1.0, 2.0], dtype=np.float32))
    staticItem.SetReferenceCoordinates(5, 6, 7)
    staticItem.SetOrientation(8, 9, 10)
    builder.AddStaticItem(staticItem.GetStaticItem())
    builder.GetFile().Close()

    file = DfsFileFactory.DfsGenericOpen(filename)
    itemInfo = file.ItemInfo[0]
    staticItemInfo = file.ReadStaticItemNext()
    file.Close()

    assert staticItemInfo is not None

    assert (1.5, 2.5, 3.5) == (
        itemInfo.ReferenceCoordinateX,
        itemInfo.ReferenceCoordinateY,
        itemInfo.ReferenceCoordinateZ,
    )
    assert (10, 20, 30) == (
        itemInfo.OrientationAlpha,
        itemInfo.OrientationPhi,
        itemInfo.OrientationTheta,
    )
    assert (5, 6, 7) == (
        staticItemInfo.ReferenceCoordinateX,
        staticItemInfo.ReferenceCoordinateY,
        staticItemInfo.ReferenceCoordinateZ,
    )
    assert (8, 9, 10) == (
        staticItemInfo.OrientationAlpha,
        staticItemInfo.OrientationPhi,
        staticItemInfo.OrientationTheta,
    )
