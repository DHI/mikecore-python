import datetime
import unittest

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from mikecore.DfsuBuilder import DfsuBuilder
from mikecore.DfsuFile import DfsuFile, DfsuFileType
from mikecore.MeshFile import MeshFile
from mikecore.MeshBuilder import MeshBuilder
from mikecore.eum import *
from tests.test_util import *


class MeshTests(unittest.TestCase):
    def test_OresundMeshTest(self):

        filename = "testdata/Oresund.mesh"

        mesh = MeshFile.ReadMesh(filename)

        Assert.AreEqual(eumItem.eumIBathymetry, mesh.EumQuantity.Item)
        Assert.AreEqual(eumUnit.eumUmeter, mesh.EumQuantity.Unit)
        Assert.AreEqual("UTM-33", mesh.ProjectionString)
        Assert.AreEqual(2057, mesh.NumberOfNodes)
        Assert.AreEqual(3636, mesh.NumberOfElements)

        # ## 1 359862.97332797921 6206313.7132576201 -1.7859922534795478 1
        Assert.AreEqual(359862.97332797921, mesh.X[0])
        Assert.AreEqual(6206313.7132576201, mesh.Y[0])
        Assert.AreEqual(-1.7859922534795478, mesh.Z[0])
        Assert.AreEqual(1, mesh.Code[0])
        Assert.AreEqual(1, mesh.NodeIds[0])

        # ## 667 352184.12574449758 6173038.637708677 -11.379499679148227 0
        Assert.AreEqual(352184.12574449758, mesh.X[666])
        Assert.AreEqual(6173038.637708677, mesh.Y[666])
        Assert.AreEqual(-11.379499679148227, mesh.Z[666])
        Assert.AreEqual(0, mesh.Code[666])
        Assert.AreEqual(667, mesh.NodeIds[666])

        # ## 1 667 142 929
        Assert.AreEqual(667, mesh.ElementTable[0][0])
        Assert.AreEqual(142, mesh.ElementTable[0][1])
        Assert.AreEqual(929, mesh.ElementTable[0][2])
        Assert.AreEqual(1, mesh.ElementIds[0])
        Assert.AreEqual(21, mesh.ElementType[0])
        # ## 3636 1024 2057 1766
        Assert.AreEqual(1024, mesh.ElementTable[3635][0])
        Assert.AreEqual(2057, mesh.ElementTable[3635][1])
        Assert.AreEqual(1766, mesh.ElementTable[3635][2])
        Assert.AreEqual(3636, mesh.ElementIds[3635])
        Assert.AreEqual(21, mesh.ElementType[3635])


# Two triangles over four nodes
X = [0.0, 1.0, 1.0, 0.0]
Y = [0.0, 0.0, 1.0, 1.0]
Z = [-1.0, -2.0, -3.0, -4.0]
CODE = [1, 0, 0, 1]
ELEMENTS = [[1, 2, 3], [1, 3, 4]]


def test_MeshBuilder_mesh_is_written(tmp_path):
    filename = str(tmp_path / "built.mesh")
    builder = MeshBuilder()
    builder.SetProjection("NON-UTM")
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.CreateMesh().Write(filename)

    mesh = MeshFile.ReadMesh(filename)
    quantity = mesh.EumQuantity
    assert quantity is not None
    assert "NON-UTM" == mesh.ProjectionString
    assert eumItem.eumIBathymetry == quantity.Item
    assert eumUnit.eumUmeter == quantity.Unit
    assert_array_equal([1, 2, 3, 4], mesh.NodeIds)
    assert_array_equal(X, mesh.X)
    assert_array_equal(Y, mesh.Y)
    assert_array_equal(Z, mesh.Z)
    assert_array_equal(CODE, mesh.Code)
    assert_array_equal([1, 2], mesh.ElementIds)
    assert 2 == len(mesh.ElementTable)
    for expected, element in zip(ELEMENTS, mesh.ElementTable):
        assert_array_equal(expected, element)


def test_MeshBuilder_validate_reports_missing_values():
    errors = MeshBuilder().Validate()

    assert [
        "Projection has not been set",
        "Nodes have not been set",
        "Elements have not been set",
    ] == errors


def test_MeshBuilder_create_mesh_without_values_fails():
    with pytest.raises(Exception, match="Nodes have not been set"):
        MeshBuilder().CreateMesh()


def _mesh_builder_with_node_number(nodeNumber):
    builder = MeshBuilder()
    builder.SetProjection("NON-UTM")
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements([[1, 2, 3], [1, 3, nodeNumber]])
    return builder


@pytest.mark.parametrize("nodeNumber", [0, 5])
def test_MeshBuilder_validate_reports_node_number_outside_the_nodes(nodeNumber):
    errors = _mesh_builder_with_node_number(nodeNumber).Validate()

    assert [
        "At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]"
    ] == errors


def test_MeshBuilder_create_mesh_with_node_number_outside_the_nodes_fails():
    with pytest.raises(Exception, match="invalid node number"):
        _mesh_builder_with_node_number(5).CreateMesh()


UTM33_WKT = 'PROJCS["UTM-33",GEOGCS["Unused",DATUM["UTM Projections",SPHEROID["WGS 1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",15],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0],UNIT["Meter",1]]'


# 2011 version: "[numNodes:integer] [projection:string]", always bathymetry in meter
# 2012 version: "[eumItem:integer] [eumUnit:integer] [numNodes:integer] [projection:string]"
@pytest.mark.parametrize(
    "header, unit, projection",
    [
        (" 2057  UTM-33  ", eumUnit.eumUmeter, "UTM-33"),
        (f" 2057  {UTM33_WKT}  ", eumUnit.eumUmeter, UTM33_WKT),
        ("          100079 1014 2057 UTM-33  ", eumUnit.eumUfeetUS, "UTM-33"),
        (f" 100079 1000 2057 {UTM33_WKT}  ", eumUnit.eumUmeter, UTM33_WKT),
    ],
)
def test_ReadMesh_header_line_versions(tmp_path, header, unit, projection):
    with open("testdata/Oresund.mesh") as reader:
        lines = reader.readlines()
    filename = tmp_path / "header.mesh"
    filename.write_text(header + "\n" + "".join(lines[1:]))

    mesh = MeshFile.ReadMesh(str(filename))

    quantity = mesh.EumQuantity
    assert quantity is not None
    assert eumItem.eumIBathymetry == quantity.Item
    assert unit == quantity.Unit
    assert projection == mesh.ProjectionString
    assert 2057 == mesh.NumberOfNodes
    assert 3636 == mesh.NumberOfElements
    x = mesh.X
    assert x is not None
    # ## 1 359862.97332797921 6206313.7132576201 -1.7859922534795478 1
    assert 359862.97332797921 == x[0]


def test_MeshBuilder_rebuilds_the_Oresund_mesh(tmp_path):
    filename = str(tmp_path / "Oresund.mesh")
    original = MeshFile.ReadMesh("testdata/Oresund.mesh")
    builder = MeshBuilder()

    assert 3 == len(builder.Validate())
    builder.SetProjection(original.ProjectionString)
    assert 2 == len(builder.Validate())
    builder.SetNodes(original.X, original.Y, original.Z, original.Code)
    assert 1 == len(builder.Validate())
    builder.SetElements(original.ElementTable)
    assert [] == builder.Validate()
    builder.SetEumQuantity(eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUcentimeter))
    builder.CreateMesh().Write(filename)

    mesh = MeshFile.ReadMesh(filename)
    quantity = mesh.EumQuantity
    assert quantity is not None
    assert eumItem.eumIBathymetry == quantity.Item
    assert eumUnit.eumUcentimeter == quantity.Unit
    assert "UTM-33" == mesh.ProjectionString
    assert_array_equal(original.NodeIds, mesh.NodeIds)
    assert_array_equal(original.X, mesh.X)
    assert_array_equal(original.Y, mesh.Y)
    originalZ = original.Z
    z = mesh.Z
    assert originalZ is not None
    assert z is not None
    # Exact z is test_MeshBuilder_keeps_z_precision
    assert_allclose(originalZ, z, rtol=1e-6)
    assert_array_equal(original.Code, mesh.Code)
    assert_array_equal(original.ElementIds, mesh.ElementIds)
    assert_array_equal(original.ElementType, mesh.ElementType)
    assert len(original.ElementTable) == len(mesh.ElementTable)
    for expected, element in zip(original.ElementTable, mesh.ElementTable):
        assert_array_equal(expected, element)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Suspected bug: MeshBuilder.SetNodes converts z to float32, so a mesh built "
        "from double z values, such as one read with MeshFile.ReadMesh, is written "
        "with z rounded to about 7 digits. Mesh files store z as doubles, and "
        "MeshFile and SetNodes keep x and y as doubles. Correct: z is kept as given."
    ),
)
def test_MeshBuilder_keeps_z_precision(tmp_path):
    filename = str(tmp_path / "z.mesh")
    # ## 1 359862.97332797921 6206313.7132576201 -1.7859922534795478 1
    z = [-1.7859922534795478, -2.0, -3.0, -4.0]
    builder = MeshBuilder()
    builder.SetProjection("NON-UTM")
    builder.SetNodes(X, Y, z, CODE)
    builder.SetElements(ELEMENTS)
    builder.CreateMesh().Write(filename)

    mesh = MeshFile.ReadMesh(filename)
    assert_array_equal(z, mesh.Z)


def test_MeshBuilder_element_ids_are_written(tmp_path):
    filename = str(tmp_path / "element_ids.mesh")
    builder = MeshBuilder()
    builder.SetProjection("NON-UTM")
    builder.SetNodes(X, Y, Z, CODE)
    builder.SetElements(ELEMENTS)
    builder.SetElementIds([10, 20])
    builder.CreateMesh().Write(filename)

    mesh = MeshFile.ReadMesh(filename)
    assert_array_equal([10, 20], mesh.ElementIds)


def test_MeshBuilder_mixed_triangles_and_quadrilaterals(tmp_path):
    meshFilename = str(tmp_path / "mixed.mesh")
    dfsuFilename = str(tmp_path / "mixed.dfsu")
    # A square and a triangle on its right side
    builder = MeshBuilder()
    builder.SetProjection("NON-UTM")
    builder.SetNodes(
        [0.0, 1.0, 1.0, 0.0, 2.0],
        [0.0, 0.0, 1.0, 1.0, 0.5],
        [-1.0, -2.0, -3.0, -4.0, -5.0],
        [1, 1, 1, 1, 1],
    )
    builder.SetElements([[1, 2, 3, 4], [2, 5, 3]])
    builder.CreateMesh().Write(meshFilename)

    # The mesh format's element header line after the 5 nodes: number of elements,
    # nodes per element and element type, 25 for up to 4 nodes. Other MIKE tools
    # read it; MeshFile.ReadMesh does not.
    with open(meshFilename) as reader:
        lines = reader.read().splitlines()
    assert ["2", "4", "25"] == lines[6].split()

    mesh = MeshFile.ReadMesh(meshFilename)
    assert_array_equal([1, 2, 3, 4], mesh.ElementTable[0])
    assert_array_equal([2, 5, 3], mesh.ElementTable[1])

    # The native dfsu library reads the element types from the mesh as written
    dfsuBuilder = DfsuBuilder.Create(DfsuFileType.Dfsu2D)
    dfsuBuilder.SetFromMeshFile(mesh)
    dfsuBuilder.SetTimeInfo(datetime.datetime(2020, 1, 1), 60)
    dfsuBuilder.AddDynamicItem(
        "Value", eumQuantity(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined)
    )
    dfsuBuilder.CreateFile(dfsuFilename).Close()
    dfsu = DfsuFile.Open(dfsuFilename)
    # MIKE element types: 25 is a quadrilateral, 21 a triangle
    assert_array_equal([25, 21], dfsu.ElementType)
    assert_array_equal([1, 2, 3, 4], dfsu.ElementTable[0])
    assert_array_equal([2, 5, 3], dfsu.ElementTable[1])
    dfsu.Close()


def test_MeshBuilder_create_from_dfsu_file(tmp_path):
    filename = str(tmp_path / "from_dfsu.mesh")
    dfsu = DfsuFile.Open("testdata/OresundHD.dfsu")
    MeshBuilder.Create(dfsu).Write(filename)

    mesh = MeshFile.ReadMesh(filename)
    quantity = mesh.EumQuantity
    assert quantity is not None
    # The dfsu file has no z unit, so the mesh is in meter
    assert eumItem.eumIBathymetry == quantity.Item
    assert eumUnit.eumUmeter == quantity.Unit
    assert dfsu.Projection.WKTString == mesh.ProjectionString
    assert_array_equal(dfsu.NodeIds, mesh.NodeIds)
    assert_array_equal(dfsu.X, mesh.X)
    assert_array_equal(dfsu.Y, mesh.Y)
    z = mesh.Z
    assert z is not None
    assert_array_equal(dfsu.Z, z.astype(np.float32))
    assert_array_equal(dfsu.Code, mesh.Code)
    assert_array_equal(dfsu.ElementIds, mesh.ElementIds)
    assert len(dfsu.ElementTable) == len(mesh.ElementTable)
    for expected, element in zip(dfsu.ElementTable, mesh.ElementTable):
        assert_array_equal(expected, element)
    dfsu.Close()
