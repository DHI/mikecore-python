import unittest
import datetime
import os

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from mikecore.DfsFileFactory import *
from mikecore.DfsuBuilder import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *
from tests.examples_dfsu import *
from tests.test_util import *


class DfsuFileTests(unittest.TestCase):
    # region Vertical profile with only sigma layers

    # / <summary>
    # / Reading a vertical profile dfsu file.
    # / </summary>
    def test_VerticalProfileSigmaReadTest(self):
        filename = "testdata/VerticalProfileSigma.dfsu"
        self.VerticalProfileReadTest(filename, True)

    # / <summary>
    # / create a vertical profile dfsu file.
    # / </summary>
    def test_VerticalProfileSigmaCreateTest(self):
        sourcefilename = "testdata/VerticalProfileSigma.dfsu"
        filename = "testdata/testtmp/test_create_VerticalProfileSigma.dfsu"

        self.CreateDfsu3DFromSource(sourcefilename, filename)

        self.VerticalProfileReadTest(filename, False)

    def VerticalProfileReadTest(self, filename, original):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename)

        FileVerticalProfileSigmaDfsu.FileInfoTester(dfsFile)
        FileVerticalProfileSigmaDfsu.CustomBlockTester(dfsFile)
        FileVerticalProfileSigmaDfsu.DynamicItemTester(dfsFile.ItemInfo)
        FileVerticalProfileSigmaDfsu.StaticItemTester(dfsFile, original)
        FileVerticalProfileSigmaDfsu.ReadTester(dfsFile)

        dfsFile = DfsuFile.Open(filename)

        # Check file info
        FileVerticalProfileSigmaDfsu.FileInfoTester(dfsFile)
        # Check data in the dynamic items
        FileVerticalProfileSigmaDfsu.ReadTester(dfsFile)

    # endregion

    # region Vertical profile with mixed sigma-Z layers

    # / <summary>
    # / Reading a vertical profile dfsu file.
    # / </summary>
    def test_VerticalProfileSigmaZReadTest(self):
        filename = "testdata/VerticalProfileSigmaZ.dfsu"
        self.VerticalProfileSigmaZReadTest(filename, True)

    def test_VerticalProfileSigmaZCreateTest(self):
        sourcefilename = "testdata/VerticalProfileSigmaZ.dfsu"
        filename = "testdata/testtmp/test_create_VerticalProfileSigmaZ.dfsu"

        self.CreateDfsu3DFromSource(sourcefilename, filename)
        self.VerticalProfileSigmaZReadTest(filename, False)

    def VerticalProfileSigmaZReadTest(self, filename, original):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename)

        FileVerticalProfileSigmaZDfsu.FileInfoTester(dfsFile)
        FileVerticalProfileSigmaZDfsu.CustomBlockTester(dfsFile)
        FileVerticalProfileSigmaZDfsu.DynamicItemTester(dfsFile.ItemInfo)
        FileVerticalProfileSigmaZDfsu.StaticItemTester(dfsFile, original)
        FileVerticalProfileSigmaZDfsu.ReadTester(dfsFile)

        dfsFile = DfsuFile.Open(filename)

        # Check file info
        FileVerticalProfileSigmaZDfsu.FileInfoTester(dfsFile)
        # Check data in the dynamic items
        FileVerticalProfileSigmaZDfsu.ReadTester(dfsFile)

    # endregion

    # region Vertical Column

    # / <summary>
    # / Reading a vertical profile dfsu file.
    # / </summary>
    def test_VerticalColumnReadTest(self):
        filename = "testdata/VerticalColumn.dfsu"
        self.VerticalColumnReadTest(filename, True)

    def test_VerticalColumnCreateTest(self):
        sourcefilename = "testdata/VerticalColumn.dfsu"
        filename = "testdata/testtmp/test_create_VerticalColumn.dfsu"

        self.CreateDfsu3DFromSource(sourcefilename, filename)
        self.VerticalColumnReadTest(filename, False)

    # / <summary>
    # / Reading a vertical profile dfsu file.
    # / </summary>
    def VerticalColumnReadTest(self, filename, original):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename)

        FileVerticalColumnDfsu.FileInfoTester(dfsFile)
        FileVerticalColumnDfsu.CustomBlockTester(dfsFile)
        FileVerticalColumnDfsu.DynamicItemTester(dfsFile.ItemInfo)
        FileVerticalColumnDfsu.StaticItemTester(dfsFile, original)
        FileVerticalColumnDfsu.ReadTester(dfsFile)

        dfsFile = DfsuFile.Open(filename)

        # Check file info
        FileVerticalColumnDfsu.FileInfoTester(dfsFile)
        # Check data in the dynamic items
        FileVerticalColumnDfsu.ReadTester(dfsFile)

    # endregion

    # region 3D dfsu with mixed sigma-Z

    # / <summary>
    # / Reading a vertical profile dfsu file.
    # / </summary>
    def test_Read3DSigmaZOresundTest(self):
        filename = "testdata/Oresund3DSigmaZ.dfsu"
        self.Read3DSigmaZOresundTest(filename, True)

    def test_Create3DSigmaZOresundTest(self):
        sourcefilename = "testdata/Oresund3DSigmaZ.dfsu"
        filename = "testdata/testtmp/test_create_Oresund3DSigmaZ.dfsu"

        self.CreateDfsu3DFromSource(sourcefilename, filename)

        self.Read3DSigmaZOresundTest(filename, False)

    def Read3DSigmaZOresundTest(self, filename, original):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename)
        FileOresund3DSigmaZ.CustomBlockTester(dfsFile, original)
        FileOresund3DSigmaZ.StaticItemTester(dfsFile, original)
        dfsFile.Close()
        dfsFile = DfsFileFactory.DfsuFileOpen(filename)
        FileOresund3DSigmaZ.FileInfoTester(dfsFile, original)
        FileOresund3DSigmaZ.ReadTester(dfsFile)

        x, y, z = dfsFile.CalculateElementCenterCoordinates()

        topLayerIndices = DfsuUtil.FindTopLayerElements(dfsFile.ElementTable)
        topLayerIndices2 = DfsuUtil.FindTopLayerElementsXY(
            dfsFile.ElementTable, dfsFile.X, dfsFile.Y
        )

        Assert.AreEqual(3700, len(topLayerIndices))
        Assert.AreEqual(3700, len(topLayerIndices2))

    # endregion

    # region 3D dfsu with only sigma, but mixed triangle-quads

    # / <summary>
    # / Reading a vertical profile dfsu file.
    # / </summary>
    def test_Read3DSigmaOdenseTest(self):
        filename = "testdata/OdenseHD3D.dfsu"
        self.Read3DSigmaOdenseTest(filename, True)

    def test_Create3DSigmaOdenseTest(self):
        sourcefilename = "testdata/OdenseHD3D.dfsu"
        filename = "testdata/testtmp/test_create_OdenseHD3D.dfsu"

        self.CreateDfsu3DFromSource(sourcefilename, filename)

        self.Read3DSigmaOdenseTest(filename, False)

    def Read3DSigmaOdenseTest(self, filename, original):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename)
        FileOdenseHD3DDfsu.CustomBlockTester(dfsFile, original)
        FileOdenseHD3DDfsu.StaticItemTester(dfsFile, original)
        dfsFile.Close()
        dfsFile = DfsFileFactory.DfsuFileOpen(filename)
        FileOdenseHD3DDfsu.FileInfoTester(dfsFile, original)
        dfsFile.Close()

    # endregion

    # region Submesh files

    # Test files in testdata/submesh, all data type 2001:
    #
    #   File                                              MIKE_FM custom block
    #   Dfsu2D_CustomBlock6_Submesh0.dfsu                 [  9,   4, 2, 0,  0,  0]
    #   Dfsu2D_CustomBlock6_Submesh1_LocallyRefined.dfsu  [ 31,  40, 2, 0,  0,  1]
    #   Dfsu3DSigmaZ_CustomBlock5.dfsu                    [ 30,   8, 3, 3,  1]
    #   Dfsu3DSigmaZ_CustomBlock6_Submesh0.dfsu           [ 30,   8, 3, 3,  1,  0]
    #   DfsuSpectral0D_CustomBlock6_Legacy.dfsu           [416, 400, 2, 0, 25, 16]
    #
    # The two Dfsu3DSigmaZ files hold the same mesh, and the same data to
    # within float32 rounding (separate model runs).

    # / <summary>
    # / Reading a 2D dfsu file with submesh type 0.
    # / </summary>
    def test_Read2DSubmesh0Test(self):
        self.SubmeshCustomBlockTester(
            "testdata/submesh/Dfsu2D_CustomBlock6_Submesh0.dfsu", [9, 4, 2, 0, 0, 0]
        )
        dfsFile = DfsuFile.Open("testdata/submesh/Dfsu2D_CustomBlock6_Submesh0.dfsu")
        Assert.AreEqual(DfsuFileType.Dfsu2D, dfsFile.DfsuFileType)
        Assert.AreEqual(9, dfsFile.NumberOfNodes)
        Assert.AreEqual(4, dfsFile.NumberOfElements)
        Assert.AreEqual(0, dfsFile.NumberOfLayers)
        Assert.AreEqual(0, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(0, dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(0, dfsFile.NumberOfDirections)
        Assert.AreEqual(4, dfsFile.ReadItemTimeStep(1, 0).Data.size)
        dfsFile.Close()

    # / <summary>
    # / Reading a 3D sigma-z dfsu file with submesh type 0, the same as the
    # / 5-value file.
    # / </summary>
    def test_Read3DSubmesh0Test(self):
        self.SubmeshCustomBlockTester(
            "testdata/submesh/Dfsu3DSigmaZ_CustomBlock5.dfsu", [30, 8, 3, 3, 1]
        )
        self.SubmeshCustomBlockTester(
            "testdata/submesh/Dfsu3DSigmaZ_CustomBlock6_Submesh0.dfsu",
            [30, 8, 3, 3, 1, 0],
        )
        oldFile = DfsuFile.Open("testdata/submesh/Dfsu3DSigmaZ_CustomBlock5.dfsu")
        newFile = DfsuFile.Open(
            "testdata/submesh/Dfsu3DSigmaZ_CustomBlock6_Submesh0.dfsu"
        )
        Assert.AreEqual(DfsuFileType.Dfsu3DSigmaZ, newFile.DfsuFileType)
        Assert.AreEqual(oldFile.NumberOfNodes, newFile.NumberOfNodes)
        Assert.AreEqual(oldFile.NumberOfElements, newFile.NumberOfElements)
        Assert.AreEqual(oldFile.NumberOfLayers, newFile.NumberOfLayers)
        Assert.AreEqual(oldFile.NumberOfSigmaLayers, newFile.NumberOfSigmaLayers)
        Assert.IsNull(oldFile.SubMeshType)
        Assert.AreEqual(0, newFile.SubMeshType)
        Assert.AreEqual(oldFile.NumberOfFrequencies, newFile.NumberOfFrequencies)
        Assert.AreEqual(oldFile.NumberOfDirections, newFile.NumberOfDirections)
        assert_array_equal(
            oldFile.ReadItemTimeStep(1, 0).Data, newFile.ReadItemTimeStep(1, 0).Data
        )
        oldFile.Close()
        newFile.Close()

    # / <summary>
    # / Reading a locally refined 2D dfsu file, submesh type 1.
    # / </summary>
    # TODO: Only checks that it reads as an ordinary 2D mesh, not full
    # submesh support.
    def test_Read2DSubmesh1LocallyRefinedTest(self):
        self.SubmeshCustomBlockTester(
            "testdata/submesh/Dfsu2D_CustomBlock6_Submesh1_LocallyRefined.dfsu",
            [31, 40, 2, 0, 0, 1],
        )
        dfsFile = DfsuFile.Open(
            "testdata/submesh/Dfsu2D_CustomBlock6_Submesh1_LocallyRefined.dfsu"
        )
        Assert.AreEqual(DfsuFileType.Dfsu2D, dfsFile.DfsuFileType)
        Assert.AreEqual(31, dfsFile.NumberOfNodes)
        Assert.AreEqual(40, dfsFile.NumberOfElements)
        Assert.AreEqual(1, dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(0, dfsFile.NumberOfDirections)
        Assert.AreEqual(40, dfsFile.ReadItemTimeStep(1, 0).Data.size)
        dfsFile.Close()

    # / <summary>
    # / Reading a legacy Spectral0D (rose-plot) file, not as a submesh file.
    # / </summary>
    def test_ReadLegacySpectral0DTest(self):
        self.SubmeshCustomBlockTester(
            "testdata/submesh/DfsuSpectral0D_CustomBlock6_Legacy.dfsu",
            [416, 400, 2, 0, 25, 16],
        )
        dfsFile = DfsuFile.Open(
            "testdata/submesh/DfsuSpectral0D_CustomBlock6_Legacy.dfsu"
        )
        Assert.AreEqual(DfsuFileType.DfsuSpectral0D, dfsFile.DfsuFileType)
        Assert.AreEqual(416, dfsFile.NumberOfNodes)
        Assert.AreEqual(400, dfsFile.NumberOfElements)
        Assert.IsNull(dfsFile.SubMeshType)
        Assert.AreEqual(25, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(16, dfsFile.NumberOfDirections)
        assert dfsFile.Frequencies is not None
        assert dfsFile.Directions is not None
        Assert.AreEqual(25, len(dfsFile.Frequencies))
        Assert.AreEqual(16, len(dfsFile.Directions))
        Assert.AreEqual(400, dfsFile.ReadItemTimeStep(1, 0).Data.size)
        dfsFile.Close()

    # / <summary>
    # / Reading a legacy Spectral0D file with directions in degrees.
    # / </summary>
    def test_ReadLegacySpectral0DDegreesTest(self):
        filename = "testdata/testtmp/test_DfsuSpectral0D_CustomBlock6_Degrees.dfsu"
        self.RewriteDfsu(
            "testdata/submesh/DfsuSpectral0D_CustomBlock6_Legacy.dfsu",
            filename,
            staticQuantities={
                11: eumQuantity(eumItem.eumIWaveDirection, eumUnit.eumUdegree)
            },
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.DfsuSpectral0D, dfsFile.DfsuFileType)
        Assert.IsNull(dfsFile.SubMeshType)
        Assert.AreEqual(25, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(16, dfsFile.NumberOfDirections)
        assert dfsFile.Directions is not None
        Assert.AreEqual(16, len(dfsFile.Directions))
        dfsFile.Close()

    # / <summary>
    # / Reading a legacy Spectral0D file with generic EUM item types.
    # / </summary>
    def test_ReadLegacySpectral0DGenericItemTypesTest(self):
        filename = "testdata/testtmp/test_DfsuSpectral0D_CustomBlock6_Generic.dfsu"
        self.RewriteDfsu(
            "testdata/submesh/DfsuSpectral0D_CustomBlock6_Legacy.dfsu",
            filename,
            staticQuantities={
                10: eumQuantity(eumItem.eumIFrequency, eumUnit.eumUhertz),
                11: eumQuantity(eumItem.eumIDirection, eumUnit.eumUradian),
            },
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.DfsuSpectral0D, dfsFile.DfsuFileType)
        Assert.IsNull(dfsFile.SubMeshType)
        Assert.AreEqual(25, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(16, dfsFile.NumberOfDirections)
        assert dfsFile.Frequencies is not None
        Assert.AreEqual(25, len(dfsFile.Frequencies))
        assert dfsFile.Directions is not None
        Assert.AreEqual(16, len(dfsFile.Directions))
        dfsFile.Close()

    # / <summary>
    # / A legacy Spectral0D file with 7 values reads with the MIKE 2027 layout.
    # / </summary>
    def test_ReadLegacySpectral0DCustomBlock7Test(self):
        filename = "testdata/testtmp/test_DfsuSpectral0D_CustomBlock7.dfsu"
        self.RewriteDfsu(
            "testdata/submesh/DfsuSpectral0D_CustomBlock6_Legacy.dfsu",
            filename,
            customBlockValues=[416, 400, 2, 0, 25, 16, 0],
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.Dfsu2D, dfsFile.DfsuFileType)
        Assert.AreEqual(25, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(16, dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(0, dfsFile.NumberOfDirections)
        dfsFile.Close()

    # / <summary>
    # / Reading a legacy Spectral0D file with frequencies only.
    # / </summary>
    def test_ReadLegacySpectral0DFrequencyOnlyTest(self):
        filename = "testdata/testtmp/test_DfsuSpectral0D_FrequencyOnly.dfsu"
        self.CreateSingleAxisSpectral0D(
            filename,
            [6, 5, 1, 0, 5, 0],
            eumQuantity(eumItem.eumIWaveFrequency, eumUnit.eumUhertz),
            [0.05, 0.06, 0.07, 0.08, 0.09],
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.DfsuSpectral0D, dfsFile.DfsuFileType)
        Assert.AreEqual(6, dfsFile.NumberOfNodes)
        Assert.AreEqual(5, dfsFile.NumberOfElements)
        Assert.IsNull(dfsFile.SubMeshType)
        Assert.AreEqual(5, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(0, dfsFile.NumberOfDirections)
        assert dfsFile.Frequencies is not None
        np.testing.assert_allclose(
            dfsFile.Frequencies, [0.05, 0.06, 0.07, 0.08, 0.09], rtol=1e-6
        )
        Assert.IsNull(dfsFile.Directions)
        Assert.AreEqual(5, dfsFile.ReadItemTimeStep(1, 0).Data.size)
        dfsFile.Close()

    # / <summary>
    # / Reading a legacy Spectral0D file with directions only.
    # / </summary>
    def test_ReadLegacySpectral0DDirectionOnlyTest(self):
        filename = "testdata/testtmp/test_DfsuSpectral0D_DirectionOnly.dfsu"
        self.CreateSingleAxisSpectral0D(
            filename,
            [5, 4, 1, 0, 0, 4],
            eumQuantity(eumItem.eumIWaveDirection, eumUnit.eumUdegree),
            [0, 90, 180, 270],
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.DfsuSpectral0D, dfsFile.DfsuFileType)
        Assert.AreEqual(5, dfsFile.NumberOfNodes)
        Assert.AreEqual(4, dfsFile.NumberOfElements)
        Assert.IsNull(dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(4, dfsFile.NumberOfDirections)
        Assert.IsNull(dfsFile.Frequencies)
        assert_array_equal([0, 90, 180, 270], dfsFile.Directions)
        Assert.AreEqual(4, dfsFile.ReadItemTimeStep(1, 0).Data.size)
        dfsFile.Close()

    # / <summary>
    # / A 6-value file whose 10th static item is not a frequency reads with
    # / the MIKE 2027 layout.
    # / </summary>
    def test_ReadSingleAxisNotFrequencyTest(self):
        filename = "testdata/testtmp/test_Dfsu1D_CustomBlock6_NotFrequency.dfsu"
        self.CreateSingleAxisSpectral0D(
            filename,
            [6, 5, 1, 0, 5, 0],
            eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
            [1, 2, 3, 4, 5],
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.Dfsu1D, dfsFile.DfsuFileType)
        Assert.AreEqual(5, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(0, dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(0, dfsFile.NumberOfDirections)
        Assert.IsNull(dfsFile.Frequencies)
        dfsFile.Close()

    # / <summary>
    # / A frequency-only file with an extra static item reads with the MIKE
    # / 2027 layout.
    # / </summary>
    def test_ReadSingleAxisExtraStaticItemTest(self):
        filename = "testdata/testtmp/test_Dfsu1D_CustomBlock6_ExtraStaticItem.dfsu"
        self.CreateSingleAxisSpectral0D(
            filename,
            [6, 5, 1, 0, 5, 0],
            eumQuantity(eumItem.eumIWaveFrequency, eumUnit.eumUhertz),
            [0.05, 0.06, 0.07, 0.08, 0.09],
            extraStaticItem=True,
        )
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.Dfsu1D, dfsFile.DfsuFileType)
        Assert.AreEqual(5, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(0, dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        dfsFile.Close()

    # / <summary>
    # / Appending a time step to files with a 6-value custom block, including
    # / legacy Spectral0D files, whose static items are read first.
    # / </summary>
    def test_AppendSubmeshTest(self):
        frequencyOnly = "testdata/testtmp/test_DfsuSpectral0D_FrequencyOnly_Source.dfsu"
        self.CreateSingleAxisSpectral0D(
            frequencyOnly,
            [6, 5, 1, 0, 5, 0],
            eumQuantity(eumItem.eumIWaveFrequency, eumUnit.eumUhertz),
            [0.05, 0.06, 0.07, 0.08, 0.09],
        )
        for source, subMeshType in (
            ("testdata/submesh/Dfsu2D_CustomBlock6_Submesh1_LocallyRefined.dfsu", 1),
            ("testdata/submesh/Dfsu3DSigmaZ_CustomBlock6_Submesh0.dfsu", 0),
            ("testdata/submesh/DfsuSpectral0D_CustomBlock6_Legacy.dfsu", None),
            (frequencyOnly, None),
        ):
            filename = "testdata/testtmp/test_append_" + os.path.basename(source)
            testUtil.copy_file(source, filename)
            dfsFile = DfsuFile.OpenAppend(filename)
            Assert.AreEqual(subMeshType, dfsFile.SubMeshType)
            numberOfTimeSteps = dfsFile.NumberOfTimeSteps
            for itemInfo in dfsFile.ItemInfo:
                dfsFile.WriteItemTimeStepNext(
                    0, np.ones(itemInfo.ElementCount, np.float32)
                )
            dfsFile.Close()
            dfsFile = DfsuFile.Open(filename)
            Assert.AreEqual(numberOfTimeSteps + 1, dfsFile.NumberOfTimeSteps)
            Assert.AreEqual(subMeshType, dfsFile.SubMeshType)
            for itemNumber in range(1, len(dfsFile.ItemInfo) + 1):
                assert_array_equal(
                    1, dfsFile.ReadItemTimeStep(itemNumber, numberOfTimeSteps).Data
                )
            dfsFile.Close()

    # / <summary>
    # / A 3D sigma-z file with 7 values reads with the MIKE 2027 layout;
    # / values from 7 on are ignored.
    # / </summary>
    def test_Read3DCustomBlock7Test(self):
        filename = "testdata/testtmp/test_Dfsu3DSigmaZ_CustomBlock7.dfsu"
        self.RewriteDfsu(
            "testdata/submesh/Dfsu3DSigmaZ_CustomBlock6_Submesh0.dfsu",
            filename,
            customBlockValues=[30, 8, 3, 3, 1, 0, 0],
        )
        self.SubmeshCustomBlockTester(filename, [30, 8, 3, 3, 1, 0, 0])
        dfsFile = DfsuFile.Open(filename)
        Assert.AreEqual(DfsuFileType.Dfsu3DSigmaZ, dfsFile.DfsuFileType)
        Assert.AreEqual(30, dfsFile.NumberOfNodes)
        Assert.AreEqual(8, dfsFile.NumberOfElements)
        Assert.AreEqual(3, dfsFile.NumberOfLayers)
        Assert.AreEqual(1, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(0, dfsFile.SubMeshType)
        Assert.AreEqual(0, dfsFile.NumberOfFrequencies)
        Assert.AreEqual(0, dfsFile.NumberOfDirections)
        Assert.AreEqual(8, dfsFile.ReadItemTimeStep(2, 0).Data.size)
        dfsFile.Close()

    # / <summary>
    # / Copies a dfsu file, optionally replacing its custom block values and
    # / the quantity of static items by number.
    # / </summary>
    def RewriteDfsu(
        self, sourcefilename, filename, customBlockValues=None, staticQuantities=None
    ):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        source = DfsFileFactory.DfsGenericOpen(sourcefilename)
        fileInfo = source.FileInfo

        builder = DfsBuilder.Create(
            fileInfo.FileTitle, fileInfo.ApplicationTitle, fileInfo.ApplicationVersion
        )
        builder.SetDataType(fileInfo.DataType)
        builder.SetGeographicalProjection(fileInfo.Projection)
        timeAxis = fileInfo.TimeAxis
        assert timeAxis is not None
        builder.SetTemporalAxis(timeAxis)
        builder.DeleteValueFloat = fileInfo.DeleteValueFloat
        customBlock = fileInfo.CustomBlocks[0]
        if customBlockValues is None:
            builder.AddCustomBlock(customBlock)
        else:
            builder.AddCreateCustomBlock(
                customBlock.Name, np.array(customBlockValues, np.int32)
            )
        for itemInfo in source.ItemInfo:
            builder.AddDynamicItem(itemInfo)
        builder.CreateFile(filename)

        staticItemNumber = 1
        staticItem = source.ReadStaticItemNext()
        while staticItem is not None:
            if staticQuantities and staticItemNumber in staticQuantities:
                staticItem.Quantity = staticQuantities[staticItemNumber]
            builder.AddStaticItem(staticItem)
            staticItemNumber += 1
            staticItem = source.ReadStaticItemNext()

        file = builder.GetFile()
        itemData = source.ReadItemTimeStepNext()
        while itemData is not None:
            file.WriteItemTimeStepNext(itemData.Time, itemData.Data)
            itemData = source.ReadItemTimeStepNext()
        source.Close()
        file.Close()

    # / <summary>
    # / Creates a legacy single-axis Spectral0D file (dimension 1, one node
    # / more than elements) with the axis as static item 10, optionally
    # / repeated as item 11.
    # / </summary>
    def CreateSingleAxisSpectral0D(
        self,
        filename,
        customBlockValues,
        axisQuantity,
        axisValues,
        extraStaticItem=False,
    ):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        numberOfElements = len(axisValues)
        numberOfNodes = numberOfElements + 1
        factory = DfsFactory()
        builder = DfsBuilder.Create("Single axis Spectral0D", "MIKE Core Python", 1)
        builder.SetDataType(2001)
        builder.SetGeographicalProjection(factory.CreateProjection("LONG/LAT"))
        builder.SetTemporalAxis(factory.CreateTemporalEqTimeAxis(eumUnit.eumUsec, 0, 1))
        builder.AddCreateCustomBlock("MIKE_FM", np.array(customBlockValues, np.int32))
        builder.AddCreateDynamicItem(
            "Water level",
            eumQuantity(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
            spatialAxis=factory.CreateAxisEqD1(
                eumUnit.eumUmeter, numberOfElements, 0, 1
            ),
        )
        builder.CreateFile(filename)

        intCode = eumQuantity(eumItem.eumIIntegerCode, eumUnit.eumUintCode)
        xyQuantity = eumQuantity(eumItem.eumILatLong, eumUnit.eumUdegree)
        nodeIds = np.arange(1, numberOfNodes + 1, dtype=np.int32)
        elementIds = np.arange(1, numberOfElements + 1, dtype=np.int32)
        builder.AddCreateStaticItem("Node id", intCode, nodeIds)
        builder.AddCreateStaticItem(
            "X-coord", xyQuantity, np.arange(numberOfNodes, dtype=np.float64)
        )
        builder.AddCreateStaticItem(
            "Y-coord", xyQuantity, np.zeros(numberOfNodes, np.float64)
        )
        builder.AddCreateStaticItem(
            "Z-coord",
            eumQuantity(eumItem.eumIItemGeometry3D, eumUnit.eumUmeter),
            np.full(numberOfNodes, -10, np.float32),
        )
        builder.AddCreateStaticItem("Code", intCode, np.zeros(numberOfNodes, np.int32))
        builder.AddCreateStaticItem("Element id", intCode, elementIds)
        builder.AddCreateStaticItem(
            "Element type", intCode, np.full(numberOfElements, 11, np.int32)
        )
        builder.AddCreateStaticItem(
            "No of nodes", intCode, np.full(numberOfElements, 2, np.int32)
        )
        builder.AddCreateStaticItem(
            "Connectivity",
            intCode,
            np.column_stack([elementIds, elementIds + 1]).ravel().astype(np.int32),
        )
        builder.AddCreateStaticItem(
            "Axis", axisQuantity, np.array(axisValues, np.float32)
        )
        if extraStaticItem:
            builder.AddCreateStaticItem(
                "Extra", axisQuantity, np.array(axisValues, np.float32)
            )

        file = builder.GetFile()
        file.WriteItemTimeStepNext(0, np.ones(numberOfElements, np.float32))
        file.Close()

    # / <summary>
    # / Checks the custom block values, read as a generic dfs file.
    # / </summary>
    def SubmeshCustomBlockTester(self, filename, expectedValues):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename)
        fileInfo = dfsFile.FileInfo
        Assert.AreEqual(2001, fileInfo.DataType)
        Assert.AreEqual(1, len(fileInfo.CustomBlocks))
        customBlock = fileInfo.CustomBlocks[0]
        Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType)
        Assert.AreEqual("MIKE_FM", customBlock.Name)
        Assert.AreEqual(len(expectedValues), customBlock.Count)
        for i in range(customBlock.Count):
            Assert.AreEqual(expectedValues[i], customBlock[i])

        dfsFile.Close()

    # endregion

    def CreateDfsu3DFromSource(self, sourcefilename, filename):
        source = DfsuFile.Open(sourcefilename)

        builder = DfsuBuilder.Create(source.DfsuFileType)

        # Setup header and geometry, copy from source file
        builder.SetNodes(source.X, source.Y, source.Z, source.Code)
        builder.SetElements(source.ElementTable)
        builder.SetProjection(source.Projection)
        builder.SetTimeInfo(source.StartDateTime, source.TimeStepInSeconds)
        builder.SetNumberOfSigmaLayers(source.NumberOfSigmaLayers)

        # Add dynamic items, copying from source. Do not add the first
        # dynamic item - that is a Z-coordinate item and is added automatically.
        for i in range(1, len(source.ItemInfo)):
            itemInfo = source.ItemInfo[i]
            builder.AddDynamicItem(itemInfo.Name, itemInfo.Quantity)

        file = builder.CreateFile(filename)

        # Add data for all item-timesteps, copying from source.
        # Be aware that the first item is the Z-coordinate, and has
        # another length than the other items.
        while True:
            sourceData = source.ReadItemTimeStepNext()
            if sourceData is None:
                break
            file.WriteItemTimeStepNext(sourceData.Time, sourceData.Data)

        source.Close()
        file.Close()


class FileOresund3DSigmaZ:
    @staticmethod
    def FileInfoTester(dfsFile, original):
        Assert.AreEqual(DfsuFileType.Dfsu3DSigmaZ, dfsFile.DfsuFileType)
        Assert.AreEqual(3, dfsFile.NumberOfSigmaLayers)
        # For some reason the original file reports 38 layers, thouth
        # data only starts at layer 6, the first 5 are empty.
        Assert.AreEqual(38 if (original) else 33, dfsFile.NumberOfLayers)

        Assert.AreEqual("3D volume series", dfsFile.FileTitle)
        Assert.AreEqual("", dfsFile.ApplicationTitle)
        Assert.AreEqual(0, dfsFile.ApplicationVersion)
        Assert.AreEqual(38227, dfsFile.NumberOfElements)
        Assert.AreEqual(25272, dfsFile.NumberOfNodes)

        topLayerElements = dfsFile.FindTopLayerElements()
        Assert.AreEqual(3700, len(topLayerElements))
        Assert.AreEqual(2, topLayerElements[0])
        Assert.AreEqual(99, topLayerElements[23])
        Assert.AreEqual(38211, topLayerElements[3698])
        Assert.AreEqual(38226, topLayerElements[3699])

    @staticmethod
    def CustomBlockTester(dfsFile, original):
        fileInfo = dfsFile.FileInfo

        Assert.AreEqual(1, len(fileInfo.CustomBlocks))

        customBlock = fileInfo.CustomBlocks[0]
        Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType)
        Assert.AreEqual("MIKE_FM", customBlock.Name)
        Assert.AreEqual(5, customBlock.Count)
        Assert.AreEqual(25272, customBlock[0])
        Assert.AreEqual(38227, customBlock[1])
        Assert.AreEqual(3, customBlock[2])
        Assert.AreEqual(38 if (original) else 33, customBlock[3])
        Assert.AreEqual(3, customBlock[4])

    @staticmethod
    def StaticItemTester(dfsFile, original):
        staticItems = []

        staticItemNumber = 1
        while True:
            varstaticItem = dfsFile.ReadStaticItem(staticItemNumber)
            if varstaticItem is None:
                break
            staticItems.append(varstaticItem)
            staticItemNumber += 1

        Assert.IsNotNull(staticItems)
        Assert.AreEqual(9, len(staticItems))

        # / Static items in a dfsu file:
        # / "Node id"       , int
        # / "X-coord"       , float
        # / "Y-coord"       , float
        # / "Z-coord"       , float
        # / "Code"          , int
        # / "Element id"    , int
        # / "Element type"  , int
        # / "No of nodes"   , int
        # / "Connectivity"  , int

        deleteValueFloat = np.float32(-1.00000002e-35)

        # --------------------------------------
        # Check x-coord static item
        staticItem = staticItems[1]
        Assert.AreEqual(2, staticItem.ItemNumber)
        Assert.AreEqual(25272, staticItem.ElementCount)
        # Assert.AreEqual(25272, staticItem.UsedElementCount);

        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIGeographicalCoordinate == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUmeter, staticItem.Quantity.Unit)
        else:
            Assert.Fail("X coordinate axis item type mismatch")

        if (
            staticItem.DataType != DfsSimpleType.Double
            and staticItem.DataType != DfsSimpleType.Float
        ):
            Assert.Fail("DataType of X static item mismatch")
        Assert.AreEqual("X-coord", staticItem.Name)

        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateX)
        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateY)
        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateZ)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationAlpha)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationPhi)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationTheta)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        if original:
            Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit)
        else:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, axis.AxisUnit)
        Assert.AreEqual(25272, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check data - first and last coordinate
        Assert.AreEqual(np.float32(351641.031), staticItem.Data[0])
        Assert.AreEqual(np.float32(340130.375), staticItem.Data[25271])

        # --------------------------------------
        # Check element type static item
        staticItem = staticItems[6]
        Assert.AreEqual(7, staticItem.ItemNumber)
        Assert.AreEqual(38227, staticItem.ElementCount)
        # Assert.AreEqual(38227, staticItem.UsedElementCount);
        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIIntegerCode == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit)
        else:
            Assert.Fail("Element Type static item type mismatch")
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        Assert.AreEqual(
            "Element type", staticItem.Name
        )  # Note: Not the same as in dfsu file from engine!

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(38227, axis.XCount)

        # Check data - first and last elements
        Assert.AreEqual(32, staticItem.Data[0])
        Assert.AreEqual(32, staticItem.Data[2])
        Assert.AreEqual(32, staticItem.Data[38220])

        # --------------------------------------
        # Check connectivity static item
        staticItem = staticItems[8]
        Assert.AreEqual(9, staticItem.ItemNumber)
        Assert.AreEqual(6 * 38227, staticItem.ElementCount)
        # Assert.AreEqual(6 * 38227, staticItem.UsedElementCount);
        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIIntegerCode == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit)
        else:
            Assert.Fail("Connectivity item type mismatch")
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        Assert.AreEqual("Connectivity", staticItem.Name)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        if original:
            Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit)
        else:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, axis.AxisUnit)
        Assert.AreEqual(6 * 38227, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check data - first and last element
        Assert.AreEqual(1, staticItem.Data[0])
        Assert.AreEqual(5, staticItem.Data[1])
        Assert.AreEqual(9, staticItem.Data[2])
        Assert.AreEqual(2, staticItem.Data[3])
        Assert.AreEqual(6, staticItem.Data[4])
        Assert.AreEqual(10, staticItem.Data[5])
        Assert.AreEqual(2, staticItem.Data[6])

    @staticmethod
    def ReadTester(dfsFile):

        # Check that the ReadItemTimeStepNext item round-robin is correct

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(0.0, itemData.Time)
        Assert.AreEqual(25272, itemData.Data.size)
        Assert.AreEqual(np.float32(-0.5387732), itemData.Data[2])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(38227, itemData.Data.size)
        Assert.AreEqual(np.float32(22.9464741), itemData.Data[4])

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(10800, itemData.Time)
        Assert.AreEqual(np.float32(-0.503681362), itemData.Data[2])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(np.float32(23.0609226), itemData.Data[4])

        # Testing reusing the itemData's
        itemDatas = np.zeros(6, dtype=object)
        for i in range(2):
            itemDatas[i] = dfsFile.ReadItemTimeStep(i + 1, 0)

        for j in range(1, 9):
            for i in range(2):
                itemData = itemDatas[i]
                dfsFile.ReadItemTimeStep(itemData, j)
                Assert.AreEqual(i + 1, itemData.ItemNumber)
                Assert.AreEqual(j * 10800, itemData.Time)

        Assert.AreEqual(np.float32(-0.449256927), itemDatas[0].Data[2])
        Assert.AreEqual(np.float32(24.12122), itemDatas[1].Data[4])

        # Now we are at end of file, check what happens then:
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())


class FileOdenseHD3DDfsu:
    @staticmethod
    def FileInfoTester(dfsFile, original):
        Assert.AreEqual(DfsuFileType.Dfsu3DSigma, dfsFile.DfsuFileType)
        Assert.AreEqual(7, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(7, dfsFile.NumberOfLayers)

        # Assert.AreEqual("3D volume series", dfsFile.FileTitle);
        # Assert.AreEqual("", dfsFile.ApplicationTitle);
        # Assert.AreEqual(0, dfsFile.ApplicationVersion);
        Assert.AreEqual(5068, dfsFile.NumberOfElements)
        Assert.AreEqual(4280, dfsFile.NumberOfNodes)

        topLayerElements = dfsFile.FindTopLayerElements()
        Assert.AreEqual(724, len(topLayerElements))
        Assert.AreEqual(6, topLayerElements[0])
        Assert.AreEqual(13, topLayerElements[1])
        Assert.AreEqual(20, topLayerElements[2])

        Assert.AreEqual(5068, len(dfsFile.ElementTable))
        Assert.AreEqual(6, dfsFile.ElementTable[0].size)
        Assert.AreEqual(6, dfsFile.ElementTable[7 * 507 - 1].size)
        Assert.AreEqual(8, dfsFile.ElementTable[7 * 507].size)
        Assert.AreEqual(8, dfsFile.ElementTable[7 * 509 - 1].size)
        Assert.AreEqual(6, dfsFile.ElementTable[7 * 509].size)

        Assert.AreEqual(5068, dfsFile.ElementType.size)
        Assert.AreEqual(32, dfsFile.ElementType[0])
        Assert.AreEqual(32, dfsFile.ElementType[7 * 507 - 1])
        Assert.AreEqual(33, dfsFile.ElementType[7 * 507])
        Assert.AreEqual(33, dfsFile.ElementType[7 * 509 - 1])
        Assert.AreEqual(32, dfsFile.ElementType[7 * 509])

    @staticmethod
    def CustomBlockTester(dfsFile, original):
        fileInfo = dfsFile.FileInfo

        Assert.AreEqual(1, len(fileInfo.CustomBlocks))

        customBlock = fileInfo.CustomBlocks[0]
        Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType)
        Assert.AreEqual("MIKE_FM", customBlock.Name)
        Assert.AreEqual(5, customBlock.Count)
        Assert.AreEqual(4280, customBlock[0])
        Assert.AreEqual(5068, customBlock[1])
        Assert.AreEqual(3, customBlock[2])
        Assert.AreEqual(7, customBlock[3])
        Assert.AreEqual(7, customBlock[4])

    @staticmethod
    def StaticItemTester(dfsFile, original):
        staticItems = []

        staticItemNumber = 1
        while True:
            varstaticItem = dfsFile.ReadStaticItem(staticItemNumber)
            if varstaticItem is None:
                break
            staticItems.append(varstaticItem)
            staticItemNumber += 1

        Assert.IsNotNull(staticItems)
        Assert.AreEqual(9, len(staticItems))

        # Static items in a dfsu file:
        # "Node id"       , int
        # "X-coord"       , float
        # "Y-coord"       , float
        # "Z-coord"       , float
        # "Code"          , int
        # "Element id"    , int
        # "Element type"  , int
        # "No of nodes"   , int
        # "Connectivity"  , int

        # --------------------------------------
        # Check x-coord static item
        staticItem = staticItems[1]
        Assert.AreEqual(2, staticItem.ItemNumber)
        Assert.AreEqual(4280, staticItem.ElementCount)
        Assert.AreEqual("X-coord", staticItem.Name)

        # Check data - first and last coordinate
        Assert.AreEqual(np.float32(222397.938), staticItem.Data[0])
        Assert.AreEqual(np.float32(213346.141), staticItem.Data[4279])

        # --------------------------------------
        # Check element type static item
        staticItem = staticItems[6]
        Assert.AreEqual(7, staticItem.ItemNumber)
        Assert.AreEqual(5068, staticItem.ElementCount)
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        Assert.AreEqual(
            "Element type", staticItem.Name
        )  # Note: Not the same as in dfsu file from engine!

        # Check data - first and last elements
        Assert.AreEqual(32, staticItem.Data[0])
        Assert.AreEqual(32, staticItem.Data[7 * 507 - 1])  # upper element - triangle
        Assert.AreEqual(
            33, staticItem.Data[7 * 507]
        )  # lower element in next column, quad
        Assert.AreEqual(33, staticItem.Data[7 * 509 - 1])  # upper element - quad
        Assert.AreEqual(
            32, staticItem.Data[7 * 509]
        )  # lower element in next column, triangle

        # --------------------------------------
        # Check connectivity static item
        staticItem = staticItems[8]
        Assert.AreEqual(9, staticItem.ItemNumber)
        Assert.AreEqual(33362, staticItem.ElementCount)
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        Assert.AreEqual("Connectivity", staticItem.Name)

        # Check data - first and last element
        Assert.AreEqual(1, staticItem.Data[0])
        Assert.AreEqual(9, staticItem.Data[1])
        Assert.AreEqual(17, staticItem.Data[2])
        Assert.AreEqual(2, staticItem.Data[3])
        Assert.AreEqual(10, staticItem.Data[4])
        Assert.AreEqual(18, staticItem.Data[5])
        Assert.AreEqual(2, staticItem.Data[6])
        Assert.AreEqual(10, staticItem.Data[7])
        Assert.AreEqual(18, staticItem.Data[8])


# / <summary>
# / Class with methods to test the content of the
# / file "VerticalProfileSigmaZ.dfsu" which is a
# / vertical profile through a 3D mixed sigma-z
# / dfsu file.
# / </summary>
class FileVerticalProfileSigmaDfsu:
    @staticmethod
    def FileInfoTester(dfsFile):
        Assert.AreEqual(datetime.datetime(2002, 1, 3), dfsFile.StartDateTime)
        Assert.AreEqual(13, dfsFile.NumberOfTimeSteps)

        Assert.AreEqual(DfsuFileType.DfsuVerticalProfileSigma, dfsFile.DfsuFileType)
        Assert.AreEqual(7, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(7, dfsFile.NumberOfLayers)

        # Check dynamic items
        Assert.AreEqual(2, len(dfsFile.ItemInfo))
        Assert.AreEqual("Z coordinate", dfsFile.ItemInfo[0].Name)
        Assert.AreEqual("Current speed", dfsFile.ItemInfo[1].Name)

        # Check geometry (static items)
        Assert.AreEqual(312, dfsFile.X.size)

        # Check data - first and last coordinate
        Assert.AreEqual(np.float32(214817.375), dfsFile.X[0])
        Assert.AreEqual(np.float32(223442.266), dfsFile.X[311])
        Assert.AreEqual(np.float32(6159041.5), dfsFile.Y[0])
        Assert.AreEqual(np.float32(6158791.0), dfsFile.Y[311])

        Assert.AreEqual(266, len(dfsFile.ElementTable))

        topLayerElements = dfsFile.FindTopLayerElements()
        Assert.AreEqual(38, len(topLayerElements))
        Assert.AreEqual(6, topLayerElements[0])
        Assert.AreEqual(13, topLayerElements[1])
        Assert.AreEqual(20, topLayerElements[2])
        Assert.AreEqual(38 * 7 - 1, topLayerElements[37])

    @staticmethod
    def FileInfoTester(dfsFile):
        fileInfo = dfsFile.FileInfo

        # Assert.AreEqual("", fileInfo.FileTitle);
        # Assert.AreEqual("", fileInfo.ApplicationTitle);
        # Assert.AreEqual(1, fileInfo.ApplicationVersion);
        Assert.AreEqual(2001, fileInfo.DataType)

        # Assert.AreEqual(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
        Assert.AreEqual(StatType.NoStat, fileInfo.StatsType)

        Assert.AreEqual(np.float32(1e-35), fileInfo.DeleteValueFloat)
        Assert.AreEqual(0, fileInfo.DeleteValueByte)
        Assert.AreEqual(-1e-255, fileInfo.DeleteValueDouble)
        Assert.AreEqual(2147483647, fileInfo.DeleteValueInt)
        Assert.AreEqual(2147483647, fileInfo.DeleteValueUnsignedInt)

        Assert.AreEqual(
            TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType
        )
        timeAxis = fileInfo.TimeAxis
        Assert.IsNotNull(timeAxis)
        Assert.AreEqual(eumUnit.eumUsec, timeAxis.TimeUnit)
        Assert.AreEqual(86400, timeAxis.TimeStep)
        Assert.AreEqual(0, timeAxis.StartTimeOffset)
        Assert.AreEqual(13, timeAxis.NumberOfTimeSteps)

    @staticmethod
    def CustomBlockTester(dfsFile):
        fileInfo = dfsFile.FileInfo

        Assert.AreEqual(1, len(fileInfo.CustomBlocks))

        customBlock = fileInfo.CustomBlocks[0]
        Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType)
        Assert.AreEqual("MIKE_FM", customBlock.Name)
        Assert.AreEqual(5, customBlock.Count)
        Assert.AreEqual(312, customBlock[0])
        Assert.AreEqual(266, customBlock[1])
        Assert.AreEqual(2, customBlock[2])
        Assert.AreEqual(7, customBlock[3])
        Assert.AreEqual(7, customBlock[4])

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):

        Assert.IsNotNull(dynamicItemInfos)
        Assert.AreEqual(2, len(dynamicItemInfos))

        # Check dynamic info
        itemInfo = dynamicItemInfos[0]
        Assert.AreEqual(312, itemInfo.ElementCount)
        Assert.AreEqual(eumItem.eumIItemGeometry3D, itemInfo.Quantity.Item)
        Assert.AreEqual(eumUnit.eumUmeter, itemInfo.Quantity.Unit)
        Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType)
        Assert.AreEqual("Z coordinate", itemInfo.Name)
        Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType)

        # Check dynamic info
        itemInfo = dynamicItemInfos[1]
        Assert.AreEqual(266, itemInfo.ElementCount)
        Assert.AreEqual(eumItem.eumICurrentSpeed, itemInfo.Quantity.Item)
        Assert.AreEqual(eumUnit.eumUmeterPerSec, itemInfo.Quantity.Unit)
        Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType)
        Assert.AreEqual("Current speed", itemInfo.Name)
        Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType)

    @staticmethod
    def StaticItemTester(dfsFile, datamanager):
        staticItems = []

        staticItemNumber = 1
        while True:
            varstaticItem = dfsFile.ReadStaticItem(staticItemNumber)
            if varstaticItem is None:
                break
            staticItems.append(varstaticItem)
            staticItemNumber += 1

        Assert.IsNotNull(staticItems)
        Assert.AreEqual(9, len(staticItems))

        # Static items in a dfsu file:
        # "Node id"       , int
        # "X-coord"       , float
        # "Y-coord"       , float
        # "Z-coord"       , float
        # "Code"          , int
        # "Element id"    , int
        # "Element type"  , int
        # "No of nodes"   , int
        # "Connectivity"  , int

        # --------------------------------------
        # Check x-coord static item
        staticItem = staticItems[1]
        Assert.AreEqual(2, staticItem.ItemNumber)
        Assert.AreEqual(312, staticItem.ElementCount)
        if (
            staticItem.DataType != DfsSimpleType.Double
            and staticItem.DataType != DfsSimpleType.Float
        ):
            Assert.Fail("DataType of X static item mismatch")
        if datamanager:
            Assert.AreEqual(
                "x coordinate", staticItem.Name
            )  # Note: not the same name as default dfsu file! :-(
        else:
            Assert.AreEqual("X-coord", staticItem.Name)

        # Check data - first and last coordinate
        Assert.AreEqual(np.float32(214817.375), staticItem.Data[0])
        Assert.AreEqual(np.float32(223442.266), staticItem.Data[311])

        staticItem = staticItems[2]
        Assert.AreEqual(np.float32(6159041.5), staticItem.Data[0])
        Assert.AreEqual(np.float32(6158791.0), staticItem.Data[311])

        # --------------------------------------
        # Check element type static item
        staticItem = staticItems[6]
        Assert.AreEqual(7, staticItem.ItemNumber)
        Assert.AreEqual(266, staticItem.ElementCount)
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        if datamanager:
            Assert.AreEqual(
                "element code", staticItem.Name
            )  # Note: Not the same as in dfsu file from engine!
        else:
            Assert.AreEqual("Element type", staticItem.Name)

        # Check data - first and last elements
        Assert.AreEqual(25, staticItem.Data[0])
        Assert.AreEqual(25, staticItem.Data[265])

        # --------------------------------------
        # Check connectivity static item
        staticItem = staticItems[8]
        Assert.AreEqual(9, staticItem.ItemNumber)
        Assert.AreEqual(4 * 266, staticItem.ElementCount)
        ##Assert.AreEqual(4 * 266, staticItem.UsedElementCount);
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        if datamanager:
            Assert.AreEqual(
                "indices of nodes in element", staticItem.Name
            )  # Note: Not the same as in dfsu file from engine!
        else:
            Assert.AreEqual("Connectivity", staticItem.Name)

        # Check data - first and last element
        Assert.AreEqual(1, staticItem.Data[0])
        Assert.AreEqual(9, staticItem.Data[1])
        Assert.AreEqual(10, staticItem.Data[2])
        Assert.AreEqual(2, staticItem.Data[3])
        Assert.AreEqual(2, staticItem.Data[4])
        Assert.AreEqual(10, staticItem.Data[5])
        Assert.AreEqual(11, staticItem.Data[6])
        Assert.AreEqual(3, staticItem.Data[7])

    @staticmethod
    def ReadTester(dfsFile):

        # Check that the ReadItemTimeStepNext item round-robin is correct

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(0.0, itemData.Time)
        Assert.AreEqual(312, itemData.Data.size)
        Assert.AreEqual(np.float32(0.369), itemData.Data[7])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(266, itemData.Data.size)
        Assert.AreEqual(np.float32(0), itemData.Data[6])

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(86400, itemData.Time)
        Assert.AreEqual(np.float32(0.0213589743), itemData.Data[7])

        # Salinity
        itemData = dfsFile.ReadItemTimeStep(2, 3)
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(np.float32(1.0e-35), itemData.Data[6])
        Assert.AreEqual(np.float32(0.0682572052), itemData.Data[20])

        # Testing reusing the itemData's
        dfsFile.Reset()

        itemDatas = np.zeros(2, dtype=object)
        for i in range(2):
            itemDatas[i] = dfsFile.ReadItemTimeStep(i + 1, 0)

        for j in range(1, 13):
            for i in range(2):
                itemData = itemDatas[i]
                dfsFile.ReadItemTimeStep(itemData, j)
                Assert.AreEqual(i + 1, itemData.ItemNumber)
                Assert.AreEqual(j * 86400, itemData.Time)

        Assert.AreEqual(np.float32(0.1990469), itemDatas[0].Data[7])
        Assert.AreEqual(np.float32(0.07601847), itemDatas[1].Data[6])

        # Now we are at end of file, check what happens then:
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())


# / <summary>
# / Class with methods to test the content of the
# / file "VerticalProfileSigmaZ.dfsu" which is a
# / vertical profile through a 3D mixed sigma-z
# / dfsu file.
# / </summary>
class FileVerticalProfileSigmaZDfsu:
    @staticmethod
    def FileInfoTester(dfsFile):
        Assert.AreEqual(datetime.datetime(1997, 9, 6), dfsFile.StartDateTime)
        Assert.AreEqual(9, dfsFile.NumberOfTimeSteps)

        Assert.AreEqual(DfsuFileType.DfsuVerticalProfileSigmaZ, dfsFile.DfsuFileType)
        Assert.AreEqual(3, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(8, dfsFile.NumberOfLayers)

        # Check dynamic items
        Assert.AreEqual(2, len(dfsFile.ItemInfo))
        Assert.AreEqual("Z coordinate", dfsFile.ItemInfo[0].Name)
        Assert.AreEqual("Salinity", dfsFile.ItemInfo[1].Name)

        # Check geometry (static items)
        Assert.AreEqual(212, dfsFile.X.size)
        Assert.AreEqual(np.float32(360327.438), dfsFile.X[0])
        Assert.AreEqual(np.float32(368120.2), dfsFile.X[211])

        Assert.AreEqual(166, len(dfsFile.ElementTable))

        topLayerElements = dfsFile.FindTopLayerElements()
        Assert.AreEqual(35, len(topLayerElements))
        Assert.AreEqual(2, topLayerElements[0])
        Assert.AreEqual(118, topLayerElements[23])
        Assert.AreEqual(162, topLayerElements[33])
        Assert.AreEqual(165, topLayerElements[34])

    @staticmethod
    def FileInfoTester(dfsFile):
        fileInfo = dfsFile.FileInfo

        # Assert.AreEqual("", fileInfo.FileTitle);
        # Assert.AreEqual("", fileInfo.ApplicationTitle);
        # Assert.AreEqual(1, fileInfo.ApplicationVersion);
        Assert.AreEqual(2001, fileInfo.DataType)

        # Assert.AreEqual(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
        Assert.AreEqual(StatType.NoStat, fileInfo.StatsType)

        Assert.AreEqual(np.float32(1e-35), fileInfo.DeleteValueFloat)
        Assert.AreEqual(0, fileInfo.DeleteValueByte)
        Assert.AreEqual(-1e-255, fileInfo.DeleteValueDouble)
        Assert.AreEqual(2147483647, fileInfo.DeleteValueInt)
        Assert.AreEqual(2147483647, fileInfo.DeleteValueUnsignedInt)

        Assert.AreEqual(
            TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType
        )
        timeAxis = fileInfo.TimeAxis
        Assert.IsNotNull(timeAxis)
        Assert.AreEqual(eumUnit.eumUsec, timeAxis.TimeUnit)
        Assert.AreEqual(10800, timeAxis.TimeStep)
        Assert.AreEqual(0, timeAxis.StartTimeOffset)
        Assert.AreEqual(9, timeAxis.NumberOfTimeSteps)

    @staticmethod
    def CustomBlockTester(dfsFile):
        fileInfo = dfsFile.FileInfo

        Assert.AreEqual(1, len(fileInfo.CustomBlocks))

        customBlock = fileInfo.CustomBlocks[0]
        Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType)
        Assert.AreEqual("MIKE_FM", customBlock.Name)
        Assert.AreEqual(5, customBlock.Count)
        Assert.AreEqual(212, customBlock[0])
        Assert.AreEqual(166, customBlock[1])
        Assert.AreEqual(2, customBlock[2])
        Assert.AreEqual(8, customBlock[3])
        Assert.AreEqual(3, customBlock[4])

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):

        Assert.IsNotNull(dynamicItemInfos)
        Assert.AreEqual(2, len(dynamicItemInfos))

        # Check dynamic info
        itemInfo = dynamicItemInfos[0]
        Assert.AreEqual(212, itemInfo.ElementCount)
        Assert.AreEqual(eumItem.eumIItemGeometry3D, itemInfo.Quantity.Item)
        Assert.AreEqual(eumUnit.eumUmeter, itemInfo.Quantity.Unit)
        Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType)
        Assert.AreEqual("Z coordinate", itemInfo.Name)
        Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType)

        # Check spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, itemInfo.SpatialAxis.AxisType)
        axis = itemInfo.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit)
        Assert.AreEqual(212, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check dynamic info
        itemInfo = dynamicItemInfos[1]
        Assert.AreEqual(166, itemInfo.ElementCount)
        Assert.AreEqual(eumItem.eumISalinity, itemInfo.Quantity.Item)
        Assert.AreEqual(eumUnit.eumUPSU, itemInfo.Quantity.Unit)
        Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType)
        Assert.AreEqual("Salinity", itemInfo.Name)
        Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType)

        # Check spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, itemInfo.SpatialAxis.AxisType)
        axis = itemInfo.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit)
        Assert.AreEqual(166, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

    @staticmethod
    def StaticItemTester(dfsFile, datamanager):
        staticItems = []

        staticItemNumber = 1
        while True:
            varstaticItem = dfsFile.ReadStaticItem(staticItemNumber)
            if varstaticItem is None:
                break
            staticItems.append(varstaticItem)
            staticItemNumber += 1

        Assert.IsNotNull(staticItems)
        Assert.AreEqual(9, len(staticItems))

        # / Static items in a dfsu file:
        # / "Node id"       , int
        # / "X-coord"       , float
        # / "Y-coord"       , float
        # / "Z-coord"       , float
        # / "Code"          , int
        # / "Element id"    , int
        # / "Element type"  , int
        # / "No of nodes"   , int
        # / "Connectivity"  , int

        deleteValueFloat = np.float32(-1.00000002e-35)

        # --------------------------------------
        # Check x-coord static item
        staticItem = staticItems[1]
        Assert.AreEqual(2, staticItem.ItemNumber)
        Assert.AreEqual(212, staticItem.ElementCount)
        # Assert.AreEqual(212, staticItem.UsedElementCount);

        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIGeographicalCoordinate == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUmeter, staticItem.Quantity.Unit)
        else:
            Assert.Fail("X coordinate axis item type mismatch")

        if (
            staticItem.DataType != DfsSimpleType.Double
            and staticItem.DataType != DfsSimpleType.Float
        ):
            Assert.Fail("DataType of X static item mismatch")
        if datamanager:
            Assert.AreEqual(
                "x coordinate", staticItem.Name
            )  # Note: not the same name as default dfsu file! :-(
        else:
            Assert.AreEqual("X-coord", staticItem.Name)

        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateX)
        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateY)
        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateZ)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationAlpha)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationPhi)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationTheta)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUUnitUndefined, axis.AxisUnit)
        Assert.AreEqual(212, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check data - first and last coordinate
        Assert.AreEqual(np.float32(360327.438), staticItem.Data[0])
        Assert.AreEqual(np.float32(368120.2), staticItem.Data[211])

        # --------------------------------------
        # Check element type static item
        staticItem = staticItems[6]
        Assert.AreEqual(7, staticItem.ItemNumber)
        Assert.AreEqual(166, staticItem.ElementCount)
        # Assert.AreEqual(166, staticItem.UsedElementCount);
        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIIntegerCode == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit)
        else:
            Assert.Fail("Element type static item type mismatch")
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        if datamanager:
            Assert.AreEqual(
                "element code", staticItem.Name
            )  # Note: Not the same as in dfsu file from engine!
        else:
            Assert.AreEqual("Element type", staticItem.Name)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(166, axis.XCount)

        # Check data - first and last elements
        Assert.AreEqual(25, staticItem.Data[0])
        Assert.AreEqual(25, staticItem.Data[165])

        # --------------------------------------
        # Check connectivity static item
        staticItem = staticItems[8]
        Assert.AreEqual(9, staticItem.ItemNumber)
        Assert.AreEqual(4 * 166, staticItem.ElementCount)
        # Assert.AreEqual(4 * 166, staticItem.UsedElementCount);
        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIIntegerCode == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit)
        else:
            Assert.Fail("Connectivity item type mismatch")
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        if datamanager:
            Assert.AreEqual(
                "indices of nodes in element", staticItem.Name
            )  # Note: Not the same as in dfsu file from engine!
        else:
            Assert.AreEqual("Connectivity", staticItem.Name)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUUnitUndefined, axis.AxisUnit)
        Assert.AreEqual(4 * 166, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check data - first and last element
        Assert.AreEqual(1, staticItem.Data[0])
        Assert.AreEqual(5, staticItem.Data[1])
        Assert.AreEqual(6, staticItem.Data[2])
        Assert.AreEqual(2, staticItem.Data[3])
        Assert.AreEqual(207, staticItem.Data[4 * 166 - 4])
        Assert.AreEqual(211, staticItem.Data[4 * 166 - 3])
        Assert.AreEqual(212, staticItem.Data[4 * 166 - 2])
        Assert.AreEqual(208, staticItem.Data[4 * 166 - 1])

    @staticmethod
    def ReadTester(dfsFile):

        # Check that the ReadItemTimeStepNext item round-robin is correct

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(0.0, itemData.Time)
        Assert.AreEqual(212, itemData.Data.size)
        Assert.AreEqual(np.float32(0), itemData.Data[3])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(166, itemData.Data.size)
        Assert.AreEqual(np.float32(21.2441158), itemData.Data[71])

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(10800, itemData.Time)
        Assert.AreEqual(np.float32(0.0669299588), itemData.Data[3])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(np.float32(21.5351353), itemData.Data[71])

        # Testing reusing the itemData's
        itemDatas = np.zeros(6, dtype=object)
        for i in range(2):
            itemDatas[i] = dfsFile.ReadItemTimeStep(i + 1, 0)

        for j in range(1, 9):
            for i in range(2):
                itemData = itemDatas[i]
                dfsFile.ReadItemTimeStep(itemData, j)
                Assert.AreEqual(i + 1, itemData.ItemNumber)
                Assert.AreEqual(j * 10800, itemData.Time)

        Assert.AreEqual(np.float32(0.131808951), itemDatas[0].Data[3])
        Assert.AreEqual(np.float32(24.6949234), itemDatas[1].Data[71])

        # Now we are at end of file, check what happens then:
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())


# / <summary>
# / Class with methods to test the content of the
# / file "VerticalColumn.dfsu" which is a
# / vertical column through a 3D mixed sigma-z
# / dfsu file.
# / </summary>
class FileVerticalColumnDfsu:
    @staticmethod
    def FileInfoTester(dfsFile):
        Assert.AreEqual(datetime.datetime(1997, 9, 6), dfsFile.StartDateTime)
        Assert.AreEqual(9, dfsFile.NumberOfTimeSteps)

        Assert.AreEqual(DfsuFileType.DfsuVerticalColumn, dfsFile.DfsuFileType)
        Assert.AreEqual(3, dfsFile.NumberOfSigmaLayers)
        Assert.AreEqual(10, dfsFile.NumberOfLayers)

        # Check dynamic items
        Assert.AreEqual(2, len(dfsFile.ItemInfo))
        Assert.AreEqual("Z coordinate", dfsFile.ItemInfo[0].Name)
        Assert.AreEqual("Salinity", dfsFile.ItemInfo[1].Name)

        # Check geometry (static items)
        Assert.AreEqual(11, dfsFile.X.size)
        Assert.AreEqual(np.float32(363808.125), dfsFile.X[0])
        Assert.AreEqual(np.float32(363808.125), dfsFile.X[10])

        Assert.AreEqual(10, len(dfsFile.ElementTable))

        topLayerElements = dfsFile.FindTopLayerElements()
        Assert.AreEqual(1, len(topLayerElements))
        Assert.AreEqual(9, topLayerElements[0])

    @staticmethod
    def FileInfoTester(dfsFile):
        fileInfo = dfsFile.FileInfo

        # Assert.AreEqual("", fileInfo.FileTitle);
        # Assert.AreEqual("", fileInfo.ApplicationTitle);
        # Assert.AreEqual(1, fileInfo.ApplicationVersion);
        Assert.AreEqual(2001, fileInfo.DataType)

        # Assert.AreEqual(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
        Assert.AreEqual(StatType.NoStat, fileInfo.StatsType)

        Assert.AreEqual(np.float32(1e-35), fileInfo.DeleteValueFloat)
        Assert.AreEqual(0, fileInfo.DeleteValueByte)
        Assert.AreEqual(-1e-255, fileInfo.DeleteValueDouble)
        Assert.AreEqual(2147483647, fileInfo.DeleteValueInt)
        Assert.AreEqual(2147483647, fileInfo.DeleteValueUnsignedInt)

        Assert.AreEqual(
            TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType
        )
        timeAxis = fileInfo.TimeAxis
        Assert.IsNotNull(timeAxis)
        Assert.AreEqual(eumUnit.eumUsec, timeAxis.TimeUnit)
        Assert.AreEqual(10800, timeAxis.TimeStep)
        Assert.AreEqual(0, timeAxis.StartTimeOffset)
        Assert.AreEqual(9, timeAxis.NumberOfTimeSteps)

    @staticmethod
    def CustomBlockTester(dfsFile):
        fileInfo = dfsFile.FileInfo

        Assert.AreEqual(1, len(fileInfo.CustomBlocks))

        customBlock = fileInfo.CustomBlocks[0]
        Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType)
        Assert.AreEqual("MIKE_FM", customBlock.Name)
        Assert.AreEqual(5, customBlock.Count)
        Assert.AreEqual(11, customBlock[0])
        Assert.AreEqual(10, customBlock[1])
        Assert.AreEqual(1, customBlock[2])
        Assert.AreEqual(10, customBlock[3])
        Assert.AreEqual(3, customBlock[4])

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):

        Assert.IsNotNull(dynamicItemInfos)
        Assert.AreEqual(2, len(dynamicItemInfos))

        # Check dynamic info
        itemInfo = dynamicItemInfos[0]
        Assert.AreEqual(11, itemInfo.ElementCount)
        Assert.AreEqual(eumItem.eumIItemGeometry3D, itemInfo.Quantity.Item)
        Assert.AreEqual(eumUnit.eumUmeter, itemInfo.Quantity.Unit)
        Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType)
        Assert.AreEqual("Z coordinate", itemInfo.Name)
        Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType)

        # Check spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, itemInfo.SpatialAxis.AxisType)
        axis = itemInfo.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit)
        Assert.AreEqual(11, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check dynamic info
        itemInfo = dynamicItemInfos[1]
        Assert.AreEqual(10, itemInfo.ElementCount)
        Assert.AreEqual(eumItem.eumISalinity, itemInfo.Quantity.Item)
        Assert.AreEqual(eumUnit.eumUPSU, itemInfo.Quantity.Unit)
        Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType)
        Assert.AreEqual("Salinity", itemInfo.Name)
        Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType)

        # Check spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, itemInfo.SpatialAxis.AxisType)
        axis = itemInfo.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit)
        Assert.AreEqual(10, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        repr(itemInfo)  # only requirement is to not fail

    @staticmethod
    def StaticItemTester(dfsFile, datamanager):
        staticItems = []

        staticItemNumber = 1
        while True:
            varstaticItem = dfsFile.ReadStaticItem(staticItemNumber)
            if varstaticItem is None:
                break
            staticItems.append(varstaticItem)
            staticItemNumber += 1

        Assert.IsNotNull(staticItems)
        Assert.AreEqual(9, len(staticItems))

        # / Static items in a dfsu file:
        # / "Node id"       , int
        # / "X-coord"       , float
        # / "Y-coord"       , float
        # / "Z-coord"       , float
        # / "Code"          , int
        # / "Element id"    , int
        # / "Element type"  , int
        # / "No of nodes"   , int
        # / "Connectivity"  , int

        deleteValueFloat = np.float32(-1.00000002e-35)

        # --------------------------------------
        # Check x-coord static item
        staticItem = staticItems[1]
        Assert.AreEqual(2, staticItem.ItemNumber)
        Assert.AreEqual(11, staticItem.ElementCount)
        # Assert.AreEqual(11, staticItem.UsedElementCount);

        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIGeographicalCoordinate == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUmeter, staticItem.Quantity.Unit)
        else:
            Assert.Fail("X coordinate axis item type mismatch")

        if (
            staticItem.DataType != DfsSimpleType.Double
            and staticItem.DataType != DfsSimpleType.Float
        ):
            Assert.Fail("DataType of X static item mismatch")
        if datamanager:
            Assert.AreEqual(
                "x coordinate", staticItem.Name
            )  # Note: not the same name as default dfsu file! :-(
        else:
            Assert.AreEqual("X-coord", staticItem.Name)

        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateX)
        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateY)
        Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateZ)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationAlpha)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationPhi)
        Assert.AreEqual(deleteValueFloat, staticItem.OrientationTheta)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUUnitUndefined, axis.AxisUnit)
        Assert.AreEqual(11, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check data - first and last coordinate
        Assert.AreEqual(np.float32(363808.125), staticItem.Data[0])
        Assert.AreEqual(np.float32(363808.125), staticItem.Data[10])

        # --------------------------------------
        # Check element type static item
        staticItem = staticItems[6]
        Assert.AreEqual(7, staticItem.ItemNumber)
        Assert.AreEqual(10, staticItem.ElementCount)
        # Assert.AreEqual(10, staticItem.UsedElementCount);
        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIIntegerCode == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit)
        else:
            Assert.Fail("Element Type static item type mismatch")
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        if datamanager:
            Assert.AreEqual(
                "element code", staticItem.Name
            )  # Note: Not the same as in dfsu file from engine!
        else:
            Assert.AreEqual("Element type", staticItem.Name)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(10, axis.XCount)

        # Check data - first and last elements
        Assert.AreEqual(11, staticItem.Data[0])
        Assert.AreEqual(11, staticItem.Data[9])

        # --------------------------------------
        # Check connectivity static item
        staticItem = staticItems[8]
        Assert.AreEqual(9, staticItem.ItemNumber)
        Assert.AreEqual(20, staticItem.ElementCount)
        # Assert.AreEqual(20, staticItem.UsedElementCount);
        if eumItem.eumIItemUndefined == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit)
        elif eumItem.eumIIntegerCode == staticItem.Quantity.Item:
            Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit)
        else:
            Assert.Fail("Connectivity item type mismatch")
        Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType)
        if datamanager:
            Assert.AreEqual(
                "indices of nodes in element", staticItem.Name
            )  # Note: Not the same as in dfsu file from engine!
        else:
            Assert.AreEqual("Connectivity", staticItem.Name)

        # Check dummy spatial axis
        Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType)
        axis = staticItem.SpatialAxis
        Assert.IsNotNull(axis)
        Assert.AreEqual(1, axis.Dimension)
        Assert.AreEqual(eumUnit.eumUUnitUndefined, axis.AxisUnit)
        Assert.AreEqual(20, axis.XCount)
        Assert.AreEqual(0, axis.X0)
        Assert.AreEqual(1, axis.Dx)

        # Check data - first and last elements
        Assert.AreEqual(1, staticItem.Data[0])
        Assert.AreEqual(2, staticItem.Data[1])
        Assert.AreEqual(2, staticItem.Data[2])
        Assert.AreEqual(3, staticItem.Data[3])
        Assert.AreEqual(10, staticItem.Data[17])
        Assert.AreEqual(10, staticItem.Data[18])
        Assert.AreEqual(11, staticItem.Data[19])

    @staticmethod
    def ReadTester(dfsFile):

        # Check that the ReadItemTimeStepNext item round-robin is correct

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(0.0, itemData.Time)
        Assert.AreEqual(11, itemData.Data.size)
        Assert.AreEqual(np.float32(-1.0), itemData.Data[9])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(10, itemData.Data.size)
        Assert.AreEqual(np.float32(23.907732), itemData.Data[8])

        # Z-coordinate
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(1, itemData.ItemNumber)
        Assert.AreEqual(10800, itemData.Time)
        Assert.AreEqual(np.float32(-0.9590657), itemData.Data[9])

        # Salinity
        itemData = dfsFile.ReadItemTimeStepNext()
        Assert.AreEqual(2, itemData.ItemNumber)
        Assert.AreEqual(np.float32(23.955143), itemData.Data[8])

        # Testing reusing the itemData's
        itemDatas = np.zeros(6, dtype=object)
        for i in range(2):
            itemDatas[i] = dfsFile.ReadItemTimeStep(i + 1, 0)

        for j in range(1, 9):
            for i in range(2):
                itemData = itemDatas[i]
                dfsFile.ReadItemTimeStep(itemData, j)
                Assert.AreEqual(i + 1, itemData.ItemNumber)
                Assert.AreEqual(j * 10800, itemData.Time)

        Assert.AreEqual(np.float32(-0.9001775), itemDatas[0].Data[9])
        Assert.AreEqual(np.float32(24.9080048), itemDatas[1].Data[8])

        # Now we are at end of file, check what happens then:
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())
        Assert.IsNull(dfsFile.ReadItemTimeStepNext())


@pytest.mark.parametrize(
    "filename, fileType, value",
    [
        ("testdata/OresundHD.dfsu", DfsuFileType.Dfsu2D, 2),
        ("testdata/VerticalColumn.dfsu", DfsuFileType.DfsuVerticalColumn, 3),
        (
            "testdata/VerticalProfileSigma.dfsu",
            DfsuFileType.DfsuVerticalProfileSigma,
            4,
        ),
        (
            "testdata/VerticalProfileSigmaZ.dfsu",
            DfsuFileType.DfsuVerticalProfileSigmaZ,
            5,
        ),
        ("testdata/OdenseHD3D.dfsu", DfsuFileType.Dfsu3DSigma, 6),
        ("testdata/Oresund3DSigmaZ.dfsu", DfsuFileType.Dfsu3DSigmaZ, 7),
    ],
)
def test_DfsuFileType_of_file(filename, fileType, value):
    dfsu = DfsuFile.Open(filename)
    dfsuFileType = dfsu.DfsuFileType
    dfsu.Close()

    assert fileType is dfsuFileType
    # The value of the MIKE Core DfsuFileType enum
    assert value == dfsuFileType
