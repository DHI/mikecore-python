from datetime import datetime
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *
from numpy.testing import *

class ExamplesDfs0:

    @staticmethod
    def CreateDfs0File(filename, calendarAxis):
        factory = DfsFactory();
        builder = DfsBuilder.Create("TemporalAxisTest");

        # Set up file header
        builder.SetDataType(1);
        builder.SetGeographicalProjection(factory.CreateProjectionUndefined());
        if (calendarAxis):
            builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(2010,  1,  4, 12, 34, 00), 4, 10));
        else:
            builder.SetTemporalAxis(factory.CreateTemporalEqTimeAxis(eumUnit.eumUsec, 3, 10));
        #builder.SetItemStatisticsType(StatType.RegularStat);

        # Set up first item
        item1 = builder.CreateDynamicItemBuilder();
        item1.Set("WaterLevel item", eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter), DfsSimpleType.Float);
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

        # Write data to file
        file.WriteItemTimeStepNext(0, np.array([  0], np.float32));  # water level
        file.WriteItemTimeStepNext(0, np.array([100], np.float32));  # water depth
        file.WriteItemTimeStepNext(0, np.array([  1], np.float32));  # water level
        file.WriteItemTimeStepNext(0, np.array([101], np.float32));  # water depth
        file.WriteItemTimeStepNext(0, np.array([  2], np.float32));  # water level
        file.WriteItemTimeStepNext(0, np.array([102], np.float32));  # water depth
        file.WriteItemTimeStepNext(0, np.array([  3], np.float32));  # etc...
        file.WriteItemTimeStepNext(0, np.array([103], np.float32));
        file.WriteItemTimeStepNext(0, np.array([  4], np.float32));
        file.WriteItemTimeStepNext(0, np.array([104], np.float32));
        file.WriteItemTimeStepNext(0, np.array([  5], np.float32));
        file.WriteItemTimeStepNext(0, np.array([105], np.float32));
        file.WriteItemTimeStepNext(0, np.array([ 10], np.float32));
        file.WriteItemTimeStepNext(0, np.array([110], np.float32));
        file.WriteItemTimeStepNext(0, np.array([ 11], np.float32));
        file.WriteItemTimeStepNext(0, np.array([111], np.float32));
        file.WriteItemTimeStepNext(0, np.array([ 12], np.float32));
        file.WriteItemTimeStepNext(0, np.array([112], np.float32));
        file.WriteItemTimeStepNext(0, np.array([ 13], np.float32));
        file.WriteItemTimeStepNext(0, np.array([113], np.float32));

        file.Close();

