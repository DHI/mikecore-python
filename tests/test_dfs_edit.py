"""Editing item names and quantities, on every dfs file type and edit mode."""

import copy
import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
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
    open: Callable[[Path], Any]
    openEdit: Callable[[Path], Any]
    openAppend: Callable[[Path], Any]


def createDfs1(filename):
    # testdata has no dfs1 file
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
    ),
    "dfsu": DfsType(
        "testdata/OresundHD.dfsu",
        F.DfsuFileOpen,
        F.DfsuFileOpenEdit,
        F.DfsuFileOpenAppend,
    ),
}


@dataclass
class Case:
    path: Path
    dfsType: DfsType


@pytest.fixture(params=list(DFS_TYPES))
def case(request, tmp_path):
    dfsType = DFS_TYPES[request.param]
    path = tmp_path / ("test." + request.param)
    if dfsType.source:
        shutil.copyfile(dfsType.source, path)
        os.chmod(path, 0o644)
    else:
        createDfs1(str(path))
    return Case(path, dfsType)


OPENERS = {
    "edit": lambda case: case.dfsType.openEdit(case.path),
    "append": lambda case: case.dfsType.openAppend(case.path),
    "generic": lambda case: DfsFileFactory.DfsGenericOpenEdit(case.path),
}

# Differs from the quantity of every item in the test files
NEW_ITEM = eumItem.eumIAreaFraction
NEW_UNIT = eumUnit.eumUPerCent


def readItems(path):
    """(Name, eumItem, eumUnit) of each item."""
    file = DfsFileFactory.DfsGenericOpen(path)
    items = [
        (itemInfo.Name, itemInfo.Quantity.Item, itemInfo.Quantity.Unit)
        for itemInfo in file.ItemInfo
    ]
    file.Close()
    return items


def readDynamicData(path):
    """(time, data) of every item time step."""
    file = DfsFileFactory.DfsGenericOpen(path)
    data = []
    while (itemData := file.ReadItemTimeStepNext()) is not None:
        data.append((itemData.Time, itemData.Data.copy()))
    file.Close()
    return data


def firstNameInFile(path):
    """The first item's name, its NUL-terminated bytes and their offset."""
    content = path.read_bytes()
    name = readItems(path)[0][0]
    nameBytes = name.encode("cp1252") + b"\0"
    assert content.count(nameBytes) == 1
    return name, nameBytes, content.index(nameBytes)


@pytest.mark.parametrize("opener", list(OPENERS))
def test_name_edit_is_written_to_that_item_only(case, opener):
    data = readDynamicData(case.path)
    expected = readItems(case.path)
    # Another item is needed to check it stays unchanged
    assert len(expected) > 1

    for itemNo, (name, item, unit) in enumerate(readItems(case.path)):
        file = OPENERS[opener](case)
        file.ItemInfo[itemNo].Name = "Q" * len(name)
        file.Close()

        expected[itemNo] = ("Q" * len(name), item, unit)
        assert expected == readItems(case.path)
    np.testing.assert_equal(data, readDynamicData(case.path))


@pytest.mark.parametrize("opener", list(OPENERS))
def test_quantity_edit_is_written_to_that_item_only(case, opener):
    data = readDynamicData(case.path)
    expected = readItems(case.path)
    # Another item is needed to check it stays unchanged
    assert len(expected) > 1

    for itemNo, (name, _, _) in enumerate(readItems(case.path)):
        file = OPENERS[opener](case)
        file.ItemInfo[itemNo].Quantity = eumQuantity(NEW_ITEM, NEW_UNIT)
        file.Close()

        expected[itemNo] = (name, NEW_ITEM, NEW_UNIT)
        assert expected == readItems(case.path)
    np.testing.assert_equal(data, readDynamicData(case.path))


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
    """As in the C# library, a new name is padded or truncated to the old length."""
    data = readDynamicData(case.path)
    oldName, oldBytes, offset = firstNameInFile(case.path)
    newName = ("Ab" * len(oldName))[: length(len(oldName))]

    file = case.dfsType.openEdit(case.path)
    itemInfo = file.ItemInfo[0]
    itemInfo.Name = newName
    file.Close()

    expected = newName[: len(oldName)].ljust(len(oldName))
    written = case.path.read_bytes()[offset : offset + len(oldBytes)]
    assert expected.encode("cp1252") + b"\0" == written
    assert expected == itemInfo.Name
    assert expected == readItems(case.path)[0][0]
    np.testing.assert_equal(data, readDynamicData(case.path))


@pytest.mark.parametrize(
    "attribute, value, error",
    [
        pytest.param("Name", "Ω", UnicodeEncodeError, id="not-cp1252"),
        pytest.param("Name", "A\0B", ValueError, id="nul"),
        pytest.param(
            "Quantity",
            eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUPerCent),
            ValueError,
            id="unit-of-another-item",
        ),
    ],
)
@pytest.mark.parametrize("closeWith", ["flush", "close"])
def test_rejected_value_changes_no_item(case, attribute, value, error, closeWith):
    """
    A rejected value raises before anything is written, so the valid edit of
    item 0 is not written either. Close still closes the file.
    """
    original = case.path.read_bytes()

    file = case.dfsType.openEdit(case.path)
    file.ItemInfo[0].Quantity = eumQuantity(NEW_ITEM, NEW_UNIT)
    setattr(file.ItemInfo[1], attribute, value)
    if closeWith == "flush":
        with pytest.raises(error):
            file.Flush()
    with pytest.raises(error):
        file.Close()
    with pytest.raises(OSError):
        file.Flush()

    assert original == case.path.read_bytes()


def test_read_mode_writes_nothing(case):
    original = case.path.read_bytes()

    file = case.dfsType.open(case.path)
    for itemInfo in file.ItemInfo:
        itemInfo.Name = "abc"
        itemInfo.Quantity = eumQuantity(NEW_ITEM, NEW_UNIT)
    file.Close()

    # Not fitted to the stored length
    assert "abc" == file.ItemInfo[0].Name
    assert original == case.path.read_bytes()


def test_edit_after_close_writes_nothing(case):
    original = case.path.read_bytes()

    file = case.dfsType.openEdit(case.path)
    file.Close()
    for itemInfo in file.ItemInfo:
        itemInfo.Name = "abc"
        itemInfo.Quantity = eumQuantity(NEW_ITEM, NEW_UNIT)
    file.Close()
    with pytest.raises(OSError):
        file.Flush()

    assert original == case.path.read_bytes()


def test_quantity_changed_in_place_is_not_written(case):
    """As in the C# library, only assigning a new Quantity writes it."""
    original = case.path.read_bytes()

    file = case.dfsType.openEdit(case.path)
    for itemInfo in file.ItemInfo:
        itemInfo.Quantity.Item = NEW_ITEM
        itemInfo.Quantity.Unit = NEW_UNIT
    file.Close()

    assert original == case.path.read_bytes()


def test_item_put_in_item_info_is_not_written(case):
    """Only items read from the file are written, not replacements."""
    original = case.path.read_bytes()

    file = case.dfsType.openEdit(case.path)
    itemInfo = copy.copy(file.ItemInfo[0])
    file.ItemInfo[0] = itemInfo
    itemInfo.Quantity = eumQuantity(NEW_ITEM, NEW_UNIT)
    file.Close()

    assert original == case.path.read_bytes()


def test_flush_then_append(case):
    """Writing item edits on Flush does not move the append position."""
    data = [values for _, values in readDynamicData(case.path)]
    items = readItems(case.path)
    name, item, unit = items[0]

    file = case.dfsType.openAppend(case.path)
    file.ItemInfo[0].Name = "Q" * len(name)
    file.Flush()
    # Differs from the first time step, so overwriting it would show
    appended = data[-len(items) :]
    assert not np.array_equal(appended[0], data[0])
    for values in appended:
        file.WriteItemTimeStepNext(0.0, values)
    file.Close()

    newData = [values for _, values in readDynamicData(case.path)]
    np.testing.assert_equal(data + appended, newData)
    assert [("Q" * len(name), item, unit), *items[1:]] == readItems(case.path)


def test_quantity_edit_keeps_a_name_cp1252_cannot_decode(case):
    """
    A Quantity-only edit writes back unchanged a name cp1252 cannot decode,
    such as UTF-8 from another tool.
    """
    _, oldBytes, offset = firstNameInFile(case.path)
    # 0x81 is undefined in cp1252
    nameBytes = b"\x81" + oldBytes[1:]
    with open(case.path, "r+b") as f:
        f.seek(offset)
        f.write(nameBytes)
    assert "�" == readItems(case.path)[0][0][0]
    data = readDynamicData(case.path)

    file = case.dfsType.openEdit(case.path)
    file.ItemInfo[0].Quantity = eumQuantity(NEW_ITEM, NEW_UNIT)
    file.Close()

    written = case.path.read_bytes()[offset : offset + len(nameBytes)]
    assert nameBytes == written
    assert (NEW_ITEM, NEW_UNIT) == readItems(case.path)[0][1:]
    np.testing.assert_equal(data, readDynamicData(case.path))


def test_flush_writes_the_edit_in_edit_mode(case):
    """Not Append mode: there the native library writes the header only on Close."""
    oldName, oldBytes, offset = firstNameInFile(case.path)

    file = case.dfsType.openEdit(case.path)
    file.ItemInfo[0].Name = "Q" * len(oldName)
    file.Flush()
    written = case.path.read_bytes()[offset : offset + len(oldBytes)]
    file.Close()

    assert ("Q" * len(oldName)).encode("cp1252") + b"\0" == written
