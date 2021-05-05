import numpy as np
import unittest
from mikecore.MeshFile import MeshFile
from mikecore.MeshBuilder import MeshBuilder
from mikecore.eum import *
from numpy.testing import *
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

    def test_MeshBuilderTest(self):
    
        builder = MeshBuilder()
        filename = "testdata/Oresund.mesh"
        mesh = MeshFile.ReadMesh(filename)

    #     Assert.AreEqual(3, builder.Validate().Length)
    #     builder.SetProjection(mesh.ProjectionString)
    #     Assert.AreEqual(2, builder.Validate().Length)
    #     builder.SetNodes(mesh.X, mesh.Y, mesh.Z, mesh.Code)
    #     Assert.AreEqual(1, builder.Validate().Length)
    #     builder.SetElements(mesh.ElementTable)
    #     Assert.AreEqual(0, builder.Validate().Length)

    #     builder.SetEumQuantity(eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUcentimeter))

    #     newmesh = builder.CreateMesh()
    #     newmesh.Write("testdata/test_build_Oresund.mesh")
    


    ## <summary>
    ## Testing parsing of header line of mesh file.
    ## <para>
    ## 2011 version: "[numNodes:integer] [projection:string]"
    ## 2012 version: "[eumItem:integer] [eumUnit:integer] [numNodes:integer] [projection:string]"
    ## eumItem is so far always eumIBathymetry.
    ## </para>
    ## </summary>
    def test_MeshHeaderlineParsingTest(self):
    
        utm33Full = "PROJCS[\"UTM-33\",GEOGCS[\"Unused\",DATUM[\"UTM Projections\",SPHEROID[\"WGS 1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",15],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]"
        utm33Abbr = "UTM-33"

        ## Different versions of the header line string
        header2011 = " 2057  UTM-33  "
        header2011P = " 2057  PROJCS[\"UTM-33\",GEOGCS[\"Unused\",DATUM[\"UTM Projections\",SPHEROID[\"WGS 1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",15],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]  "
        header2012F = "          100079 1014 2057 UTM-33  "
        header2012P = " 100079 1000 2057 PROJCS[\"UTM-33\",GEOGCS[\"Unused\",DATUM[\"UTM Projections\",SPHEROID[\"WGS 1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",15],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]  "

        # quantity
        # numNodes
        # proj
            # header2012 = lambda s: re.match(r"(\d+)\s+(\d+)\s+(\d+)\s+(.+)", s)            
            # header2011 = lambda s: re.match(r"(\d+)\s+(.+)", s)

            # # First try match the 2012 header line format
            # match = header2012(line)
            # if match:
            #     groups = match.groups()
            #     itemType = eumItem(int(groups[0]))
            #     itemUnit = eumUnit(int(groups[1]))


        # ParseHeaderline(header2011.Trim(), out quantity, out numNodes, out proj)
        # Assert.AreEqual(eumItem.eumIBathymetry, quantity.Item)
        # Assert.AreEqual(eumUnit.eumUmeter, quantity.Unit)
        # Assert.AreEqual(2057, numNodes)
        # Assert.AreEqual(utm33Abbr, proj)

        # ParseHeaderline(header2011P.Trim(), out quantity, out numNodes, out proj)
        # Assert.AreEqual(eumItem.eumIBathymetry, quantity.Item)
        # Assert.AreEqual(eumUnit.eumUmeter, quantity.Unit)
        # Assert.AreEqual(2057, numNodes)
        # Assert.AreEqual(utm33Full, proj)

        # ParseHeaderline(header2012F.Trim(), out quantity, out numNodes, out proj)
        # Assert.AreEqual(eumItem.eumIBathymetry, quantity.Item)
        # Assert.AreEqual(eumUnit.eumUfeetUS, quantity.Unit)
        # Assert.AreEqual(2057, numNodes)
        # Assert.AreEqual(utm33Abbr, proj)

        # ParseHeaderline(header2012P.Trim(), out quantity, out numNodes, out proj)
        # Assert.AreEqual(eumItem.eumIBathymetry, quantity.Item)
        # Assert.AreEqual(eumUnit.eumUmeter, quantity.Unit)
        # Assert.AreEqual(2057, numNodes)
        # Assert.AreEqual(utm33Full, proj)
    