import unittest
from datetime import datetime
from mikecore.DfsFileFactory import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *
from numpy.testing import *
from tests.examples_dfs2 import *
from tests.test_util import *


class Dfs2Tests(unittest.TestCase):
    '''
    Class for testing functionality related to dfs2 files.
    '''

    def test_FirstExample(self):
        # Name of the file to open
        filename = "testdata/OresundHD.dfs2";
        ExamplesDfs2.ReadingDfs2File(filename);

    def test_ModifyDfs2Bathymetry(self):
        sourceFilename = "testdata/OresundBathy900.dfs2";
        filename = "testdata/testtmp/test_updated_OresundBathy900.dfs2";
        #ExamplesMisc.CopyDfsFile(sourceFilename, filename);
        testUtil.copy_file(sourceFilename, filename);
        ExamplesDfs2.ModifyDfs2Bathymetry(filename);


    def test_ReadOresundHDTest(self):

        filename = "testdata/OresundHD.dfs2";

        # Load as Dfs2 file
  
        dfs2File = DfsFileFactory.Dfs2FileOpen(filename);
        FileOresundHDDfs2.FileInfoTester(dfs2File.FileInfo);
        FileOresundHDDfs2.CustomBlockTester(dfs2File.FileInfo.CustomBlocks);
        FileOresundHDDfs2.StaticItemTester(dfs2File);
        FileOresundHDDfs2.DynamicItemTester(dfs2File.ItemInfo);
        FileOresundHDDfs2.ReadTester2D(dfs2File);
        dfs2File.Close();

        # Load as generic Dfs file
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileOresundHDDfs2.FileInfoTester(dfsFile.FileInfo);
        FileOresundHDDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileOresundHDDfs2.StaticItemTester(dfsFile);
        FileOresundHDDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileOresundHDDfs2.ReadTester(dfsFile);
        dfsFile.Close();

        #ExamplesDfs2.GetjkIndexForGeoCoordinate(filename);

    def test_ReadOresundBathy900Test(self):
        filename = "testdata/OresundBathy900.dfs2";
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileOresundBathy900Dfs2.FileInfoTester(dfsFile);
        FileOresundBathy900Dfs2.CustomBlockTester(dfsFile);
        FileOresundBathy900Dfs2.StaticItemTester(dfsFile);
        FileOresundBathy900Dfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileOresundBathy900Dfs2.ReadTester(dfsFile);

    def test_ReadLanduseTest(self):
        filename = "testdata/Landuse.dfs2";
        # Load as Dfs2File
        dfsFile = DfsFileFactory.Dfs2FileOpen(filename);
        FileLanduseDfs2.FileInfoTester(dfsFile.FileInfo);
        FileLanduseDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileLanduseDfs2.StaticItemTester(dfsFile);
        FileLanduseDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileLanduseDfs2.ReadTester2D(dfsFile);

        # Load as generic Dfs
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileLanduseDfs2.FileInfoTester(dfsFile.FileInfo);
        FileLanduseDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileLanduseDfs2.StaticItemTester(dfsFile);
        FileLanduseDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileLanduseDfs2.ReadTester(dfsFile);


    def test_CreateOresundHDTest(self):

        sourceFilename = "testdata/OresundHD.dfs2";
        filename       = "testdata/testtmp/test_create_OresundHD.dfs2";

        ExamplesDfs2.CreateDfs2File(sourceFilename, filename);

        # Check the content of the file
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileOresundHDDfs2.FileInfoTester(dfsFile.FileInfo);
        FileOresundHDDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileOresundHDDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileOresundHDDfs2.StaticItemTester(dfsFile);
        FileOresundHDDfs2.ReadTester(dfsFile);
        dfsFile.Close();

        # Check the content of the file
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileOresundHDDfs2.FileInfoTester(dfsFile.FileInfo);
        FileOresundHDDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileOresundHDDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileOresundHDDfs2.StaticItemTester(dfsFile);
        FileOresundHDDfs2.ReadTester(dfsFile);
        dfsFile.Close();

#    def CopyOresundHDTest():
#
#        sourceFilename = "testdata/OresundHD.dfs2";
#        filename = "testdata/testtmp/test_copy_OresundHD.dfs2";
#
#        ExamplesMisc.CopyDfsFile(sourceFilename, filename);
#
#        # Check the content of the file
#        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
#        FileOresundHDDfs2.FileInfoTester(dfsFile.FileInfo);
#        FileOresundHDDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
#        FileOresundHDDfs2.DynamicItemTester(dfsFile.ItemInfo);
#        FileOresundHDDfs2.StaticItemTester(dfsFile);
#        FileOresundHDDfs2.ReadTester(dfsFile);
#        dfsFile.Close();

#    def MergeOresundHDTest():
#        sourceFilename = "testdata/OresundHD.dfs2";
#        targetFilename = "testdata/testtmp/test_merge_OresundHD.dfs2";
#
#        sources = []
#        sources.append(sourceFilename);
#        sources.append(sourceFilename);
#
#        ExamplesMisc.MergeDfsFileItems(targetFilename, sources);


    def test_CreateLanduseTest(self):

        sourceFilename = "testdata/Landuse.dfs2";
        filename = "testdata/testtmp/test_create_Landuse.dfs2";

        source = DfsFileFactory.Dfs2FileOpen(sourceFilename);

        factory = DfsFactory();
        builder = DfsBuilder.Create("File Title", "Grid editor", 1);

        # Set up the header
        builder.SetDataType(0);
        builder.SetGeographicalProjection(factory.CreateProjectionGeoOrigin("NON-UTM", 0,0,0));
        builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(2000,  1,  1, 10, 0, 0), 0, 1));
        builder.SetSpatialAxis(factory.CreateAxisEqD2(eumUnit.eumUmeter, 62, 0, 500, 70, 0, 500));
        builder.DeleteValueFloat = -2;

        # Set up dynamic items
        builder.AddCreateDynamicItem("Landuse", eumQuantity.Create(eumItem.eumIIntegerCode, eumUnit.eumUintCode), DfsSimpleType.Float, DataValueType.Instantaneous);

        # Create and get file
        builder.CreateFile(filename);
        file = builder.GetFile();

        # Add data for all item-timesteps
        while (True):
            sourceData = source.ReadItemTimeStepNext()
            if (sourceData == None):
                break;
            file.WriteItemTimeStepNext(sourceData.Time, sourceData.Data);

        source.Close();
        file.Close();

        # Check the content of the file
        # Load as generic Dfs

        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileLanduseDfs2.FileInfoTester(dfsFile.FileInfo);
        FileLanduseDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileLanduseDfs2.StaticItemTester(dfsFile);
        FileLanduseDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileLanduseDfs2.ReadTester(dfsFile);

        # Load as Dfs2File

        dfsFile = DfsFileFactory.Dfs2FileOpen(filename);
        FileLanduseDfs2.ReadTester2D(dfsFile);





    def test_CreateOresundBathy900Test(self):

        sourceFilename = "testdata/OresundBathy900.dfs2";
        filename = "testdata/testtmp/test_create_OresundBathy900.dfs2";

        source = DfsFileFactory.Dfs2FileOpen(sourceFilename);
        sourceData = source.ReadItemTimeStepNext()
        if (None == sourceData):
            raise Exception("Could not read bathymetry data");
        bathyDataArray = sourceData.Data;
        source.Close();

        ExamplesDfs2.CreateM21Bathymetry(bathyDataArray, filename);

        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        FileOresundBathy900Dfs2.FileInfoTester(dfsFile);
        FileOresundBathy900Dfs2.CustomBlockTester(dfsFile);
        FileOresundBathy900Dfs2.StaticItemTester(dfsFile);
        FileOresundBathy900Dfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileOresundBathy900Dfs2.ReadTester(dfsFile);

#    def ModifyAxisTest():
#        originalFilename = "testdata/OresundHD.dfs2";
#        filename = "testdata/testtmp/test_modifyAxis_OresundHD.dfs2";
#
#        testUtil.copy_file(originalFilename, filename)
#
#        ExamplesDfs2.ModifyDfs2ItemAxis(filename);
#
#        # Check all dynamic items
#        dfs2File = DfsFileFactory.DfsGenericOpen(filename);
#        for itemInfo in dfs2File.ItemInfo:
#            axisEqD2 = itemInfo.SpatialAxis;
#            assert_equal( 55, axisEqD2.X0);
#            assert_equal(905, axisEqD2.Dx);
#            assert_equal(-55, axisEqD2.Y0);
#            assert_equal(915, axisEqD2.Dy);
#
#        # Check all static items
#        while (True):
#            staticItem = dfs2File.ReadStaticItemNext()
#            if (staticItem == None):
#                break;
#            axisEqD2 = staticItem.SpatialAxis;
#            assert_equal( 55, axisEqD2.X0);
#            assert_equal(905, axisEqD2.Dx);
#            assert_equal(-55, axisEqD2.Y0);
#            assert_equal(915, axisEqD2.Dy);
#
#        dfs2File.Close();

#    def ModifyLanduseItemInfoTest():
#
#        originalFilename = "testdata/Landuse.dfs2";
#        filename = "testdata/testtmp/test_create_Landuse.dfs2";
#
#        File.Copy(originalFilename, filename, true);
#        File.SetAttributes(filename, FileAttributes.Normal); # remove read-only flag
#
#        # Check the new file
#  
#        file = DfsFileFactory.Dfs2FileOpen(filename);
#
#        # Check existing data
#        itemInfo = file.ItemInfo[0];
#        assert_equal("Landuse", itemInfo.Name);
#        assert_equal(eumItem.eumIIntegerCode, itemInfo.Quantity.Item);
#        assert_equal(eumUnit.eumUintCode, itemInfo.Quantity.Unit);
#
#        file.Close();
#
#        # Method that modifies the Landuse.dfs2 file
#        ExamplesDfs2.ModifyDfs2ItemInfo(filename);
#
#        # Check the new file
#        file = DfsFileFactory.Dfs2FileOpen(filename);
#
#        # Check existing data
#        itemInfo = file.ItemInfo[0];
#        assert_equal("GroundU", itemInfo.Name);
#        assert_equal(eumItem.eumIAreaFraction, itemInfo.Quantity.Item);
#        assert_equal(eumUnit.eumUPerCent, itemInfo.Quantity.Unit);
#
#        file.Close();

    def test_ModifyLanduseDataTest(self):

        originalFilename = "testdata/Landuse.dfs2";
        filename = "testdata/testtmp/test_modify_Landuse.dfs2";

        testUtil.copy_file(originalFilename, filename);

        # Method that modifies the Landuse.dfs2 file
        ExamplesDfs2.ModifyDfs2FileData(filename);

        # Check the new file
  
        file = DfsFileFactory.Dfs2FileOpen(filename);

        # Check the new data
        data2D = file.ReadItemTimeStepNext(reshape = True);
        assert_equal(7, data2D.Data[21, 61]);
        assert_equal(6, data2D.Data[21, 62]);
        assert_equal(5, data2D.Data[21, 63]);
        assert_equal(4, data2D.Data[21, 64]);
        assert_equal(3, data2D.Data[21, 65]);

        file.Close();

    def test_CreateOresundHDGenericTest(self):

        sourceFilename = "testdata/OresundHD.dfs2";
        filename = "testdata/testtmp/test_create_OresundHD.dfs2";

        source = DfsFileFactory.DfsGenericOpen(sourceFilename);

        factory = DfsFactory();
        builder = DfsBuilder.Create("", r"C:\Program Files\DHI\2010\bin\nmodel.exe", 0);

        # Build header
        builder.SetDataType(1);
        builder.SetGeographicalProjection(factory.CreateProjectionGeoOrigin("UTM-33", 12.438741600559766, 55.225707842436385, 326.99999999999955));
        builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(1993, 12,  2, 0, 0, 0), 0, 86400));
        builder.DeleteValueFloat = -1e-30;

        builder.AddCreateCustomBlock("M21_Misc", np.array([ 327, 0.2, -900, 10, 0, 0, 0 ], np.float32));

        # Set up items
        itemBuilders = []

        item = builder.CreateDynamicItemBuilder();
        item.Set("H Water Depth m", eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter), DfsSimpleType.Float);
        itemBuilders.append(item);

        item = builder.CreateDynamicItemBuilder();
        item.Set("P Flux m^3/s/m", eumQuantity.Create(eumItem.eumIFlowFlux, eumUnit.eumUm3PerSecPerM), DfsSimpleType.Float);
        itemBuilders.append(item);

        item = builder.CreateDynamicItemBuilder();
        item.Set("Q Flux m^3/s/m", eumQuantity.Create(eumItem.eumIFlowFlux, eumUnit.eumUm3PerSecPerM), DfsSimpleType.Float);
        itemBuilders.append(item);

        axisEqD2 = factory.CreateAxisEqD2(eumUnit.eumUmeter, 71, 0, 900, 91, 0, 900);

        for varItem in itemBuilders:
            varItem.SetValueType(DataValueType.Instantaneous);
            varItem.SetAxis(axisEqD2);
            # Set to default ufs delete values (not used anyway, just to make file exactly equal)
            varItem.SetReferenceCoordinates(-1e-35, -1e-35, -1e-35);
            varItem.SetOrientation(-1e-35, -1e-35, -1e-35);
            builder.AddDynamicItem(varItem.GetDynamicItemInfo());
    

        builder.CreateFile(filename);

        # Add static items

        # Static item containing bathymetri data
        sourceStaticItem = source.ReadStaticItemNext();
        assert_equal(DfsSimpleType.Float, sourceStaticItem.DataType);
        staticItemBuilder = builder.CreateStaticItemBuilder();
        staticItemBuilder.Set(sourceStaticItem.Name, eumQuantity.UnDefined(), DfsSimpleType.Float);
        staticItemBuilder.SetAxis(axisEqD2);
        staticItemBuilder.SetData(sourceStaticItem.Data);
        staticItem = staticItemBuilder.GetStaticItem();
        builder.AddStaticItem(staticItem);

        # Get file
        file = builder.GetFile();

        # Add data for all item-timesteps
        while (True):
            sourceData = source.ReadItemTimeStepNext()
            if (sourceData == None):
                break;
            file.WriteItemTimeStepNext(sourceData.Time, sourceData.Data);

        source.Close();
        file.Close();

        # Check the content of the file
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);

        FileOresundHDDfs2.FileInfoTester(dfsFile.FileInfo);
        FileOresundHDDfs2.CustomBlockTester(dfsFile.FileInfo.CustomBlocks);
        FileOresundHDDfs2.DynamicItemTester(dfsFile.ItemInfo);
        FileOresundHDDfs2.StaticItemTester(dfsFile);
        FileOresundHDDfs2.ReadTester(dfsFile);

        dfsFile.Close();


class FileOresundBathy900Dfs2:

    @staticmethod
    def FileInfoTester(dfsFile):

        fileInfo = dfsFile.FileInfo;

        assert_equal(r"C:\0\Training\Bat1_0.dfs2", fileInfo.FileTitle);
        assert_equal(r"Grid editor", fileInfo.ApplicationTitle);
        assert_equal(1, fileInfo.ApplicationVersion);
        assert_equal(0, fileInfo.DataType);

        #assert_equal(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
        assert_equal(StatType.NoStat, fileInfo.StatsType);

        assert_equal(TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType);
        time = fileInfo.TimeAxis;
        assert_equal(datetime.datetime(2003,  1,  1, 0, 0, 0), time.StartDateTime);
        assert_equal(1, time.NumberOfTimeSteps);
        assert_equal(0, time.StartTimeOffset);
        assert_equal(1, time.TimeStep);
        assert_equal(eumUnit.eumUsec, time.TimeUnit);
        assert_equal(0, time.FirstTimeStepIndex);

        assert_equal(np.float32(-1e-30), fileInfo.DeleteValueFloat);
        assert_equal(0, fileInfo.DeleteValueByte);
        assert_equal(-1e-255, fileInfo.DeleteValueDouble);
        assert_equal(2147483647, fileInfo.DeleteValueInt);
        assert_equal(2147483647, fileInfo.DeleteValueUnsignedInt);

        assert_equal("UTM-33", fileInfo.Projection.WKTString);
        assert_equal(12.438741600559911, fileInfo.Projection.Longitude);
        assert_equal(55.2257078424238, fileInfo.Projection.Latitude);
        assert_allclose(327, fileInfo.Projection.Orientation, 1e-12);


    @staticmethod
    def CustomBlockTester(dfsFile):

        fileInfo = dfsFile.FileInfo;

        assert_equal(2, len(fileInfo.CustomBlocks));

        customBlock = fileInfo.CustomBlocks[0];
        assert_equal("Display Settings", customBlock.Name);
        assert_equal(DfsSimpleType.Int, customBlock.SimpleType);
        assert_allclose(3, customBlock.Count, 1e-23);
        assert_equal(1, customBlock[0]);
        assert_equal(0, customBlock[1]);
        assert_equal(0, customBlock[2]);

        customBlock = fileInfo.CustomBlocks[1];
        assert_equal("M21_Misc", customBlock.Name);
        assert_equal(DfsSimpleType.Float, customBlock.SimpleType);
        assert_allclose(7, customBlock.Count, 1e-23);
        assert_allclose(327, customBlock[0], 1e-23);
        assert_allclose(0, customBlock[1], 1e-5);
        assert_allclose(-900, customBlock[2], 1e-4);
        assert_equal(10, customBlock[3]);
        assert_equal(0, customBlock[4]);
        assert_equal(0, customBlock[5]);
        assert_equal(0, customBlock[6]);

    @staticmethod
    def StaticItemTester(dfsFile):

        staticItem = dfsFile.ReadStaticItemNext();
        assert None == staticItem;

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):

        assert_equal(1, len(dynamicItemInfos));

        # Check dynamic info
        itemInfo = dynamicItemInfos[0];
        assert_equal(72 * 94, itemInfo.ElementCount);
        assert_equal(eumItem.eumIWaterLevel, itemInfo.Quantity.Item);
        assert_equal(eumUnit.eumUmeter, itemInfo.Quantity.Unit);
        assert_equal(DfsSimpleType.Float, itemInfo.DataType);
        assert_equal("Bathymetry", itemInfo.Name);
        assert_equal(DataValueType.Instantaneous, itemInfo.ValueType);

        # Check spatial axis for all items
        for varItemInfo in dynamicItemInfos:
            assert_equal(SpaceAxisType.EqD2, varItemInfo.SpatialAxis.AxisType);
            axis = varItemInfo.SpatialAxis;
            assert_equal(2, axis.Dimension);
            assert_equal(eumUnit.eumUmeter, axis.AxisUnit);
            assert_equal(72, axis.XCount);
            assert_equal(94, axis.YCount);
            assert_equal(0, axis.X0);
            assert_equal(0, axis.X0);
            assert_equal(900, axis.Dx);
            assert_equal(900, axis.Dy);

  

    @staticmethod
    def ReadTester(dfsFile):

        itemData = dfsFile.ReadItemTimeStepNext();
        floatData = itemData;
        floatArr = floatData.Data;
        # Check first row
        assert_equal(np.float32(10), floatArr[0]);
        assert_equal(np.float32(-15.9582891), floatArr[1]);
        assert_equal(np.float32(-19.18562), floatArr[2]);
        # Check second row
        assert_equal(np.float32(10), floatArr[0 + 72]);
        assert_equal(np.float32(-16.3214531), floatArr[1 + 72]);
        assert_equal(np.float32(-18.7345638), floatArr[2 + 72]);


class FileOresundHDDfs2:

    @staticmethod
    def FileInfoTester(fileInfo):


        assert_equal("", fileInfo.FileTitle);
        assert_equal(r"C:\Program Files\DHI\2010\bin\nmodel.exe", fileInfo.ApplicationTitle);
        assert_equal(0, fileInfo.ApplicationVersion);
        assert_equal(1, fileInfo.DataType);

        #assert_equal(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
        assert_equal(StatType.NoStat, fileInfo.StatsType);

        assert_equal(TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType);
        time = fileInfo.TimeAxis;
        assert_equal(datetime.datetime(1993, 12,  2, 0, 0, 0), time.StartDateTime);
        assert_equal(13, time.NumberOfTimeSteps);
        assert_equal(0, time.StartTimeOffset);
        assert_equal(86400, time.TimeStep);
        assert_equal(eumUnit.eumUsec, time.TimeUnit);
        assert_equal(0, time.FirstTimeStepIndex);

        assert_equal(np.float32(-1e-30), fileInfo.DeleteValueFloat);
        assert_equal(-1e-255, fileInfo.DeleteValueDouble);
        assert_equal(0, fileInfo.DeleteValueByte);
        assert_equal(2147483647, fileInfo.DeleteValueInt);
        assert_equal(2147483647, fileInfo.DeleteValueUnsignedInt);

        assert_equal("UTM-33", fileInfo.Projection.WKTString);
        assert_equal(12.438741600559766, fileInfo.Projection.Longitude);
        assert_equal(55.225707842436385, fileInfo.Projection.Latitude);
        assert_allclose(327, fileInfo.Projection.Orientation, 1e-12);


    @staticmethod
    def CustomBlockTester(customBlocks):


        assert_equal(1, len(customBlocks));

        customBlock = customBlocks[0];
        assert_equal("M21_Misc", customBlock.Name);
        assert_equal(DfsSimpleType.Float, customBlock.SimpleType);
        assert_allclose(7, customBlock.Count, 1e-23);
        assert_allclose(327, customBlock[0], 1e-23);  # Orientation - matching that in the projection info
        assert_allclose(0.2, customBlock[1], 1e-5);   # Drying depth
        assert_allclose(-900, customBlock[2], 1e-4);  # -900 = contains geographic information (projection)
        assert_equal(10, customBlock[3]);             # Land value
        assert_equal(0, customBlock[4]);
        assert_equal(0, customBlock[5]);
        assert_equal(0, customBlock[6]);


    @staticmethod
    def StaticItemTester(dfsFile):

        staticItem = dfsFile.ReadStaticItemNext();

        assert_equal("Static item", staticItem.Name);
        assert_equal(eumItem.eumIItemUndefined, staticItem.Quantity.Item);
        assert_equal(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit);
        assert_equal(DfsSimpleType.Float, staticItem.DataType);
        assert_equal(1, staticItem.ItemNumber);
        assert_equal(71 * 91, staticItem.ElementCount);
        #assert_equal(71 * 91, staticItem.UsedElementCount);
        assert_equal(np.float32(-1e-35), staticItem.ReferenceCoordinateX);
        assert_equal(np.float32(-1e-35), staticItem.ReferenceCoordinateY);
        assert_equal(np.float32(-1e-35), staticItem.ReferenceCoordinateZ);
        assert_equal(np.float32(-1e-35), staticItem.OrientationAlpha);
        assert_equal(np.float32(-1e-35), staticItem.OrientationPhi);
        assert_equal(np.float32(-1e-35), staticItem.OrientationTheta);

        # Check the axis
        spatialAxis = staticItem.SpatialAxis;
        assert_equal(SpaceAxisType.EqD2, spatialAxis.AxisType);
        axis = spatialAxis;
        assert_equal(2, axis.Dimension);
        assert_equal(eumUnit.eumUmeter, axis.AxisUnit);
        assert_equal(71, axis.XCount);
        assert_equal(91, axis.YCount);
        assert_equal(0, axis.X0);
        assert_equal(0, axis.Y0);
        assert_equal(900, axis.Dx);
        assert_equal(900, axis.Dy);

        # Check the data
        data = staticItem.Data;
        data2D = data.reshape(axis.XCount, axis.YCount, order = 'F');
        assert_equal(71 * 91, data.size);

        assert_equal(10, data[0]);
        assert_equal(np.float32(-15.9582891), data[1]);
        assert_equal(np.float32(-15.9582891), data2D[1, 0]);
        assert_equal(10, data[71]);
        assert_equal(np.float32(-21.8158112), data[10 + 6 * 71]);
        assert_equal(np.float32(-21.8158112), data2D[10, 6]);
        assert_equal(np.float32(-16.3214531), data[72]);
        assert_equal(np.float32(-16.3214531), data2D[1, 1]);
        assert_equal(np.float32(-26.3713856), data[71 * 91 - 5]);
        assert_equal(10, data[71 * 91 - 1]);

        # Check that there are no more static items
        staticItem2 = dfsFile.ReadStaticItemNext();
        assert None == staticItem2;

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):
        assert_equal(3, len(dynamicItemInfos));

        # Check dynamic info
        itemInfo = dynamicItemInfos[2];
        assert_equal(3, itemInfo.ItemNumber);
        assert_equal("Q Flux m^3/s/m", itemInfo.Name);
        assert_equal(eumItem.eumIFlowFlux, itemInfo.Quantity.Item);
        assert_equal(eumUnit.eumUm3PerSecPerM, itemInfo.Quantity.Unit);
        assert_equal(DfsSimpleType.Float, itemInfo.DataType);
        assert_equal(DataValueType.Instantaneous, itemInfo.ValueType);
        assert_equal(71 * 91, itemInfo.ElementCount);

        assert_equal(-1e-35, itemInfo.ReferenceCoordinateX);
        assert_equal(-1e-35, itemInfo.ReferenceCoordinateY);
        assert_equal(-1e-35, itemInfo.ReferenceCoordinateZ);
        assert_equal(-1e-35, itemInfo.OrientationAlpha);
        assert_equal(-1e-35, itemInfo.OrientationPhi);
        assert_equal(-1e-35, itemInfo.OrientationTheta);


        # Check spatial axis for all items
        for varItemInfo in dynamicItemInfos:
            assert_equal(SpaceAxisType.EqD2, varItemInfo.SpatialAxis.AxisType);
            axis = varItemInfo.SpatialAxis;
            assert_equal(2, axis.Dimension);
            assert_equal(eumUnit.eumUmeter, axis.AxisUnit);
            assert_equal(71, axis.XCount);
            assert_equal(91, axis.YCount);
            assert_equal(0, axis.X0);
            assert_equal(0, axis.X0);
            assert_equal(900, axis.Dx);
            assert_equal(900, axis.Dy);

  

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):


        assert_equal(3, len(dynamicItemInfos));

        # Check dynamic info
        itemInfo = dynamicItemInfos[2];
        assert_equal(3, itemInfo.ItemNumber);
        assert_equal("Q Flux m^3/s/m", itemInfo.Name);
        assert_equal(eumItem.eumIFlowFlux, itemInfo.Quantity.Item);
        assert_equal(eumUnit.eumUm3PerSecPerM, itemInfo.Quantity.Unit);
        assert_equal(DfsSimpleType.Float, itemInfo.DataType);
        assert_equal(DataValueType.Instantaneous, itemInfo.ValueType);

    @staticmethod
    def ReadTester(dfsFile):

        itemData = dfsFile.ReadItemTimeStep(1, 0);
        assert_equal(1, itemData.ItemNumber);
        assert_equal(0, itemData.TimeStepIndex);

        assert_equal(np.float32(-1e-30), itemData.Data[0]);
        assert_equal(np.float32(15.578289), itemData.Data[1]);
        assert_equal(np.float32(-1e-30), itemData.Data[71]);
        assert_equal(np.float32(15.941453), itemData.Data[72]);
        assert_equal(np.float32(12.1645823), itemData.Data[69 + 89 * 71]);

        itemData = dfsFile.ReadItemTimeStep(1, 10);
        assert_equal(np.float32(15.7142982), itemData.Data[1]);


    @staticmethod
    def ReadTester2D(dfsFile):

        itemData2D = dfsFile.ReadItemTimeStep(1, 0, reshape = True).Data;

        assert_equal(np.float32(-1e-30), itemData2D[0, 0]);
        assert_equal(np.float32(15.578289), itemData2D[1, 0]);
        assert_equal(np.float32(-1e-30), itemData2D[0, 1]);
        assert_equal(np.float32(15.941453), itemData2D[1, 1]);
        assert_equal(np.float32(12.1645823), itemData2D[69, 89]);

class FileLanduseDfs2:

    @staticmethod
    def FileInfoTester(fileInfo):

        assert_equal("File Title", fileInfo.FileTitle);
        assert_equal(r"Grid editor", fileInfo.ApplicationTitle);
        assert_equal(1, fileInfo.ApplicationVersion);
        assert_equal(0, fileInfo.DataType);

        #assert_equal(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
        assert_equal(StatType.NoStat, fileInfo.StatsType);

        assert_equal(TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType);
        time = fileInfo.TimeAxis;
        assert_equal(datetime.datetime(2000,  1,  1, 10, 0, 0), time.StartDateTime);
        assert_equal(1, time.NumberOfTimeSteps);
        assert_equal(0, time.StartTimeOffset);
        assert_equal(1, time.TimeStep);
        assert_equal(eumUnit.eumUsec, time.TimeUnit);
        assert_equal(0, time.FirstTimeStepIndex);

        assert_equal(np.float32(-2), fileInfo.DeleteValueFloat);
        assert_equal(-1e-255, fileInfo.DeleteValueDouble);
        assert_equal(0, fileInfo.DeleteValueByte);
        assert_equal(2147483647, fileInfo.DeleteValueInt);
        assert_equal(2147483647, fileInfo.DeleteValueUnsignedInt);

        assert_equal(ProjectionType.Projection, fileInfo.Projection.Type);
        assert_equal("NON-UTM", fileInfo.Projection.WKTString);
        assert_equal(0, fileInfo.Projection.Longitude);
        assert_equal(0, fileInfo.Projection.Latitude);
        assert_equal(0, fileInfo.Projection.Orientation);


    @staticmethod
    def CustomBlockTester(customBlocks):
        assert_equal(0, len(customBlocks));

    @staticmethod
    def StaticItemTester(dfsFile):

        staticItem = dfsFile.ReadStaticItemNext();
        assert None == staticItem;

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):

        assert_equal(1, len(dynamicItemInfos));

        # Check dynamic info
        itemInfo = dynamicItemInfos[0];
        assert_equal("Landuse", itemInfo.Name);
        assert_equal(eumItem.eumIIntegerCode, itemInfo.Quantity.Item);
        assert_equal(eumUnit.eumUintCode, itemInfo.Quantity.Unit);
        assert_equal(DfsSimpleType.Float, itemInfo.DataType);
        assert_equal(DataValueType.Instantaneous, itemInfo.ValueType);
        assert_equal(62 * 70, itemInfo.ElementCount);

        assert_equal(-1e-35, itemInfo.ReferenceCoordinateX);
        assert_equal(-1e-35, itemInfo.ReferenceCoordinateY);
        assert_equal(-1e-35, itemInfo.ReferenceCoordinateZ);
        assert_equal(-1e-35, itemInfo.OrientationAlpha);
        assert_equal(-1e-35, itemInfo.OrientationPhi);
        assert_equal(-1e-35, itemInfo.OrientationTheta);

        # Check spatial axis for all items
        assert_equal(SpaceAxisType.EqD2, itemInfo.SpatialAxis.AxisType);
        axis = itemInfo.SpatialAxis;
        assert_equal(2, axis.Dimension);
        assert_equal(eumUnit.eumUmeter, axis.AxisUnit);
        assert_equal(62, axis.XCount);
        assert_equal(70, axis.YCount);
        assert_equal(0, axis.X0);
        assert_equal(0, axis.X0);
        assert_equal(500, axis.Dx);
        assert_equal(500, axis.Dy);

    @staticmethod
    def DynamicItemTester(dynamicItemInfos):
        assert_equal(1, len(dynamicItemInfos));

        # Check dynamic info
        itemInfo = dynamicItemInfos[0];
        assert_equal(1, itemInfo.ItemNumber);
        assert_equal("Landuse", itemInfo.Name);
        assert_equal(eumItem.eumIIntegerCode, itemInfo.Quantity.Item);
        assert_equal(eumUnit.eumUintCode, itemInfo.Quantity.Unit);
        assert_equal(DfsSimpleType.Float, itemInfo.DataType);
        assert_equal(DataValueType.Instantaneous, itemInfo.ValueType);

    @staticmethod
    def ReadTester(dfsFile):

        itemData = dfsFile.ReadItemTimeStep(1, 0);
        assert_equal(1, itemData.ItemNumber);
        assert_equal(0, itemData.TimeStepIndex);
        
        itemDataf = itemData;
        assert_equal(-2, itemDataf.Data[0]);
        assert_equal(4, itemDataf.Data[21 + 61 * 62]);
        assert_equal(1, itemDataf.Data[21 + 62 * 62]);
        assert_equal(2, itemDataf.Data[21 + 63 * 62]);
        assert_equal(2, itemDataf.Data[21 + 64 * 62]);
        assert_equal(1, itemDataf.Data[21 + 65 * 62]);


    @staticmethod
    def ReadTester2D(dfsFile):

        itemData2D = dfsFile.ReadItemTimeStep(1, 0);

        assert_equal(-2, itemData2D.Data[0]);
        assert_equal(4, itemData2D.Data[21 + 61 * 62]);
        assert_equal(1, itemData2D.Data[21 + 62 * 62]);
        assert_equal(2, itemData2D.Data[21 + 63 * 62]);
        assert_equal(2, itemData2D.Data[21 + 64 * 62]);
        assert_equal(1, itemData2D.Data[21 + 65 * 62]);

        data2D = itemData2D.Data.reshape(dfsFile.SpatialAxis.XCount, dfsFile.SpatialAxis.YCount, order = 'F');
        assert_equal(62, data2D.shape[0]);
        assert_equal(70, data2D.shape[1]);
        assert_equal(4, data2D[21,61]);
        assert_equal(1, data2D[21,62]);
        assert_equal(2, data2D[21,63]);
        assert_equal(2, data2D[21,64]);
        assert_equal(1, data2D[21,65]);

  #endregion


if __name__ == '__main__':
    unittest.main()
