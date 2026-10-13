"""
Editing the item info and spatial axes of an existing dfs file, on every dfs
file type and every way of opening it for editing.
"""

import os
import shutil
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

from mikecore.DfsBuilder import DataValueType, DfsBuilder, DfsSimpleType
from mikecore.DfsFactory import DfsFactory
from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.eum import eumItem, eumQuantity, eumUnit


@dataclass
class DfsType:
    source: str
    open: Callable[[str], Any]
    openEdit: Callable[[str], Any]
    openAppend: Callable[[str], Any]
    # Encoded files store their data compressed, so the dynamic values are not
    # the raw bytes at the end of the file
    encoded: bool = False


def createDfs1(filename):
    # There is no dfs1 file in testdata, so the tests create one
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
    builder.CreateFile(filename)
    builder.AddCreateStaticItem(
        "Bathymetry",
        eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter),
        np.arange(5, dtype=np.float32),
        factory.CreateAxisEqD1(eumUnit.eumUmeter, 5, 0, 10),
    )
    file = builder.GetFile()
    for timeStep in range(3):
        for itemNumber in (1, 2):
            data = np.arange(5, dtype=np.float32) + 10 * timeStep + itemNumber
            file.WriteItemTimeStepNext(60.0 * timeStep, data)
    file.Close()


F = DfsFileFactory
DFS_TYPES = {
    "dfs0": DfsType(
        "testdata/TemporalEqTime.dfs0",
        F.DfsGenericOpen,
        F.DfsGenericOpenEdit,
        F.DfsGenericOpenAppend,
    ),
    "dfs1": DfsType("", F.Dfs1FileOpen, F.Dfs1FileOpenEdit, F.Dfs1FileOpenAppend),
    "dfs2": DfsType(
        "testdata/OresundHD.dfs2",
        F.Dfs2FileOpen,
        F.Dfs2FileOpenEdit,
        F.Dfs2FileOpenAppend,
    ),
    "dfs3": DfsType(
        "testdata/OresundHD.dfs3",
        F.Dfs3FileOpen,
        F.Dfs3FileOpenEdit,
        F.Dfs3FileOpenAppend,
        encoded=True,
    ),
    "dfsu": DfsType(
        "testdata/OresundHD.dfsu",
        F.DfsuFileOpen,
        F.DfsuFileOpenEdit,
        F.DfsuFileOpenAppend,
    ),
}
FILE_AXIS_TYPES = ["dfs1", "dfs2", "dfs3"]


@dataclass
class Case:
    filename: str
    dfsType: DfsType


@pytest.fixture(params=list(DFS_TYPES))
def case(request, tmp_path):
    return makeCase(request.param, tmp_path)


@pytest.fixture(params=FILE_AXIS_TYPES)
def fileAxisCase(request, tmp_path):
    return makeCase(request.param, tmp_path)


def makeCase(typeName, tmp_path):
    dfsType = DFS_TYPES[typeName]
    filename = str(tmp_path / ("test." + typeName))
    if dfsType.source:
        shutil.copyfile(dfsType.source, filename)
        os.chmod(filename, 0o644)
    else:
        createDfs1(filename)
    return Case(filename, dfsType)


# Every way to open a file for editing: Edit and Append mode through the
# factory method of the file type, and Edit mode as a generic dfs file
OPENERS = {
    "edit": lambda case: case.dfsType.openEdit(case.filename),
    "append": lambda case: case.dfsType.openAppend(case.filename),
    "generic": lambda case: DfsFileFactory.DfsGenericOpenEdit(case.filename),
}

AXIS_ATTRIBUTES = ("AxisUnit", "X0", "Dx", "Y0", "Dy", "Z0", "Dz")


def axisValues(axis):
    return {
        name: getattr(axis, name) for name in AXIS_ATTRIBUTES if hasattr(axis, name)
    }


def itemValues(itemInfo):
    return (
        itemInfo.Name,
        itemInfo.Quantity.Item,
        itemInfo.Quantity.Unit,
        axisValues(itemInfo.SpatialAxis),
    )


def readItems(filename):
    file = DfsFileFactory.DfsGenericOpen(filename)
    items = [itemValues(itemInfo) for itemInfo in file.ItemInfo]
    file.Close()
    return items


def readStaticItems(filename):
    file = DfsFileFactory.DfsGenericOpen(filename)
    staticItems = []
    while (staticItem := file.ReadStaticItemNext()) is not None:
        axis = staticItem.SpatialAxis
        assert axis is not None
        staticItems.append(
            (staticItem.Name, axis.AxisType, axisValues(axis), staticItem.Data)
        )
    file.Close()
    return staticItems


def readDynamicData(filename):
    file = DfsFileFactory.DfsGenericOpen(filename)
    data = []
    while (itemData := file.ReadItemTimeStepNext()) is not None:
        data.append((itemData.Time, itemData.Data.copy()))
    file.Close()
    return data


def dynamicDataBytes(filename):
    """Size of the raw values of all item time steps, from the header."""
    file = DfsFileFactory.DfsGenericOpen(filename)
    timeAxis = file.FileInfo.TimeAxis
    assert timeAxis is not None
    timeSteps = timeAxis.NumberOfTimeSteps
    valueBytes = {DfsSimpleType.Float: 4, DfsSimpleType.Double: 8}
    itemBytes = [
        itemInfo.ElementCount * valueBytes[itemInfo.DataType]
        for itemInfo in file.ItemInfo
    ]
    file.Close()
    return timeSteps * sum(itemBytes)


def readBytes(filename):
    with open(filename, "rb") as f:
        return f.read()


def assertOnlyHeaderChanged(case, before):
    """
    The edit changed only bytes in front of the data: the file keeps its size,
    and every dynamic value, read raw from the end of the file and through the
    reader, is unchanged.
    """
    after = readBytes(case.filename)
    assert len(before) == len(after)
    if not case.dfsType.encoded:
        dataBytes = dynamicDataBytes(case.filename)
        assert 0 < dataBytes < len(before)
        assert before[-dataBytes:] == after[-dataBytes:]


# Values that differ from those of every item in the test files
NEW_QUANTITY = (eumItem.eumIAreaFraction, eumUnit.eumUPerCent)
NEW_AXIS_UNIT = eumUnit.eumUfeet
NEW_X0 = 55.0


def editName(itemInfo):
    itemInfo.Name = "Q" * len(itemInfo.Name)


def editQuantity(itemInfo):
    itemInfo.Quantity = eumQuantity(*NEW_QUANTITY)


def editAxisUnit(itemInfo):
    itemInfo.SpatialAxis.AxisUnit = NEW_AXIS_UNIT


def editX0(itemInfo):
    if not hasattr(itemInfo.SpatialAxis, "X0"):
        pytest.skip("the axis of a dfs0 item has no origin")
    itemInfo.SpatialAxis.X0 = NEW_X0


def expectName(values):
    name, item, unit, axis = values
    return ("Q" * len(name), item, unit, axis)


def expectQuantity(values):
    name, _, _, axis = values
    return (name, *NEW_QUANTITY, axis)


def expectAxisUnit(values):
    name, item, unit, axis = values
    return (name, item, unit, {**axis, "AxisUnit": NEW_AXIS_UNIT})


def expectX0(values):
    name, item, unit, axis = values
    return (name, item, unit, {**axis, "X0": NEW_X0})


EDITS = {
    "name": (editName, expectName),
    "quantity": (editQuantity, expectQuantity),
    "axisunit": (editAxisUnit, expectAxisUnit),
    "x0": (editX0, expectX0),
}


@pytest.mark.parametrize("opener", list(OPENERS))
@pytest.mark.parametrize("edit", list(EDITS))
def test_edit_each_item(case, opener, edit):
    """
    Editing one item writes that value to that item only, and leaves the
    other items and all data unchanged. Checked for each item of the file.
    """
    editItem, expectItem = EDITS[edit]
    staticItems = readStaticItems(case.filename)
    dynamicData = readDynamicData(case.filename)
    expected = readItems(case.filename)
    assert len(expected) > 1

    for itemNo in range(len(expected)):
        before = readBytes(case.filename)
        file = OPENERS[opener](case)
        editItem(file.ItemInfo[itemNo])
        file.Close()

        expected[itemNo] = expectItem(expected[itemNo])
        assert expected == readItems(case.filename)
        assertOnlyHeaderChanged(case, before)

    for staticItem, newStaticItem in zip(
        staticItems, readStaticItems(case.filename), strict=True
    ):
        assert staticItem[:3] == newStaticItem[:3]
        np.testing.assert_array_equal(staticItem[3], newStaticItem[3])
    for (time, data), (newTime, newData) in zip(
        dynamicData, readDynamicData(case.filename), strict=True
    ):
        assert time == newTime
        np.testing.assert_array_equal(data, newData)


@pytest.mark.parametrize(
    "length",
    [
        pytest.param(lambda old: 0, id="empty"),
        pytest.param(lambda old: 1, id="one"),
        pytest.param(lambda old: old - 1, id="shorter"),
        pytest.param(lambda old: old, id="same"),
        pytest.param(lambda old: old + 5, id="longer"),
    ],
)
def test_name_keeps_its_length_in_the_file(case, length):
    """
    As in the C# library, a new name takes the place of the old one in the
    file: it is padded with spaces or truncated to the old length.
    """
    original = readBytes(case.filename)
    oldName = readItems(case.filename)[0][0]
    # The old name, null terminated, is stored once in the file
    oldBytes = oldName.encode("cp1252") + b"\0"
    assert original.count(oldBytes) == 1
    offset = original.index(oldBytes)
    newName = ("Ab" * len(oldName))[: length(len(oldName))]

    file = case.dfsType.openEdit(case.filename)
    file.ItemInfo[0].Name = newName
    nameInMemory = file.ItemInfo[0].Name
    file.Close()

    after = readBytes(case.filename)
    written = after[offset : offset + len(oldBytes)]
    padded = newName.encode("cp1252")[: len(oldName)].ljust(len(oldName), b" ")
    assert padded + b"\0" == written
    # The item shows the name the file holds
    assert padded.decode("cp1252") == nameInMemory
    assert padded.decode("cp1252") == readItems(case.filename)[0][0]
    assertOnlyHeaderChanged(case, original)


def setName(itemInfo):
    # Not in the cp1252 encoding of dfs names
    itemInfo.Name = "Ω"


def setMismatchedQuantity(itemInfo):
    # A unit of another dimension than the item
    itemInfo.Quantity = eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUPerCent)


def setNoQuantity(itemInfo):
    itemInfo.Quantity = None


def setAxisUnitNotUnit(itemInfo):
    itemInfo.SpatialAxis.AxisUnit = "abc"


@pytest.mark.parametrize(
    "setter, error",
    [
        (setName, UnicodeEncodeError),
        (setMismatchedQuantity, Exception),
        (setNoQuantity, AttributeError),
        (setAxisUnitNotUnit, AttributeError),
    ],
    ids=["name", "quantity", "noquantity", "axisunit"],
)
def test_rejected_value_keeps_old_value(case, setter, error):
    """A value the file cannot hold raises, and the item and file keep the old one."""
    original = readBytes(case.filename)

    file = case.dfsType.openEdit(case.filename)
    itemInfo = file.ItemInfo[0]
    values = itemValues(itemInfo)
    with pytest.raises(error):
        setter(itemInfo)
    assert values == itemValues(itemInfo)
    file.Close()

    assert original == readBytes(case.filename)


def editEverything(file):
    for itemInfo in file.ItemInfo:
        itemInfo.Name = "abc"
        itemInfo.Quantity = eumQuantity(*NEW_QUANTITY)
        itemInfo.SpatialAxis.AxisUnit = NEW_AXIS_UNIT
    spatialAxis = getattr(file, "SpatialAxis", None)
    if spatialAxis is not None:
        spatialAxis.X0 = NEW_X0


def test_read_mode_writes_nothing(case):
    original = readBytes(case.filename)

    file = case.dfsType.open(case.filename)
    editEverything(file)
    # In Read mode the name is not fitted to the length in the file
    assert "abc" == file.ItemInfo[0].Name
    file.Close()

    assert original == readBytes(case.filename)


def test_edit_after_close_writes_nothing(case):
    original = readBytes(case.filename)

    file = case.dfsType.openEdit(case.filename)
    file.Close()
    editEverything(file)
    assert "abc" == file.ItemInfo[0].Name
    with pytest.raises(OSError):
        file.Flush()

    assert original == readBytes(case.filename)


def test_quantity_changed_in_place_is_not_written(case):
    """As in the C# library, only assigning a new Quantity writes it."""
    original = readBytes(case.filename)

    file = case.dfsType.openEdit(case.filename)
    for itemInfo in file.ItemInfo:
        itemInfo.Quantity.Item = NEW_QUANTITY[0]
        itemInfo.Quantity.Unit = NEW_QUANTITY[1]
    file.Close()

    assert original == readBytes(case.filename)


def test_axis_attribute_the_axis_type_does_not_have(case):
    """It is set on the Python object, as on an axis not in an editable file."""
    original = readBytes(case.filename)

    file = case.dfsType.openEdit(case.filename)
    axis = file.ItemInfo[0].SpatialAxis
    missing = [name for name in AXIS_ATTRIBUTES if not hasattr(axis, name)]
    if not missing:
        pytest.skip("a dfs3 axis has every attribute")
    setattr(axis, missing[0], 1.0)
    assert 1.0 == getattr(axis, missing[0])
    file.Close()

    assert original == readBytes(case.filename)


def test_flush_then_append(case):
    """
    Changes written on Flush do not move the file pointer: a time step
    appended after Flush is added at the end, and the edits are kept.
    """
    dynamicData = readDynamicData(case.filename)
    items = readItems(case.filename)

    file = case.dfsType.openAppend(case.filename)
    file.ItemInfo[0].Name = "Q" * len(items[0][0])
    spatialAxis = getattr(file, "SpatialAxis", None)
    if spatialAxis is not None:
        spatialAxis.X0 = NEW_X0
    file.Flush()
    # A copy of the last time step, which differs from the first, and which
    # an encoded file stores as it is
    appended = [data for _, data in dynamicData[-len(items) :]]
    assert not np.array_equal(appended[0], dynamicData[0][1])
    for data in appended:
        file.WriteItemTimeStepNext(0.0, data)
    file.Close()

    newData = readDynamicData(case.filename)
    assert len(dynamicData) + len(items) == len(newData)
    for (_, data), (_, newDataValues) in zip(dynamicData, newData, strict=False):
        np.testing.assert_array_equal(data, newDataValues)
    for data, (_, newDataValues) in zip(
        appended, newData[len(dynamicData) :], strict=True
    ):
        np.testing.assert_array_equal(data, newDataValues)
    newItems = readItems(case.filename)
    assert "Q" * len(items[0][0]) == newItems[0][0]
    if spatialAxis is not None:
        assert all(axis["X0"] == NEW_X0 for _, _, _, axis in newItems)


def test_file_axis_is_written_to_every_item(fileAxisCase):
    """
    Changing the axis of a dfs1, dfs2 or dfs3 file writes it to every dynamic
    item and to every static item with that type of axis, and keeps the data.
    """
    case = fileAxisCase
    original = readBytes(case.filename)
    staticItems = readStaticItems(case.filename)
    dynamicData = readDynamicData(case.filename)

    file = case.dfsType.openEdit(case.filename)
    axisType = file.SpatialAxis.AxisType
    newValues = axisValues(file.SpatialAxis)
    for name, value in axisValues(file.SpatialAxis).items():
        if name != "AxisUnit":
            newValues[name] = value + 5
            setattr(file.SpatialAxis, name, value + 5)
    file.Close()

    for _, _, _, axis in readItems(case.filename):
        assert newValues == axis
    assert axisType in [staticAxisType for _, staticAxisType, _, _ in staticItems]
    for (name, staticAxisType, axis, data), (newName, _, newAxis, newData) in zip(
        staticItems, readStaticItems(case.filename), strict=True
    ):
        assert name == newName
        assert (newValues if staticAxisType == axisType else axis) == newAxis
        np.testing.assert_array_equal(data, newData)
    for (_, data), (_, newData) in zip(
        dynamicData, readDynamicData(case.filename), strict=True
    ):
        np.testing.assert_array_equal(data, newData)
    assertOnlyHeaderChanged(case, original)
