import platform
import unittest
from datetime import datetime
from mikecore.DfsFileFactory import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import eumQuantity
from numpy.testing import *
from tests.examples_dfs0 import *
from tests.test_util import *

class Dfs0Tests(unittest.TestCase):
    timeOffset = 3.0;

    # def ReadDfs0Example():
    #    sum = examples_dfs0.ReadDfs0File("testdata/Rain_stepaccumulated.dfs0");
    #    assert_equal(21.960000000000001, sum);

    #def ReadDfs0NonTimeAxisExample():
    #    sum = examples_dfs0.ReadNonTimeAxisDfs0("testdata/Added_Mass.dfs0");
    #    assert_equal(115759469602678.09, sum);

    #def FindMaxValue():
    #    maxValue = examples_dfs0.FindMaxValue("testdata/data_ndr_roese.dfs0", 4);
    #    assert_equal(1.0754467248916626, maxValue);

    def test_Read_non_ascii_itemname(self):
        dfs = DfsFile()
        dfs.Open("testdata/TS_non_ascii.dfs0")
        Assert.AreEqual(len(dfs.ItemInfo), 12) 
        Assert.AreEqual(dfs.ItemInfo[1].Name, 'Hornbæk: Surface elevation')


    def test_Write_non_ascii(self):        
        Dfs0Tests.CreateNeqCalTimeTest(True, fileTitle="Title æøå", itemName1='item æøå')

    #def UpdateDfs0Data():
    #    examples_dfs0.UpdateDfs0Data(UnitTestHelper.TestDataRoot + @"Rain_instantaneous.dfs0", UnitTestHelper.TestDataRoot + @"test_update_Rain_instantaneous.dfs0");

    def test_CreateEqTimeTest(self):
        Dfs0Tests.CreateEqCalTimeTest(False);

    def test_CreateEqCalTest(self):
        Dfs0Tests.CreateEqCalTimeTest(True);

    @staticmethod
    def CreateEqCalTimeTest(calendarAxis):

        if (calendarAxis):
            filename = "testdata/testtmp/test_create_TemporalEqCal.dfs0";
        else:
            filename = "testdata/testtmp/test_create_TemporalEqTime.dfs0";

        ExamplesDfs0.CreateDfs0File(filename, calendarAxis);

        # Open file and test content
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);

        if (calendarAxis):
            FileTemporalEqCalDfs0.TimeAxisTester(dfsFile, False);
            FileTemporalEqCalDfs0.ReadTester(dfsFile, False);
        else:
            FileTemporalEqTimeDfs0.TimeAxisTester(dfsFile);
            FileTemporalEqTimeDfs0.ReadTester(dfsFile);

        dfsFile.Close();

        # Open file and test content with modifyTimes==True
        if (calendarAxis and platform.system() == "Linux"):
            print("WARNING: start-time-offset and ModifyTimes=True does not work on Linux");
            return;

        modifyTimes = True
        parameters = DfsFileFactory.CreateDefaultParameters();
        parameters.ModifyTimes = modifyTimes;
        dfsFile = DfsFileFactory.DfsGenericOpen(filename, parameters);

        if (calendarAxis):
            FileTemporalEqCalDfs0.TimeAxisTester(dfsFile, modifyTimes);
            FileTemporalEqCalDfs0.ReadTester(dfsFile, modifyTimes);
        else:
            FileTemporalEqTimeDfs0.TimeAxisTester(dfsFile);
            FileTemporalEqTimeDfs0.ReadTester(dfsFile);

        dfsFile.Close();

    # Create a file matching the TemporalEqTime.dfs0 file, and tests its content
    def test_CreateNeqTimeTest(self):
        Dfs0Tests.CreateNeqCalTimeTest(False);
        Dfs0Tests.CreateNeqCalTimeTest(False, bulkWrite=True);


    # Create a file matching the TemporalEqCal.dfs0 file, and tests its content
    def test_CreateNeqCalFileTest(self):
        Dfs0Tests.CreateNeqCalTimeTest(True);
        Dfs0Tests.CreateNeqCalTimeTest(True, bulkWrite=True);


    @staticmethod
    def CreateNeqCalTimeTest(calendarAxis, fileTitle="TemporalAxisTest", itemName1="WaterLevel item", bulkWrite=False):

        filename = "testdata/testtmp/test_create_Temporal";
        if (calendarAxis):
            filename = filename + "NeqCal";
        else:
            filename = filename + "NeqTime";
        if (bulkWrite):
            filename = filename + "Data";
        filename = filename + ".dfs0";

        factory = DfsFactory();
        builder = DfsBuilder.Create(fileTitle, "dfs Timeseries Bridge", 10000);

        # Set up file header
        builder.SetDataType(1);
        builder.SetGeographicalProjection(factory.CreateProjectionUndefined());
        if (calendarAxis):
            builder.SetTemporalAxis(factory.CreateTemporalNonEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(2010,  1,  4, 12, 34, 00)));
        else:
            builder.SetTemporalAxis(factory.CreateTemporalNonEqTimeAxis(eumUnit.eumUsec));
        builder.SetItemStatisticsType(StatType.NoStat);

        # Set up first item
        item1 = builder.CreateDynamicItemBuilder();
        item1.Set(itemName1, eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter), DfsSimpleType.Float);
        item1.SetValueType(DataValueType.Instantaneous);
        item1.SetAxis(factory.CreateAxisEqD0());
        item1.SetReferenceCoordinates(1, 2, 3);
        builder.AddDynamicItem(item1.GetDynamicItemInfo());

        item2 = builder.CreateDynamicItemBuilder();
        item2.Set("WaterDepth item", eumQuantity.Create(eumItem.eumIWaterDepth, eumUnit.eumUmeter), DfsSimpleType.Float);
        item2.SetValueType(DataValueType.Instantaneous);
        item2.SetAxis(factory.CreateAxisEqD0());
        item2.SetReferenceCoordinates(1, 2, 3);
        builder.AddDynamicItem(item2.GetDynamicItemInfo());

        # Create file
        builder.CreateFile(filename);
        file = builder.GetFile();

        if not bulkWrite:
            # Write data to file
            file.WriteItemTimeStepNext( 0 + Dfs0Tests.timeOffset, np.array([  0], np.float32)); # Water level
            file.WriteItemTimeStepNext( 0 + Dfs0Tests.timeOffset, np.array([100], np.float32)); # Water depth
            file.WriteItemTimeStepNext(10 + Dfs0Tests.timeOffset, np.array([  1], np.float32)); # Water level
            file.WriteItemTimeStepNext(10 + Dfs0Tests.timeOffset, np.array([101], np.float32)); # Water depth
            file.WriteItemTimeStepNext(20 + Dfs0Tests.timeOffset, np.array([  2], np.float32)); # Water level
            file.WriteItemTimeStepNext(20 + Dfs0Tests.timeOffset, np.array([102], np.float32)); # Water depth
            file.WriteItemTimeStepNext(35 + Dfs0Tests.timeOffset, np.array([  3], np.float32)); # etc...
            file.WriteItemTimeStepNext(35 + Dfs0Tests.timeOffset, np.array([103], np.float32));
            file.WriteItemTimeStepNext(50 + Dfs0Tests.timeOffset, np.array([  4], np.float32));
            file.WriteItemTimeStepNext(50 + Dfs0Tests.timeOffset, np.array([104], np.float32));
            file.WriteItemTimeStepNext(60 + Dfs0Tests.timeOffset, np.array([  5], np.float32));
            file.WriteItemTimeStepNext(60 + Dfs0Tests.timeOffset, np.array([105], np.float32));
            file.WriteItemTimeStepNext(75 + Dfs0Tests.timeOffset, np.array([ 10], np.float32));
            file.WriteItemTimeStepNext(75 + Dfs0Tests.timeOffset, np.array([110], np.float32));
            file.WriteItemTimeStepNext(90 + Dfs0Tests.timeOffset, np.array([ 11], np.float32));
            file.WriteItemTimeStepNext(90 + Dfs0Tests.timeOffset, np.array([111], np.float32));
            file.WriteItemTimeStepNext(91 + Dfs0Tests.timeOffset, np.array([ 12], np.float32));
            file.WriteItemTimeStepNext(91 + Dfs0Tests.timeOffset, np.array([112], np.float32));
            file.WriteItemTimeStepNext(95 + Dfs0Tests.timeOffset, np.array([ 13], np.float32));
            file.WriteItemTimeStepNext(95 + Dfs0Tests.timeOffset, np.array([113], np.float32));
        else:
            data = np.array(
                [
                    [ 0 + Dfs0Tests.timeOffset,  0, 100],
                    [10 + Dfs0Tests.timeOffset,  1, 101],
                    [20 + Dfs0Tests.timeOffset,  2, 102],
                    [35 + Dfs0Tests.timeOffset,  3, 103],
                    [50 + Dfs0Tests.timeOffset,  4, 104],
                    [60 + Dfs0Tests.timeOffset,  5, 105],
                    [75 + Dfs0Tests.timeOffset, 10, 110],
                    [90 + Dfs0Tests.timeOffset, 11, 111],
                    [91 + Dfs0Tests.timeOffset, 12, 112],
                    [95 + Dfs0Tests.timeOffset, 13, 113],
                ], np.float64)
            file.WriteDfs0DataDouble(data);

        file.Close();

        # Open file and test content

        dfsFile = DfsFileFactory.DfsGenericOpen(filename);

        if (calendarAxis):
            FileTemporalNeqCalDfs0.TimeAxisTester(dfsFile, False);
            FileTemporalNeqCalDfs0.ReadTester(dfsFile, False);
        else:
            FileTemporalNeqTimeDfs0.TimeAxisTester(dfsFile, False);
            FileTemporalNeqTimeDfs0.ReadTester(dfsFile, False);

        dfsFile.Close();

        # Open file and test content with modifyTimes==True
        if (calendarAxis and platform.system() == "Linux"):
            print("WARNING: start-time-offset and ModifyTimes=True does not work on Linux");
            return;

        modifyTimes = True
        parameters = DfsFileFactory.CreateDefaultParameters();
        parameters.ModifyTimes = modifyTimes;
        dfsFile = DfsFileFactory.DfsGenericOpen(filename, parameters);

        if (calendarAxis):
            FileTemporalNeqCalDfs0.TimeAxisTester(dfsFile, modifyTimes);
            FileTemporalNeqCalDfs0.ReadTester(dfsFile, modifyTimes);
        else:
            FileTemporalNeqTimeDfs0.TimeAxisTester(dfsFile, modifyTimes);
            FileTemporalNeqTimeDfs0.ReadTester(dfsFile, modifyTimes);

        dfsFile.Close();

    # Create and append to file matching the TemporalEqTime.dfs0 file
    def test_AppendEqTimeTest(self):
        Dfs0Tests.CreateEqCalTimeTest(False);
        Dfs0Tests.AppendEqCalTimeTest(False);


    # Create and append to file matching the TemporalEqCal.dfs0 file
    def test_AppendEqCalTest(self):
        Dfs0Tests.CreateEqCalTimeTest(True);
        Dfs0Tests.AppendEqCalTimeTest(True);


    # Testing the write methods when appending
    @staticmethod
    def AppendEqCalTimeTest(calendarAxis):

        if (calendarAxis):
            filename = "testdata/testtmp/test_create_TemporalEqCal.dfs0";
        else:
            filename = "testdata/testtmp/test_create_TemporalEqTime.dfs0";

        # Open file and append data to it
        dfsFile = DfsFileFactory.DfsGenericOpenAppend(filename);

        assert_equal(10, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        dfsFile.WriteItemTimeStepNext(0, np.array([20], np.float32));
        assert_equal(10, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        dfsFile.WriteItemTimeStepNext(0, np.array([120], np.float32));
        assert_equal(11, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed

        dfsFile.WriteItemTimeStepNext(0, np.array([21], np.float32));
        assert_equal(11, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        dfsFile.WriteItemTimeStepNext(0, np.array([121], np.float32));
        assert_equal(12, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed

        dfsFile.WriteItemTimeStep(1, 12, 0, np.array([22], np.float32));
        assert_equal(12, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        dfsFile.WriteItemTimeStep(2, 12, 0, np.array([122], np.float32));
        assert_equal(13, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed

        dfsFile.WriteItemTimeStep(1, 13, 0, np.array([23], np.float32));
        assert_equal(13, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        dfsFile.WriteItemTimeStep(2, 13, 0, np.array([123], np.float32));
        assert_equal(14, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed

        dfsFile.Flush();
        itemData = dfsFile.ReadItemTimeStep(1, 11);

        dfsFile.Close();

        # Open file in edit mode, and append to it
        dfsFile = DfsFileFactory.DfsGenericOpenEdit(filename);
        itemData = dfsFile.ReadItemTimeStepNext();

        assert_equal(14, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        # Find "end of file" write data (itemnumber 1 timestepindex 14)
        dfsFile.FindTimeStep(14);
        dfsFile.WriteItemTimeStepNext(0, np.array([24], np.float32));
        assert_equal(14, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        # Reposition file pointer at last time step, and rewrite data for itemnumber 1 timestepindex 14
        dfsFile.FindTimeStep(14);
        dfsFile.WriteItemTimeStepNext(0, np.array([124], np.float32));
        assert_equal(14, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        dfsFile.WriteItemTimeStepNext(0, np.array([224], np.float32));
        assert_equal(15, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        # Read the newly written data
        itemData = dfsFile.ReadItemTimeStep(1, 14);
        assert_equal(124, itemData.Data[0]);

        # Continue appending (timestep 15)
        dfsFile.WriteItemTimeStep(1, 15, 0, np.array([25], np.float32));
        assert_equal(15, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        dfsFile.WriteItemTimeStep(2, 15, 0, np.array([125], np.float32));
        assert_equal(16, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        dfsFile.Close();


        dfsFile = DfsFileFactory.DfsGenericOpen(filename);

        assert_equal(16, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        data = dfsFile.ReadItemTimeStep(1,10);
        assert_equal(10, data.TimeStepIndex);
        assert_equal(20, data.Data[0]);

        data = dfsFile.ReadItemTimeStep(1, 11);
        assert_equal(11, data.TimeStepIndex);
        assert_equal(21, data.Data[0]);

        data = dfsFile.ReadItemTimeStepNext();
        assert_equal(11, data.TimeStepIndex);
        assert_equal(121, data.Data[0]);

        data = dfsFile.ReadItemTimeStepNext();
        assert_equal(12, data.TimeStepIndex);
        assert_equal(22, data.Data[0]);

        dfsFile.Close();

    # Create and append to file matching the TemporalEqTime.dfs0 file
    def test_AppendNeqTimeTest(self):
        Dfs0Tests.CreateNeqCalTimeTest(False);
        Dfs0Tests.AppendNeqCalTimeTest(False);

    # Create and append to file matching the TemporalEqCal.dfs0 file
    def test_AppendNeqCalTest(self):
        Dfs0Tests.CreateNeqCalTimeTest(True);
        Dfs0Tests.AppendNeqCalTimeTest(True);

    # Testing the write methods when appending
    @staticmethod
    def AppendNeqCalTimeTest(calendarAxis):
        if (calendarAxis):
            filename = "testdata/testtmp/test_create_TemporalNeqCal.dfs0";
        else:
            filename = "testdata/testtmp/test_create_TemporalNeqTime.dfs0";

        # Open file and append data to it
  
        dfsFile = DfsFileFactory.DfsGenericOpenAppend(filename);

        assert_equal(10, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        #assert_equal(95, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());

        dfsFile.WriteItemTimeStepNext(100+Dfs0Tests.timeOffset, np.array([20], np.float32));
        assert_equal(10, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        #assert_equal(95, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());
        dfsFile.WriteItemTimeStepNext(100+Dfs0Tests.timeOffset, np.array([120], np.float32));
        assert_equal(11, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed
        #assert_equal(100, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());

        dfsFile.WriteItemTimeStepNext(110+Dfs0Tests.timeOffset, np.array([21], np.float32));
        assert_equal(11, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        #assert_equal(100, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());
        dfsFile.WriteItemTimeStepNext(110+Dfs0Tests.timeOffset, np.array([121], np.float32));
        assert_equal(12, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed
        #assert_equal(110, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());

        dfsFile.WriteItemTimeStep(1, 12, 111+Dfs0Tests.timeOffset, np.array([22], np.float32));
        assert_equal(12, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        #assert_equal(110, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());
        dfsFile.WriteItemTimeStep(2, 12, 111+Dfs0Tests.timeOffset, np.array([122], np.float32));
        assert_equal(13, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed
        #assert_equal(111, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());

        dfsFile.WriteItemTimeStep(1, 13, 115+Dfs0Tests.timeOffset, np.array([22], np.float32));
        assert_equal(13, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);
        #assert_equal(111, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());
        dfsFile.WriteItemTimeStep(2, 13, 115+Dfs0Tests.timeOffset, np.array([22], np.float32));
        assert_equal(14, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);  # timestep has been completed
        #assert_equal(115, dfsFile.FileInfo.TimeAxis.TimeSpanInSeconds());

        dfsFile.Close();

        dfsFile = DfsFileFactory.DfsGenericOpen(filename);

        assert_equal(14, dfsFile.FileInfo.TimeAxis.NumberOfTimeSteps);

        data = dfsFile.ReadItemTimeStep(1, 10);
        assert_equal(10, data.TimeStepIndex);
        assert_equal(20, data.Data[0]);

        data = dfsFile.ReadItemTimeStep(1, 11);
        assert_equal(11, data.TimeStepIndex);
        assert_equal(21, data.Data[0]);

        data = dfsFile.ReadItemTimeStepNext();
        assert_equal(11, data.TimeStepIndex);
        assert_equal(121, data.Data[0]);

        data = dfsFile.ReadItemTimeStepNext();
        assert_equal(12, data.TimeStepIndex);
        assert_equal(22, data.Data[0]);

        dfsFile.Close();






# Class testing the file TemporalEqTime.dfs0.
# File was creating by the TsEditor.exe.
class FileTemporalEqTimeDfs0:

    @staticmethod
    def TimeAxisTester(dfsFile):
  
        timeAxis = dfsFile.FileInfo.TimeAxis;

        assert_equal(TimeAxisType.TimeEquidistant, timeAxis.TimeAxisType);
        assert_equal(3, timeAxis.StartTimeOffset);
        assert_equal(0, timeAxis.FirstTimeStepIndex);
        assert_equal(10, timeAxis.NumberOfTimeSteps);
        assert_equal(3, timeAxis.StartTimeOffset);
        assert_equal(eumUnit.eumUsec, timeAxis.TimeUnit);

        eqTimeAxis = timeAxis;

        assert_equal(10, eqTimeAxis.TimeStep);
        #assert_equal(10, eqTimeAxis.TimeStepInSeconds());

        #assert_equal(90, timeAxis.TimeSpanInSeconds());

        ## Testing search method
        #assert_equal( ~0, dfsFile.Search(2.999));
        #assert_equal(  0, dfsFile.Search(3));
        #assert_equal( ~1, dfsFile.Search(3.001));

        #assert_equal(  4, dfsFile.Search(43));
        #assert_equal( ~5, dfsFile.Search(48));
        #assert_equal(  5, dfsFile.Search(53));

        #assert_equal( ~9, dfsFile.Search(92.999));
        #assert_equal(  9, dfsFile.Search(93));
        #assert_equal(~10, dfsFile.Search(93.001));

        #var dtvar = new []
        #    dfsFile.GetDateTimes(new DateTime(2010, 1, 4, 12, 34, 01), true),
        #    dfsFile.GetDateTimes(new DateTime(2010, 1, 4, 12, 34, 01), false)
        #foreach (IReadOnlyList<DateTime> dateTimes in dtvar)

        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 04), dateTimes[0]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 44), dateTimes[4]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 54), dateTimes[5]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 35, 34), dateTimes[9]);

    @staticmethod
    def ReadTester(dfsFile):

        # Remember that itemData.Time returns the timestep index.

        assert_equal(3, dfsFile.FileInfo.TimeAxis.StartTimeOffset);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(3, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(0, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_equal(3, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(100, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(13, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(1, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStep(1, 7);
        assert_equal(1, itemData.ItemNumber);
        assert_equal(73, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(11, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_equal(73, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(111, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(83, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(12, itemData.Data[0]);
  
class FileTemporalEqCalDfs0:
    @staticmethod
    def TimeAxisTester(dfsFile, modifiedTimes):

        timeAxis = dfsFile.FileInfo.TimeAxis;

        assert_equal(TimeAxisType.CalendarEquidistant, timeAxis.TimeAxisType);
        assert_equal(0, timeAxis.FirstTimeStepIndex);
        assert_equal(10, timeAxis.NumberOfTimeSteps);
        assert_equal(0 if modifiedTimes else 4, timeAxis.StartTimeOffset);
        assert_equal(eumUnit.eumUsec, timeAxis.TimeUnit);

        eqCalAxis = timeAxis

        if (modifiedTimes):
            assert_equal(datetime.datetime(2010, 1, 4, 12, 34,  4), eqCalAxis.StartDateTime);
        else:
            assert_equal(datetime.datetime(2010, 1, 4, 12, 34, 00), eqCalAxis.StartDateTime);
        assert_equal(10, eqCalAxis.TimeStep);
        #assert_equal(10, eqCalAxis.TimeStepInSeconds());

        #assert_equal(90, eqCalAxis.TimeSpanInSeconds());
        #assert_equal(new TimeSpan(0,1,30), eqCalAxis.TimeSpanAsTimeSpan());

        ## Testing search method
        #assert_equal( ~0, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 03)));
        #assert_equal(  0, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 04)));
        #assert_equal( ~1, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 05)));

        #assert_equal(  4, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 44)));
        #assert_equal( ~5, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 49)));
        #assert_equal(  5, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 54)));

        #assert_equal( ~9, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 33)));
        #assert_equal(  9, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 34)));
        #assert_equal(~10, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 34, 1)));

        #assert_equal( ~0, dfsFile.Search(modifiedTimes ? -0.001 :  3.999));
        #assert_equal(  0, dfsFile.Search(modifiedTimes ?  0     :  4));
        #assert_equal( ~1, dfsFile.Search(modifiedTimes ?  0.001 :  4.001));

        #assert_equal(  4, dfsFile.Search(modifiedTimes ? 40     : 44));
        #assert_equal( ~5, dfsFile.Search(modifiedTimes ? 45     : 49));
        #assert_equal(  5, dfsFile.Search(modifiedTimes ? 50     : 54));

        #assert_equal( ~9, dfsFile.Search(modifiedTimes ? 89.999 : 93.999));
        #assert_equal(  9, dfsFile.Search(modifiedTimes ? 90     : 94));
        #assert_equal(~10, dfsFile.Search(modifiedTimes ? 90.001 : 94.001));

        #var dtvar = new []
        
        #    dfsFile.GetDateTimes(true),
        #    dfsFile.GetDateTimes(false)
        #  };
        #foreach (IReadOnlyList<DateTime> dateTimes in dtvar)
    
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 04), dateTimes[0]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 44), dateTimes[4]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 54), dateTimes[5]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 35, 34), dateTimes[9]);
        #}

    @staticmethod
    def ReadTester(dfsFile, modifiedTimes):

        # Remember that time returns the timestep index.
        assert_equal(0 if modifiedTimes else 4, dfsFile.FileInfo.TimeAxis.StartTimeOffset);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(0.0 if modifiedTimes else 4.0, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(0, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_equal(0.0 if modifiedTimes else 4.0, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(100, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(10 if modifiedTimes else 14, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(1, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStep(1, 7);
        assert_equal(1, itemData.ItemNumber);
        assert_equal(70.0 if modifiedTimes else 74.0, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(11, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_equal(70.0 if modifiedTimes else 74.0, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(111, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(80.0 if modifiedTimes else 84.0, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(12, itemData.Data[0]);


# class testing the file TemporalNeqTime.dfs0.
# File was creating by the TsEditor.exe.
class FileTemporalNeqTimeDfs0:

    @staticmethod
    def TimeAxisTester(dfsFile, modifyTimes):
  
        timeAxis = dfsFile.FileInfo.TimeAxis;

        assert_equal(TimeAxisType.TimeNonEquidistant, timeAxis.TimeAxisType);
        assert_equal(0, timeAxis.FirstTimeStepIndex);
        assert_equal(10, timeAxis.NumberOfTimeSteps);
        assert_equal(3, timeAxis.StartTimeOffset);
        assert_equal(eumUnit.eumUsec, timeAxis.TimeUnit);

        neqCalTime = timeAxis

        assert_allclose(95, neqCalTime.TimeSpan, 1e-4);
        #assert_allclose(95, neqCalTime.TimeSpanInSeconds(), 1e-4);

        ## Testing search method
        #assert_equal( ~0, dfsFile.Search(modifyTimes ? -0.001 :  2.999));
        #assert_equal(  0, dfsFile.Search(modifyTimes ?  0     :  3));
        #assert_equal( ~1, dfsFile.Search(modifyTimes ?  0.001 :  3.001));

        #assert_equal(  4, dfsFile.Search(modifyTimes ? 50     : 53));
        #assert_equal( ~5, dfsFile.Search(modifyTimes ? 55     : 58));
        #assert_equal(  5, dfsFile.Search(modifyTimes ? 60     : 63));

        #assert_equal( ~9, dfsFile.Search(modifyTimes ? 94.999 : 97.999));
        #assert_equal(  9, dfsFile.Search(modifyTimes ? 95     : 98));
        #assert_equal(~10, dfsFile.Search(modifyTimes ? 95.001 : 98.001));


        #DateTime startTime = new DateTime(2010, 1, 4, 12, 34, 00);
        #var dtvar = new[]
        
        #    dfsFile.GetDateTimes(startTime, true),
        #    dfsFile.GetDateTimes(startTime, false)
        #  };
        #foreach (IReadOnlyList<DateTime> dateTimes in dtvar)
    
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 03), dateTimes[0]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 53), dateTimes[4]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 35, 03), dateTimes[5]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 35, 38), dateTimes[9]);
        #}

    @staticmethod
    def ReadTester(dfsFile, modifiedTimes):

        # Remember that itemData.Time is time since first time step, i.e., first itemData.Time is zero
        dfsFile.Reset();

        offset = 0 if (modifiedTimes) else 3;

        assert_equal(3, dfsFile.FileInfo.TimeAxis.StartTimeOffset);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(0.0+offset, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(0, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_allclose(0.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(100, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_allclose(10.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(1, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_allclose(10.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(101, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStep(1, 5);
        assert_equal(1, itemData.ItemNumber);
        assert_allclose(60.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(5, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_allclose(60.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(105, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_allclose(75.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(10, itemData.Data[0]);

# class testing the file TemporalNeqCal.dfs0.
# File was creating by the TsEditor.exe.
# 
# The TsEditor by default saves the file such
# that the start date time equals the time
# of the first time step, so the offset (tstart) will be
# zero.
class FileTemporalNeqCalDfs0:

    @staticmethod
    def TimeAxisTester(dfsFile, modifiedTimes):
  
        dateTimeOffset = 3 if (modifiedTimes) else 0;
        startTimeOffset = 0 if (modifiedTimes) else 3;

        timeAxis = dfsFile.FileInfo.TimeAxis;

        assert_equal(TimeAxisType.CalendarNonEquidistant, timeAxis.TimeAxisType);
        assert_equal(0, timeAxis.FirstTimeStepIndex);
        assert_equal(10, timeAxis.NumberOfTimeSteps);
        assert_equal(startTimeOffset, timeAxis.StartTimeOffset);
        assert_equal(eumUnit.eumUsec, timeAxis.TimeUnit);

        neqCalAxis = timeAxis

        assert_equal(datetime.datetime(2010, 1, 4, 12, 34, 00) + datetime.timedelta(seconds=dateTimeOffset), neqCalAxis.StartDateTime);
        assert_allclose(95, neqCalAxis.TimeSpan, 1e-4);
        #assert_allclose(95, neqCalAxis.TimeSpanInSeconds(), 1e-4);

        ## Testing search method
        #assert_equal( ~0, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 02)));
        #assert_equal(  0, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 03)));
        #assert_equal( ~1, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 04)));

        #assert_equal(  4, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 53)));
        #assert_equal( ~5, dfsFile.Search(new DateTime(2010, 1, 4, 12, 34, 58)));
        #assert_equal(  5, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 03)));

        #assert_equal( ~9, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 37)));
        #assert_equal(  9, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 38)));
        #assert_equal(~10, dfsFile.Search(new DateTime(2010, 1, 4, 12, 35, 38, 1)));

        #assert_equal( ~0, dfsFile.Search(modifiedTimes ? -0.001 :  2.999));
        #assert_equal(  0, dfsFile.Search(modifiedTimes ?  0     :  3));
        #assert_equal( ~1, dfsFile.Search(modifiedTimes ?  0.001 :  3.001));

        #assert_equal(  4, dfsFile.Search(modifiedTimes ? 50     : 53));
        #assert_equal( ~5, dfsFile.Search(modifiedTimes ? 55     : 58));
        #assert_equal(  5, dfsFile.Search(modifiedTimes ? 60     : 63));

        #assert_equal( ~9, dfsFile.Search(modifiedTimes ? 94.999 : 97.999));
        #assert_equal(  9, dfsFile.Search(modifiedTimes ? 95     : 98));
        #assert_equal(~10, dfsFile.Search(modifiedTimes ? 95.001 : 98.001));

        #var dtvar = new[]
        
        #    dfsFile.GetDateTimes(true),
        #    dfsFile.GetDateTimes(false)
        #  };
        #foreach (IReadOnlyList<DateTime> dateTimes in dtvar)
    
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 03), dateTimes[0]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 34, 53), dateTimes[4]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 35, 03), dateTimes[5]);
        #  assert_equal(new DateTime(2010, 1, 4, 12, 35, 38), dateTimes[9]);
        #}

    @staticmethod
    def ReadTester(dfsFile, modifyTimes):
  
        dfsFile.Reset();

        offset = 0 if (modifyTimes) else 3;

        assert_equal(offset, dfsFile.FileInfo.TimeAxis.StartTimeOffset);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_equal(0.0+offset, itemData.Time);
        assert_equal(1, itemData.Data.size);
        assert_equal(0, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_allclose(0.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(100, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_allclose(10.0 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(1, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_allclose(10.0+offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(101, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStep(1, 5);
        assert_equal(1, itemData.ItemNumber);
        assert_allclose(60.0+offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(5, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(2, itemData.ItemNumber);
        assert_allclose(60 + offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(105, itemData.Data[0]);

        itemData = dfsFile.ReadItemTimeStepNext();
        assert_equal(1, itemData.ItemNumber);
        assert_allclose(75+offset, itemData.Time, 1e-5);
        assert_equal(1, itemData.Data.size);
        assert_equal(10, itemData.Data[0]);



if __name__ == '__main__':
    unittest.main()
