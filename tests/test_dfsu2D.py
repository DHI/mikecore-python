import unittest
from datetime import datetime
from mikecore.DfsFileFactory import *
from mikecore.DfsuBuilder import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *
from numpy.testing import *
from tests.examples_dfsu import *
from tests.test_util import *

class Dfsu2DTests(unittest.TestCase):

    def test_FirstExample(self):
      filename = "testdata/OresundHD.dfsu";
      ExamplesDfsu.ReadingDfsuFile(filename);

    def test_FindElementForCoordinate(self):
      filename = "testdata/OresundHD.dfsu";
      elmt = ExamplesDfsu.FindElementForCoordinate(filename);
      Assert.AreEqual(2858, elmt)

    def test_CreateDfsuFromDfs2(self):
      dfs2Filename = "testdata/OresundHD.dfs2";
      meshFilename = "testdata/testtmp/test_OresundHD.dfs2.mesh";
      dfsuFilename = "testdata/testtmp/test_OresundHD.dfs2.dfsu";
      ExamplesDfsu.CreateDfsuFromDfs2(dfs2Filename, meshFilename, dfsuFilename);

    def test_ExtractSubareaDfsu2D(self):
      sourceFilename = "testdata/OresundHD.dfsu";
      outputFilename = "testdata/testtmp/test_extract_OresundHD.dfsu";
      ExamplesDfsu.ExtractSubareaDfsu2D(
          sourceFilename, outputFilename,
          340000, 6160000,
          360000, 6180000);

    def test_ExtractDfs0FromDfsuTest(self):
      filename = "testdata/OresundHD.dfsu";
      # Indices of elements to extract dfs0 data from
      elmtIndices = np.array([0, 5, 100, 2000], np.int32);
      ExamplesDfsu.ExtractDfs0FromDfsu(filename, elmtIndices);

    def test_CreateOresundHDTest(self):
      sourceFilename = "testdata/OresundHD.dfsu";
      filename = "testdata/testtmp/test_build_OresundHD.dfsu";

      ExamplesDfsu.CreateDfsuFile(sourceFilename, filename, False);

      # Check the content of the file
      dfsuFile = DfsFileFactory.DfsuFileOpen(filename);
      Assert.AreEqual(eumUnit.eumUfeet, dfsuFile.ZUnit);
      dfsuFile.Close();
  
      ExamplesDfsu.CreateDfsuFile(sourceFilename, filename, True);

      # Check the content of the file
      dfsuFile = DfsFileFactory.DfsuFileOpen(filename);
      Assert.AreEqual(eumUnit.eumUmeter, dfsuFile.ZUnit);
      Assert.IsNotNull(dfsuFile.TimeAxis);
      Assert.AreEqual(TimeAxisType.CalendarEquidistant, dfsuFile.TimeAxis.TimeAxisType);
      dfsuFile.Close();
      
      dfsFile = DfsFileFactory.DfsGenericOpen(filename);

      FileOresundHDDfsu.FileInfoTester(dfsFile);
      FileOresundHDDfsu.CustomBlockTester(dfsFile);
      FileOresundHDDfsu.DynamicItemTester(dfsFile);
      FileOresundHDDfsu.StaticItemTester(dfsFile);
      FileOresundHDDfsu.ReadTester(dfsFile);


    def test_ReadOdenseHD2DTest(self):
      filename = "testdata/OdenseHD2D.dfsu";

      dfsFile = DfsFileFactory.DfsGenericOpen(filename);

      FileOdenseHD2DDfsu.DfsFileInfoTester(dfsFile);
      FileOdenseHD2DDfsu.CustomBlockTester(dfsFile);
      FileOdenseHD2DDfsu.DynamicItemTester(dfsFile);
      FileOdenseHD2DDfsu.StaticItemTester(dfsFile);
      FileOdenseHD2DDfsu.ReadTester(dfsFile);

      dfsFile = DfsFileFactory.DfsuFileOpen(filename);

      FileOdenseHD2DDfsu.DfsFileInfoTester(dfsFile);
      FileOdenseHD2DDfsu.DfsuFileInfoTester(dfsFile);

    def test_CreateOdenseHD2DTest(self):
      sourceFilename = "testdata/OdenseHD2D.dfsu";
      filename = "testdata/testtmp/test_create_OdenseHD2D.dfsu";

      ExamplesDfsu.CreateDfsuFile(sourceFilename, filename, True);

      # Check the content of the file
      dfsFile = DfsFileFactory.DfsGenericOpen(filename);

      FileOdenseHD2DDfsu.DfsFileInfoTester(dfsFile);
      FileOdenseHD2DDfsu.CustomBlockTester(dfsFile);
      FileOdenseHD2DDfsu.DynamicItemTester(dfsFile);
      FileOdenseHD2DDfsu.StaticItemTester(dfsFile);
      FileOdenseHD2DDfsu.ReadTester(dfsFile);

      dfsFile = DfsFileFactory.DfsuFileOpen(filename);
      FileOdenseHD2DDfsu.DfsuFileInfoTester(dfsFile);
      FileOdenseHD2DDfsu.DfsFileInfoTester(dfsFile);

#    def test_UpdateGeometryOresundHDTest(self):
#      sourceFilename = "testdata/OresundHD.dfsu";
#      filename = "testdata/testtmp/test_copy_OresundHD.dfsu";
#
#      testUtil.copy_file(sourceFilename, filename)
#
#      ExamplesDfsu.ModifyDfsuFileGeometry(filename);
#
#      # Check the data
#      dfsFile = DfsFileFactory.DfsGenericOpen(filename);
#
#      FileOresundHDDfsu.FileInfoTester(dfsFile, timestepSecs = 43200);
#      FileOresundHDDfsu.CustomBlockTester(dfsFile);
#      FileOresundHDDfsu.DynamicItemTester(dfsFile);
#      #FileOresundHDDfsu.StaticItemTester(dfsFile);
#      FileOresundHDDfsu.ReadTester(dfsFile, timestepSecs = 43200);
#
#      dfsFile.Close();

    def test_DeleteValueTest(self):
      sourceFilename = "testdata/OresundHD.dfsu";
      filename = "testdata/testtmp/test_copy_OresundHD.dfsu";
      testUtil.copy_file(sourceFilename, filename)

      # Check the data
      dfsFile = DfsFileFactory.DfsuFileOpen(filename);
      Assert.AreEqual(np.float32(1e-35), dfsFile.DeleteValueFloat);
      dfsFile.Close();
#      # Check the data
#      dfsFile = DfsFileFactory.DfsuFileOpenEdit(filename);
#      dfsFile.DeleteValueFloat = np.float32(-1e-30);
#      dfsFile.Close();
#      # Check the data
#      dfsFile = DfsFileFactory.DfsuFileOpen(filename);
#      Assert.AreEqual(np.float32(-1e-30), dfsFile.DeleteValueFloat);
#      dfsFile.Close();


    def test_CreateOresundHDGenericTest(self):
      sourceFilename = "testdata/OresundHD.dfsu";
      filename = "testdata/testtmp/test_create_OresundHD.dfsu";

      source = DfsFileFactory.DfsGenericOpen(sourceFilename);

      factory = DfsFactory();
      builder = DfsBuilder.Create("Area Series", "", 0);

      builder.SetDataType(2001);
      builder.SetGeographicalProjection(factory.CreateProjection("UTM-33"));
      builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(1993, 12, 2, 0, 0, 0), 0, 86400));
      builder.DeleteValueFloat = np.float32(1e-35);

      builder.AddCreateCustomBlock("MIKE_FM", np.array([ 2057, 3636, 2, 0, 0 ], np.int32));

      # Set up items
      itemBuilders = []

      item = builder.CreateDynamicItemBuilder();
      item.Set("Surface elevation", eumQuantity.Create(eumItem.eumISurfaceElevation, eumUnit.eumUmeter), DfsSimpleType.Float);
      itemBuilders.append(item);

      item = builder.CreateDynamicItemBuilder();
      item.Set("U velocity", eumQuantity.Create(eumItem.eumIuVelocity, eumUnit.eumUmeterPerSec), DfsSimpleType.Float);
      itemBuilders.append(item);

      item = builder.CreateDynamicItemBuilder();
      item.Set("V velocity", eumQuantity.Create(eumItem.eumIvVelocity, eumUnit.eumUmeterPerSec), DfsSimpleType.Float);
      itemBuilders.append(item);

      item = builder.CreateDynamicItemBuilder();
      item.Set("Current speed", eumQuantity.Create(eumItem.eumICurrentSpeed, eumUnit.eumUmeterPerSec), DfsSimpleType.Float);
      itemBuilders.append(item);

      item = builder.CreateDynamicItemBuilder();
      item.Set("Current direction", eumQuantity.Create(eumItem.eumICurrentDirection, eumUnit.eumUdegree), DfsSimpleType.Float);
      itemBuilders.append(item);

      item = builder.CreateDynamicItemBuilder();
      item.Set("CFL number (HD)", eumQuantity.Create(eumItem.eumIItemUndefined, eumUnit.eumUUnitUndefined), DfsSimpleType.Float);
      itemBuilders.append(item);

      for varItem in itemBuilders:
        varItem.SetValueType(DataValueType.Instantaneous);
        # Set axis to have meter unit (not necessary, just to make file exactly equal)
        # Could instead use: varItem.SetAxis(factory.CreateAxisDummy(3636));
        varItem.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, 3636, 0, 1));
        # Set to default ufs delete values (not used anyway, just to make file exactly equal)
        varItem.SetReferenceCoordinates(-1e-35, -1e-35, -1e-35);
        varItem.SetOrientation(-1e-35, -1e-35, -1e-35);
        builder.AddDynamicItem(varItem.GetDynamicItemInfo());
  
      builder.CreateFile(filename);

      # Add static items

      # Node id
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Int, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # X-coord
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Float, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # Y-coord
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Float, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # Z-coord
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Float, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # code
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Int, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # element id
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Int, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # element type
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Int, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      # no of nodes per element
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Int, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      #connectivity
      sourceStaticItem = source.ReadStaticItemNext();
      Assert.AreEqual(DfsSimpleType.Int, sourceStaticItem.DataType);
      builder.AddCreateStaticItem(sourceStaticItem.Name, None, sourceStaticItem.Data);

      dfsFile = builder.GetFile();

      # Add data for all item-timesteps
      while (True):
        sourceData = source.ReadItemTimeStepNext()
        if (sourceData is None):
            break;
        dfsFile.WriteItemTimeStepNext(sourceData.Time, sourceData.Data);
  
      source.Close();
      dfsFile.Close();

      # Check the content of the file
      dfsFile = DfsFileFactory.DfsGenericOpen(filename);

      FileOresundHDDfsu.FileInfoTester(dfsFile);
      FileOresundHDDfsu.CustomBlockTester(dfsFile);
      FileOresundHDDfsu.DynamicItemTester(dfsFile);
      FileOresundHDDfsu.StaticItemTester(dfsFile);
      FileOresundHDDfsu.ReadTester(dfsFile);


class FileOresundHDDfsu:
    @staticmethod
    def FileInfoTester(dfsFile, timestepSecs = -1):
      fileInfo = dfsFile.FileInfo;

      Assert.AreEqual("Area Series", fileInfo.FileTitle);
      Assert.AreEqual("", fileInfo.ApplicationTitle);
      Assert.AreEqual(0, fileInfo.ApplicationVersion);
      Assert.AreEqual(2001, fileInfo.DataType);

      #Assert.AreEqual(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
      Assert.AreEqual(StatType.NoStat, fileInfo.StatsType);

      Assert.AreEqual(np.float32(1e-35), fileInfo.DeleteValueFloat);
      Assert.AreEqual(0, fileInfo.DeleteValueByte);
      Assert.AreEqual(-1e-255, fileInfo.DeleteValueDouble);
      Assert.AreEqual(2147483647, fileInfo.DeleteValueInt);
      Assert.AreEqual(2147483647, fileInfo.DeleteValueUnsignedInt);

      Assert.AreEqual(TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType);
      timeAxis = fileInfo.TimeAxis;
      Assert.AreEqual(eumUnit.eumUsec, timeAxis.TimeUnit);
      Assert.AreEqual(timestepSecs if timestepSecs > 0 else 86400, timeAxis.TimeStep);
      Assert.AreEqual(0, timeAxis.StartTimeOffset);
      Assert.AreEqual(12, timeAxis.NumberOfTimeSteps);

    @staticmethod
    def CustomBlockTester(dfsFile):
      fileInfo = dfsFile.FileInfo;

      Assert.AreEqual(1, len(fileInfo.CustomBlocks));

      customBlock = fileInfo.CustomBlocks[0];
      Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType);
      Assert.AreEqual("MIKE_FM", customBlock.Name);
      Assert.AreEqual(5, customBlock.Count);
      Assert.AreEqual(2057, customBlock[0]);
      Assert.AreEqual(3636, customBlock[1]);
      Assert.AreEqual(2, customBlock[2]);
      Assert.AreEqual(0, customBlock[3]);
      Assert.AreEqual(0, customBlock[4]);

    @staticmethod
    def DynamicItemTester(dfsFile):
      dynamicItemInfos = dfsFile.ItemInfo;

      Assert.IsNotNull(dynamicItemInfos);
      Assert.AreEqual(6, len(dynamicItemInfos));

      # Check dynamic info
      itemInfo = dynamicItemInfos[2];
      Assert.AreEqual(3636, itemInfo.ElementCount);
      Assert.AreEqual(eumItem.eumIvVelocity, itemInfo.Quantity.Item);
      Assert.AreEqual(eumUnit.eumUmeterPerSec, itemInfo.Quantity.Unit);
      Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType);
      Assert.AreEqual("V velocity", itemInfo.Name);
      Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType);

      for varItemInfo in dynamicItemInfos:
        # These are not set in the dfsu file, hence they get the default ufs delete value
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.ReferenceCoordinateX);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.ReferenceCoordinateY);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.ReferenceCoordinateZ);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.OrientationAlpha);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.OrientationPhi);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.OrientationTheta);
        Assert.AreEqual(SpaceAxisType.EqD1, varItemInfo.SpatialAxis.AxisType);
        # Check spatial axis
        axis = varItemInfo.SpatialAxis;
        Assert.IsNotNull(axis);
        Assert.AreEqual(1, axis.Dimension);
        Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit);
        Assert.AreEqual(3636, axis.XCount);
        Assert.AreEqual(0, axis.X0);
        Assert.AreEqual(1, axis.Dx);
  
    @staticmethod
    def StaticItemTester(dfsFile):
      staticItems = [];

      staticItemNumber = 1;
      while (True):
        varstaticItem = dfsFile.ReadStaticItem(staticItemNumber);
        if (varstaticItem == None):
          break;
        staticItems.append(varstaticItem);
        staticItemNumber += 1;
  
      Assert.IsNotNull(staticItems);
      Assert.AreEqual(9, len(staticItems));

      # Static items in a dfsu file:
      # "Node id"       , int
      # "X-coord"       , double/float
      # "Y-coord"       , double/float
      # "Z-coord"       , float
      # "Code"          , int
      # "Element id"    , int
      # "Element type"  , int
      # "No of nodes"   , int
      # "Connectivity"  , int

      deleteValueFloat = np.float32(-1.00000002e-35); # UFS delete value

      #--------------------------------------
      # Check x-coord static item
      staticItem = staticItems[1];
      Assert.AreEqual(2, staticItem.ItemNumber);
      Assert.AreEqual(2057, staticItem.ElementCount);
      #Assert.AreEqual(2057, staticItem.UsedElementCount);
      Assert.AreEqual("X-coord", staticItem.Name);

      if (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit);
      elif (eumItem.eumIGeographicalCoordinate == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUmeter, staticItem.Quantity.Unit);
      else:
        Assert.Fail("X coordinate axis item type mismatch");

      if (staticItem.DataType != DfsSimpleType.Double and staticItem.DataType != DfsSimpleType.Float):
        Assert.Fail("DataType of X static item mismatch");

      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateX);
      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateY);
      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateZ);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationAlpha);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationPhi);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationTheta);

      # Check dummy spatial axis
      Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType);
      axis = staticItem.SpatialAxis;
      Assert.IsNotNull(axis);
      Assert.AreEqual(1, axis.Dimension);
      # TODO: Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit);
      Assert.AreEqual(2057, axis.XCount);
      Assert.AreEqual(0, axis.X0);
      Assert.AreEqual(1, axis.Dx);

      # Check data - first and last coordinate
      Assert.AreEqual(np.float32(359978.8), staticItem.Data[0]);
      Assert.AreEqual(np.float32(338109.5), staticItem.Data[2056]);

      #--------------------------------------
      # Check element type static item
      staticItem = staticItems[6];
      Assert.AreEqual(7, staticItem.ItemNumber);
      Assert.AreEqual(3636, staticItem.ElementCount);
      #Assert.AreEqual(3636, staticItem.UsedElementCount);

      if (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit);
      elif (eumItem.eumIIntegerCode == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit);
      else:
        Assert.Fail("Element Type coordinate axis item type mismatch");
      
      Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType);
      Assert.AreEqual("Element type", staticItem.Name);

      # Check dummy spatial axis
      Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType);
      axis = staticItem.SpatialAxis;
      Assert.IsNotNull(axis);
      Assert.AreEqual(3636, axis.XCount);

      # Check data - first and last elements
      Assert.AreEqual(21, staticItem.Data[0]);
      Assert.AreEqual(21, staticItem.Data[3635]);

      #--------------------------------------
      # Check connectivity static item
      staticItem = staticItems[8];
      Assert.AreEqual(9, staticItem.ItemNumber);
      Assert.AreEqual(3 * 3636, staticItem.ElementCount);
      #Assert.AreEqual(3 * 3636, staticItem.UsedElementCount);

      if (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit);
      elif (eumItem.eumIIntegerCode == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUintCode, staticItem.Quantity.Unit);
      else:
        Assert.Fail("Connectivity coordinate axis item type mismatch");
      
      Assert.AreEqual(DfsSimpleType.Int, staticItem.DataType);
      Assert.AreEqual("Connectivity", staticItem.Name);

      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateX);
      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateY);
      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateZ);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationAlpha);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationPhi);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationTheta);

      # Check dummy spatial axis
      Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType);
      axis = staticItem.SpatialAxis;
      Assert.IsNotNull(axis);
      Assert.AreEqual(1, axis.Dimension);
      # TODO: Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit);
      Assert.AreEqual(3 * 3636, axis.XCount);
      Assert.AreEqual(0, axis.X0);
      Assert.AreEqual(1, axis.Dx);

      # Check data - first and last element
      Assert.AreEqual(1, staticItem.Data[0]);
      Assert.AreEqual(2, staticItem.Data[1]);
      Assert.AreEqual(3, staticItem.Data[2]);
      Assert.AreEqual(1698, staticItem.Data[10905]);
      Assert.AreEqual(1697, staticItem.Data[10906]);
      Assert.AreEqual(2056, staticItem.Data[10907]);

    @staticmethod
    def ReadTester(dfsFile, timestepSecs = -1):
      dtSec = timestepSecs if timestepSecs > 0 else 86400;

      Assert.AreEqual(6, len(dfsFile.ItemInfo));
      Assert.AreEqual(12, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

      # Check that the ReadItemTimeStepNext item round-robin is correct
      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(1, itemData.ItemNumber);
      Assert.AreEqual(0.0, itemData.Time);
      Assert.AreEqual(3636, itemData.Data.size);
      Assert.AreEqual(np.float32(-0.37), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(2, itemData.ItemNumber);
      Assert.AreEqual(0, itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(3, itemData.ItemNumber);
      Assert.AreEqual(0, itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(4, itemData.ItemNumber);
      Assert.AreEqual(0, itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(5, itemData.ItemNumber);
      Assert.AreEqual(np.float32(358.136932), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(6, itemData.ItemNumber);
      Assert.AreEqual(np.float32(0.197053984), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(1, itemData.ItemNumber);
      Assert.AreEqual(dtSec, itemData.Time);
      Assert.AreEqual(np.float32(-0.04831052), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStep(5, 5);
      Assert.AreEqual(5, itemData.ItemNumber);
      Assert.AreEqual(5* dtSec, itemData.Time);
      Assert.AreEqual(np.float32(356.8728), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(6, itemData.ItemNumber);
      Assert.AreEqual(5* dtSec, itemData.Time);
      Assert.AreEqual(np.float32(0.204924032), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(1, itemData.ItemNumber);
      Assert.AreEqual(6* dtSec, itemData.Time);
      Assert.AreEqual(np.float32(-0.178162947), itemData.Data[0]);

      # Testing reusing the itemData's
      itemDatas = [];
      for i in range(6):
        itemDatas.append(dfsFile.ReadItemTimeStep(i + 1, 0));
  
      for j in range(12):
        for i in range(6):
          itemData = itemDatas[i];
          dfsFile.ReadItemTimeStep(itemData, j);
          Assert.AreEqual(i + 1, itemData.ItemNumber);
          Assert.AreEqual(j* dtSec, itemData.Time);
      
      Assert.AreEqual(np.float32(-0.119216606), itemDatas[0].Data[0]);
      Assert.AreEqual(np.float32(-0.0003770217), itemDatas[1].Data[0]);
      Assert.AreEqual(np.float32(-0.00166324107), itemDatas[2].Data[0]);
      Assert.AreEqual(np.float32(0.0017054372), itemDatas[3].Data[0]);
      Assert.AreEqual(np.float32(190.908844), itemDatas[4].Data[0]);
      Assert.AreEqual(np.float32(0.201946989), itemDatas[5].Data[0]);

      # Now we are at end of file, check what happens then:
      Assert.IsNull(dfsFile.ReadItemTimeStepNext());
      Assert.IsNull(dfsFile.ReadItemTimeStepNext());

class FileOdenseHD2DDfsu:

    @staticmethod
    def DfsuFileInfoTester(dfsuFile):
      Assert.AreEqual("2D", dfsuFile.FileTitle);
      Assert.AreEqual("", dfsuFile.ApplicationTitle);
      Assert.AreEqual(0, dfsuFile.ApplicationVersion);

      Assert.AreEqual(np.float32(1e-35), dfsuFile.DeleteValueFloat);

      Assert.AreEqual(TimeAxisType.CalendarEquidistant, dfsuFile.TimeAxis.TimeAxisType);
      Assert.AreEqual(86400, dfsuFile.TimeStepInSeconds);
      Assert.AreEqual(13, dfsuFile.NumberOfTimeSteps);

      # Check the element table and element types
      Assert.AreEqual(724, len(dfsuFile.ElementTable));

      Assert.AreEqual(21, dfsuFile.ElementType[54]);
      Assert.AreEqual(25, dfsuFile.ElementType[55]);
      Assert.AreEqual(25, dfsuFile.ElementType[56]);
      Assert.AreEqual(3, dfsuFile.ElementTable[54].size);
      Assert.AreEqual(4, dfsuFile.ElementTable[55].size);
      Assert.AreEqual(4, dfsuFile.ElementTable[56].size);

      Assert.AreEqual(52, dfsuFile.ElementTable[55][0]);
      Assert.AreEqual(53, dfsuFile.ElementTable[55][1]);
      Assert.AreEqual(54, dfsuFile.ElementTable[55][2]);
      Assert.AreEqual(55, dfsuFile.ElementTable[55][3]);

    @staticmethod
    def DfsFileInfoTester(dfsFile, created = False):
      fileInfo = dfsFile.FileInfo;

      Assert.AreEqual("2D", fileInfo.FileTitle);
      Assert.AreEqual("", fileInfo.ApplicationTitle);
      Assert.AreEqual(0, fileInfo.ApplicationVersion);
      Assert.AreEqual(2001, fileInfo.DataType);

      #Assert.AreEqual(FileType.EqtimeFixedspaceAllitems, fileInfo.FileType);
      Assert.AreEqual(StatType.NoStat, fileInfo.StatsType);

      Assert.AreEqual(np.float32(1e-35), fileInfo.DeleteValueFloat);
      Assert.AreEqual(0, fileInfo.DeleteValueByte);
      Assert.AreEqual(-1e-255, fileInfo.DeleteValueDouble);
      Assert.AreEqual(2147483647, fileInfo.DeleteValueInt);
      Assert.AreEqual(2147483647, fileInfo.DeleteValueUnsignedInt);

      Assert.AreEqual(TimeAxisType.CalendarEquidistant, fileInfo.TimeAxis.TimeAxisType);
      timeAxis = fileInfo.TimeAxis;
      Assert.AreEqual(eumUnit.eumUsec, timeAxis.TimeUnit);
      Assert.AreEqual(86400, timeAxis.TimeStep);
      Assert.AreEqual(0, timeAxis.StartTimeOffset);
      Assert.AreEqual(13, timeAxis.NumberOfTimeSteps);


    @staticmethod
    def CustomBlockTester(dfsFile):
      fileInfo = dfsFile.FileInfo;

      Assert.AreEqual(1, len(fileInfo.CustomBlocks));

      customBlock = fileInfo.CustomBlocks[0];
      Assert.AreEqual(DfsSimpleType.Int, customBlock.SimpleType);
      Assert.AreEqual("MIKE_FM", customBlock.Name);
      Assert.AreEqual(5, customBlock.Count);
      Assert.AreEqual(535, customBlock[0]);
      Assert.AreEqual(724, customBlock[1]);
      Assert.AreEqual(2, customBlock[2]);
      Assert.AreEqual(0, customBlock[3]);
      Assert.AreEqual(0, customBlock[4]);

    @staticmethod
    def DynamicItemTester(dfsFile):
      dynamicItemInfos = dfsFile.ItemInfo;

      Assert.IsNotNull(dynamicItemInfos);
      Assert.AreEqual(3, len(dynamicItemInfos));

      # Check dynamic info
      itemInfo = dynamicItemInfos[0];
      Assert.AreEqual(724, itemInfo.ElementCount);
      Assert.AreEqual(eumItem.eumISurfaceElevation, itemInfo.Quantity.Item);
      Assert.AreEqual(eumUnit.eumUmeter, itemInfo.Quantity.Unit);
      Assert.AreEqual(DfsSimpleType.Float, itemInfo.DataType);
      Assert.AreEqual("Surface elevation", itemInfo.Name);
      Assert.AreEqual(DataValueType.Instantaneous, itemInfo.ValueType);

      for varItemInfo in dynamicItemInfos:
        # These are not set in the dfsu file, hence they get the default ufs delete value
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.ReferenceCoordinateX);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.ReferenceCoordinateY);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.ReferenceCoordinateZ);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.OrientationAlpha);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.OrientationPhi);
        Assert.AreEqual(np.float32(-1e-35), varItemInfo.OrientationTheta);
        Assert.AreEqual(SpaceAxisType.EqD1, varItemInfo.SpatialAxis.AxisType);
        # Check spatial axis
        axis = varItemInfo.SpatialAxis;
        Assert.IsNotNull(axis);
        Assert.AreEqual(1, axis.Dimension);
        Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit);
        Assert.AreEqual(724, axis.XCount);
        Assert.AreEqual(0, axis.X0);
        Assert.AreEqual(1, axis.Dx);
  
    @staticmethod
    def StaticItemTester(dfsFile):
      staticItems = []

      staticItemNumber = 1;
      while (True):
        varstaticItem = dfsFile.ReadStaticItem(staticItemNumber);
        if (varstaticItem == None):
          break;
        staticItems.append(varstaticItem);
        staticItemNumber += 1;
  
      Assert.IsNotNull(staticItems);
      Assert.AreEqual(9, len(staticItems));

      # Static items in a dfsu file:
      # "Node id"       , int
      # "X-coord"       , double/float
      # "Y-coord"       , double/float
      # "Z-coord"       , float
      # "Code"          , int
      # "Element id"    , int
      # "Element type"  , int
      # "No of nodes"   , int
      # "Connectivity"  , int

      deleteValueFloat = np.float32(-1.00000002e-35); # UFS delete value

      #--------------------------------------
      # Check x-coord static item
      staticItem = staticItems[1];
      Assert.AreEqual(2, staticItem.ItemNumber);
      Assert.AreEqual(535, staticItem.ElementCount);
      #Assert.AreEqual(535, staticItem.UsedElementCount);
      Assert.AreEqual("X-coord", staticItem.Name);

      if (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUUnitUndefined, staticItem.Quantity.Unit);
      elif (eumItem.eumIGeographicalCoordinate == staticItem.Quantity.Item):
        Assert.AreEqual(eumUnit.eumUmeter, staticItem.Quantity.Unit);
      else:
        Assert.Fail("X coordinate axis item type mismatch");
      
      if (staticItem.DataType != DfsSimpleType.Double and staticItem.DataType != DfsSimpleType.Float):
        Assert.Fail("DataType of X static item mismatch");

      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateX);
      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateY);
      Assert.AreEqual(deleteValueFloat, staticItem.ReferenceCoordinateZ);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationAlpha);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationPhi);
      Assert.AreEqual(deleteValueFloat, staticItem.OrientationTheta);

      # Check dummy spatial axis
      Assert.AreEqual(SpaceAxisType.EqD1, staticItem.SpatialAxis.AxisType);
      axis = staticItem.SpatialAxis;
      Assert.IsNotNull(axis);
      Assert.AreEqual(535, axis.XCount);

      # Check data - first and last coordinate
      Assert.AreEqual(np.float32(222397.938), staticItem.Data[0]);
      Assert.AreEqual(np.float32(213346.141), staticItem.Data[534]);

      #--------------------------------------
      # Check element type static item
      staticItem = staticItems[6];
      Assert.AreEqual(7, staticItem.ItemNumber);
      Assert.AreEqual(724, staticItem.ElementCount);
      Assert.AreEqual("Element type", staticItem.Name);

      # Check data - first and last elements
      Assert.AreEqual(21, staticItem.Data[0]);
      Assert.AreEqual(25, staticItem.Data[55]);

      #--------------------------------------
      # Check element type static item
      staticItem = staticItems[7];
      Assert.AreEqual(8, staticItem.ItemNumber);
      Assert.AreEqual(724, staticItem.ElementCount);
      Assert.AreEqual("No of nodes", staticItem.Name);

      # Check data - first and last elements
      Assert.AreEqual(3, staticItem.Data[0]);
      Assert.AreEqual(4, staticItem.Data[55]);

      #--------------------------------------
      # Check connectivity static item
      staticItem = staticItems[8];
      Assert.AreEqual(9, staticItem.ItemNumber);
      Assert.AreEqual(2383, staticItem.ElementCount);
      Assert.AreEqual("Connectivity", staticItem.Name);

      # Check data - first and last element
      Assert.AreEqual(1, staticItem.Data[0]);
      Assert.AreEqual(2, staticItem.Data[1]);
      Assert.AreEqual(3, staticItem.Data[2]);
      Assert.AreEqual(52, staticItem.Data[3*54+4]);
      Assert.AreEqual(53, staticItem.Data[3*54+4+1]);
      Assert.AreEqual(54, staticItem.Data[3*54+4+2]);
      Assert.AreEqual(55, staticItem.Data[3*54+4+3]);

    @staticmethod
    def ReadTester(dfsFile):

      # Check that the ReadItemTimeStepNext item round-robin is correct
      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(1, itemData.ItemNumber);
      Assert.AreEqual(0.0, itemData.Time);
      Assert.AreEqual(724, itemData.Data.size);
      Assert.AreEqual(np.float32(0.369), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(2, itemData.ItemNumber);
      Assert.AreEqual(0, itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(3, itemData.ItemNumber);
      Assert.AreEqual(0, itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(1, itemData.ItemNumber);
      Assert.AreEqual(86400, itemData.Time);
      Assert.AreEqual(np.float32(0.07376249), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(2, itemData.ItemNumber);
      Assert.AreEqual(np.float32(-0.128370076), itemData.Data[0]);

      itemData = dfsFile.ReadItemTimeStepNext();
      Assert.AreEqual(3, itemData.ItemNumber);
      Assert.AreEqual(np.float32(0.03862528), itemData.Data[0]);

      dfsFile.Reset();

      # Testing reusing the itemData's
      itemDatas = []
      for itemInfo in dfsFile.ItemInfo:
        itemDatas.append(dfsFile.CreateEmptyItemData(itemInfo));
  
      for j in range(13):
        for i in range(3):
          itemData = itemDatas[i];
          # TODO: Implement?
          #dfsFile.ReadItemTimeStep(itemData, j);
          itemData = dfsFile.ReadItemTimeStep(i+1, j);
          itemDatas[i] = itemData;
          Assert.AreEqual(i + 1, itemData.ItemNumber);
          Assert.AreEqual(j * 86400, itemData.Time);
      
      Assert.AreEqual(np.float32(0.22424224), itemDatas[0].Data[0]);
      Assert.AreEqual(np.float32(-0.0129399123), itemDatas[1].Data[0]);
      Assert.AreEqual(np.float32(0.004310336), itemDatas[2].Data[0]);

      # Now we are at end of file, check what happens then:
      Assert.IsNull(dfsFile.ReadItemTimeStepNext());
      Assert.IsNull(dfsFile.ReadItemTimeStepNext());




if __name__ == '__main__':
    unittest.main()
