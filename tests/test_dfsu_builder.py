import datetime

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from mikecore.DfsFactory import DfsFactory
from mikecore.DfsuBuilder import DfsuBuilder
from mikecore.DfsuFile import DfsuFile, DfsuFileType
from mikecore.eum import eumItem, eumQuantity, eumUnit
from mikecore.MeshFile import MeshFile

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


def test_default_node_and_element_ids_count_from_one(tmp_path):
    filename = str(tmp_path / "default_ids.dfsu")
    builder = _builder()
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert_array_equal([1, 2, 3, 4], dfsu.NodeIds)
    assert_array_equal([1, 2], dfsu.ElementIds)
    dfsu.Close()


@pytest.mark.parametrize("nodeNumber", [0, 5])
def test_validate_reports_node_number_outside_the_nodes(nodeNumber):
    builder = _builder()
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements([[1, 2, 3], [1, 3, nodeNumber]])

    errors = builder.Validate()

    assert [
        "At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]"
    ] == errors


def test_validate_accepts_highest_node_number():
    builder = _builder()
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)

    assert [] == builder.Validate()


def test_create_file_without_nodes_or_elements_fails(tmp_path):
    builder = _builder()

    with pytest.raises(Exception) as error:
        builder.CreateFile(str(tmp_path / "empty.dfsu"))

    assert "Nodes have not been set" in str(error.value)
    assert "Elements have not been set" in str(error.value)


def test_setup_before_nodes_and_elements_fails():
    builder = _builder()

    with pytest.raises(Exception, match="Nodes and elements must be set"):
        builder.SetupConnectivityArrays()


def test_node_ids_must_match_number_of_nodes():
    builder = _builder()
    builder.SetNodes(X, Y, Z, CODE)

    with pytest.raises(Exception, match="does not match number of nodes"):
        builder.SetNodeIds(np.array([1, 2, 3], dtype=np.int32))


def test_nodes_must_match_number_of_node_ids():
    builder = _builder()
    builder.SetNodeIds(np.array([1, 2, 3], dtype=np.int32))

    with pytest.raises(Exception, match="same length as the number of node ids"):
        builder.SetNodes(X, Y, Z, CODE)


def test_elements_must_match_element_ids_from_mesh_file():
    builder = _builder()
    builder.SetFromMeshFile(MeshFile.ReadMesh("testdata/Oresund.mesh"))

    with pytest.raises(Exception, match="not the same as number of element ids"):
        builder.SetElements(ELEMENTS)


def test_set_from_mesh_file_writes_the_mesh(tmp_path):
    filename = str(tmp_path / "from_mesh.dfsu")
    mesh = MeshFile.ReadMesh("testdata/Oresund.mesh")
    builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D)
    builder.SetFromMeshFile(mesh)
    builder.SetTimeInfo(datetime.datetime(2020, 1, 1), 60)
    builder.AddDynamicItem(
        "Value", eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined)
    )
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert "UTM-33" == dfsu.Projection.WKTString
    assert_array_equal(mesh.NodeIds, dfsu.NodeIds)
    assert_array_equal(mesh.X, dfsu.X)
    assert_array_equal(mesh.Y, dfsu.Y)
    z = mesh.Z
    assert z is not None
    assert_array_equal(z.astype(np.float32), dfsu.Z)
    assert_array_equal(mesh.Code, dfsu.Code)
    assert_array_equal(mesh.ElementIds, dfsu.ElementIds)
    assert len(mesh.ElementTable) == len(dfsu.ElementTable)
    for meshElement, dfsuElement in zip(mesh.ElementTable, dfsu.ElementTable):
        assert_array_equal(meshElement, dfsuElement)
    dfsu.Close()


FREQUENCIES = np.array([0.1, 0.2, 0.3])
DIRECTIONS = np.array([0.0, np.pi / 2, np.pi, 3 * np.pi / 2])


def test_spectral_file_with_frequencies_and_directions(tmp_path):
    filename = str(tmp_path / "spectral2d.dfsu")
    builder = _builder(DfsuFileType.DfsuSpectral2D)
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.SetFrequencies(FREQUENCIES)
    builder.SetDirections(DIRECTIONS)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert DfsuFileType.DfsuSpectral2D is dfsu.DfsuFileType
    # The value of the MIKE Core DfsuFileType enum
    assert 10 == dfsu.DfsuFileType
    assert_array_equal(FREQUENCIES, dfsu.Frequencies)
    assert_array_equal(DIRECTIONS, dfsu.Directions)
    # One value per element, frequency and direction
    assert 2 * 3 * 4 == dfsu.ItemInfo[0].ElementCount
    dfsu.Close()


def test_spectral_file_with_frequencies_only(tmp_path):
    filename = str(tmp_path / "frequencies_only.dfsu")
    builder = _builder(DfsuFileType.DfsuSpectral2D)
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.SetFrequencies(FREQUENCIES)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert_array_equal(FREQUENCIES, dfsu.Frequencies)
    assert 0 == dfsu.NumberOfDirections
    # One value per element and frequency
    assert 2 * 3 == dfsu.ItemInfo[0].ElementCount
    dfsu.Close()


def test_spectral_1d_file_has_values_per_node(tmp_path):
    filename = str(tmp_path / "spectral1d.dfsu")
    builder = _builder(DfsuFileType.DfsuSpectral1D)
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements([[1, 2], [2, 3], [3, 4]])
    builder.SetFrequencies(FREQUENCIES)
    builder.SetDirections(DIRECTIONS)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert DfsuFileType.DfsuSpectral1D is dfsu.DfsuFileType
    # The value of the MIKE Core DfsuFileType enum
    assert 9 == dfsu.DfsuFileType
    # One value per node, frequency and direction
    assert 4 * 3 * 4 == dfsu.ItemInfo[0].ElementCount
    dfsu.Close()


def test_temporal_axis_is_written(tmp_path):
    filename = str(tmp_path / "temporal_axis.dfsu")
    builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D)
    builder.SetProjection(DfsFactory().CreateProjection("NON-UTM"))
    builder.SetTemporalAxis(
        DfsFactory().CreateTemporalEqCalendarAxis(
            eumUnit.eumUsec, datetime.datetime(2021, 2, 3, 4, 5, 6), 0, 30
        )
    )
    builder.AddDynamicItem(
        "Value", eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined)
    )
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.CreateFile(filename).Close()

    dfsu = DfsuFile.Open(filename)
    assert datetime.datetime(2021, 2, 3, 4, 5, 6) == dfsu.StartDateTime
    assert 30 == dfsu.TimeStepInSeconds
    dfsu.Close()
