import datetime

import numpy as np
from numpy.testing import assert_array_equal

from mikecore.DfsFactory import DfsFactory
from mikecore.DfsuBuilder import DfsuBuilder
from mikecore.DfsuFile import DfsuFile, DfsuFileType
from mikecore.eum import eumItem, eumQuantity, eumUnit

# Two triangles over four nodes
X = np.array([0.0, 1.0, 1.0, 0.0])
Y = np.array([0.0, 0.0, 1.0, 1.0])
Z = np.array([-1.0, -2.0, -3.0, -4.0])
CODE = np.array([1, 1, 1, 1])
ELEMENTS = [[1, 2, 3], [1, 3, 4]]


def _builder(fileType=DfsuFileType.Dfsu2D):
    builder = DfsuBuilder.Create(fileType)
    builder.SetProjection(DfsFactory().CreateProjection("NON-UTM"))
    builder.SetTimeInfo(datetime.datetime(2020, 1, 1), 60)
    builder.AddDynamicItem(
        "Value", eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined)
    )
    return builder


def test_node_ids_set_after_nodes_are_written():
    filename = "testdata/testtmp/test_dfsu_builder_nodeids_after.dfsu"
    builder = _builder()
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetNodeIds(np.array([11, 12, 13, 14], dtype=np.int32))
    builder.SetElements(ELEMENTS)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert_array_equal([11, 12, 13, 14], dfsu.NodeIds)
    dfsu.Close()


def test_node_ids_set_before_nodes_are_written():
    filename = "testdata/testtmp/test_dfsu_builder_nodeids_before.dfsu"
    builder = _builder()
    builder.SetNodeIds(np.array([11, 12, 13, 14], dtype=np.int32))
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert_array_equal([11, 12, 13, 14], dfsu.NodeIds)
    dfsu.Close()


def test_validate_reports_missing_nodes_and_elements():
    builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D)

    errors = builder.Validate()

    assert "Nodes have not been set" in errors
    assert "Elements have not been set" in errors


def test_spectral_file_with_directions_only():
    filename = "testdata/testtmp/test_dfsu_builder_directions_only.dfsu"
    directions = np.array([0.0, np.pi / 2, np.pi, 3 * np.pi / 2])
    builder = _builder(DfsuFileType.DfsuSpectral2D)
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.SetDirections(directions)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert 0 == dfsu.NumberOfFrequencies
    assert_array_equal(directions, dfsu.Directions)
    dfsu.Close()
