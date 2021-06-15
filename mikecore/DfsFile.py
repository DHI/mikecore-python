import os.path
from enum import IntEnum
import datetime
import ctypes
import numpy as np
from mikecore.eum import *
from mikecore.DfsDLL import DfsDLL
from typing import Union
from mikecore.eum import eumQuantity

class NotSupportedException(Exception):
    pass

class ArgumentNullException(Exception):
    pass

class DfsFileMode(IntEnum):
    Read = 0
    Edit = 1
    Append = 2
    Closed = 3


class TimeAxisType(IntEnum):
    Undefined = 0
    TimeEquidistant = 1
    TimeNonEquidistant = 2
    CalendarEquidistant = 3
    CalendarNonEquidistant = 4


class DataValueType(IntEnum):
    """
    Data value type defines how one value is interpreted in time:
    Instantaneous : Value at current point in time, current time step.
    Accumulated : Value accumulated from start of time series to current time step.
    StepAccumulated : Value accumulated within time step, from last time step to current time step. 
    MeanStepBackward : Mean value from previous to current time step. Also called: mean step accumulated.
    MeanStepForward : Mean value from current to next time step. Also called: reverse mean step accumulated.
    """
    Instantaneous = 0
    Accumulated = 1
    StepAccumulated = 2
    MeanStepBackward = 3
    MeanStepForward = 4


class SpaceAxisType(IntEnum):
    Undefined = 0
    EqD0 = 1
    EqD1 = 2
    NeqD1 = 3
    # TvarD1        =  4;
    EqD2 = 5
    NeqD2 = 6
    # TvarD2        =  7;
    EqD3 = 8
    NeqD3 = 9
    # TvarD3        = 10;
    # EqD4          = 11;
    CurveLinearD2 = 12
    CurveLinearD3 = 13


class DfsSimpleType(IntEnum):
    Float = 1
    Double = 2
    Byte = 3
    Int = 4
    UInt = 5
    Short = 6
    UShort = 7


class ProjectionType(IntEnum):
    """
    Projection type, specifies whether file has projection or not. 
    All newer files has a projection defined, though there exists 
    older files which does not have a projection (Undefined).
    """
    Undefined = 0
    Projection = 1


class UnitConversionType(IntEnum):
    """
    Type of unit conversion, when reading item
    data and axis.
    NoConversion : No conversion, default
    UbgConversion : Convert to/from UBG (Unit Base Group), user defined.
    FreeConversion : Convert to/from user defined unit, which must also be provided with this type.
    FirstRegisteredUnitConversion : Converts to/from the first registered unit (default EUM unit) for the given item type.
    """
    NoConversion = 0
    UbgConversion = 1
    FreeConversion = 2
    FirstRegisteredUnitConversion = 3

class StatType(IntEnum):
    Undefined = 0
    NoStat = 1
    RegularStat = 2
    LargevalStat = 3


class DfsParameters:
    """Parameters that can be set for a dfs file."""

    def __init__(self):
        self.ModifyTimes = False

class DfsProjection:
    """
      Defines a projection and its coordinate transforms.

      You can use the <code>DHI.Projections</code> to handle the
      difference coordinate systems involved in a dfs file. Also
      see there for detailed documentation.

      The `WKTString` is a WKT string for a spatial 
      reference system. A number of abbreviated strings also exists, 
      i.e., "UTM-33" for a WGS-84 UTM zone 33 projection, 
      and "LONG/LAT" for WGS-84 geographical coordinates.

      There are 3 levels of coordinates:
      - Geographical coordinates (longitude, latitude) in degrees, 
      - Projection coordinates (easting, northing), and
      - Model/user defined coordinates (x,y).

      All coordinates in a dfs file are stored in model coordinates.

      The `WKTString` defines which ellipsoid the geographical coordinates use (example: WGS-84).

      The `WKTString` defines the mapping from geographical coordinates to projection coordinates.

      The `Longitude`, `Latitude` and `Orientation` defines the origin and the 
      orientation of the model coordinates. It is used to move and rotate
      the model coordinates, i.e., a dfs2 file with a 2D equidistant axis  
      defines its model coordinate origin and orientation here (and not in 
      its axis definition, though that would also be possible).

      `Orientation` is the rotation from true north to the model coordinate 
      y-axis in degrees, measured positive clockwise.

      If `Orientation` is zero, and `Longitude` and `Latitude`
      matches the origin of the projection coordinate system, then projection coordinates equals model
      coordinates. Example: UTM-31 has projection origin at (lon,lat) = (3,0). 
    """
    def __init__(self, type, wktString: str, longitude: float = 0.0, latitude: float = 0.0, orientation: float = 0.0):
        self.Type = type;
        self.WKTString = wktString;
        self.Longitude = longitude;
        self.Latitude = latitude;
        self.Orientation = orientation;
    
    @staticmethod
    def Create(wktString: str):
        if (wktString == None or wktString == ""):
            raise Exception("Projection string can not be null or empty");
        return DfsProjection(ProjectionType.Projection, wktString, 0.0, 0.0, 0.0)
    
    @staticmethod
    def CreateWithGeoOrigin(wktString: str, lon0: float, lat0: float, orientation: float):
        if (wktString == None or wktString == ""):
            raise Exception("Projection string can not be null or empty");
        return DfsProjection(ProjectionType.Projection, wktString, lon0, lat0, orientation)

class DfsTemporalAxis:
    def __init__(
        self, timeUnit, startTimeOffset, numberOfTimeSteps, firstTimeStepIndex
    ):
        self.TimeAxisType = TimeAxisType.Undefined
        self._TimeUnit = timeUnit
        self._StartTimeOffset = startTimeOffset
        self.NumberOfTimeSteps = numberOfTimeSteps
        self._FirstTimeStepIndex = firstTimeStepIndex
        self._OnUpdate = None;
        self.__calcToSecFactor();

    # Method that is invoked when ever the temporal axis is updated.
    def _InvokeOnUpdate(self):
        if self._OnUpdate != None:
            self._OnUpdate()

    def __getTimeUnit(self):
        return self._TimeUnit;
    def __setTimeUnit(self, timeUnit):
        self._TimeUnit = timeUnit
        self._InvokeOnUpdate();
        self.__calcToSecFactor();
    TimeUnit = property(__getTimeUnit, __setTimeUnit)

    def __calcToSecFactor(self):
        if self._TimeUnit == eumUnit.eumUmillisec: self._toSecondsFactor = 0.001; return;
        if self._TimeUnit == eumUnit.eumUsec:      self._toSecondsFactor = 1.0; return;
        if self._TimeUnit == eumUnit.eumUminute:   self._toSecondsFactor = 60.0; return;
        if self._TimeUnit == eumUnit.eumUhour:     self._toSecondsFactor = 3600.0; return;
        if self._TimeUnit == eumUnit.eumUday:      self._toSecondsFactor = 86400.0; return;
        self._toSecondsFactor = 1.0;
        if (eumWrapper.eumUnitsEqv(self._TimeUnit, eumUnit.eumUsec)):
            res = eumWrapper.eumConvertUnit(self._TimeUnit, 1.0, eumUnit.eumUsec);
            if res[0]:
                self._toSecondsFactor = res[1]
            else:
                self._toSecondsFactor = 1.0;


    def __getStartTimeOffset(self):
        return self._StartTimeOffset;
    def __setStartTimeOffset(self, startTimeOffset):
        self._StartTimeOffset = startTimeOffset
        self._InvokeOnUpdate();
    StartTimeOffset = property(__getStartTimeOffset, __setStartTimeOffset)

    def __getFirstTimeStepIndex(self):
        return self._FirstTimeStepIndex;
    def __setFirstTimeStepIndex(self, firstTimeStepIndex):
        self._FirstTimeStepIndex = firstTimeStepIndex
        self._InvokeOnUpdate();
    FirstTimeStepIndex = property(__getFirstTimeStepIndex, __setFirstTimeStepIndex)

    def IncrementNumberOfTimeSteps(self, time):
        self.NumberOfTimeSteps += 1

    def IsEquidistant(self):
        return (   self.TimeAxisType == TimeAxisType.CalendarEquidistant 
                or self.TimeAxisType == TimeAxisType.TimeEquidistant)

    def IsCalendar(self):
        return (   self.TimeAxisType == TimeAxisType.CalendarEquidistant 
                or self.TimeAxisType == TimeAxisType.CalendarNonEquidistant)

    def ToSeconds(self, relativeTime):
        return relativeTime * self._toSecondsFactor;

    def ToRelativeTime(self, relativeSeconds):
        return relativeSeconds / self._toSecondsFactor;


class DfsEqTimeAxis(DfsTemporalAxis):
    def __init__(
        self, timeUnit, startTimeOffset, timeStep, numberOfTimeSteps, firstTimeStepIndex
    ):
        super().__init__(
            timeUnit, startTimeOffset, numberOfTimeSteps, firstTimeStepIndex
        )
        self.TimeAxisType = TimeAxisType.TimeEquidistant
        self._TimeStep = timeStep

    def __getTimeStep(self):
        return self._TimeStep;
    def __setTimeStep(self, timeStep):
        self._TimeStep = timeStep
        self._InvokeOnUpdate();
    TimeStep = property(__getTimeStep, __setTimeStep)

    def TimeStepInSeconds(self):
        return self.TimeStep * self._toSecondsFactor;


class DfsNonEqTimeAxis(DfsTemporalAxis):
    def __init__(
        self, timeUnit, startTimeOffset, numberOfTimeSteps, timeSpan, firstTimeStepIndex
    ):
        super().__init__(
            timeUnit, startTimeOffset, numberOfTimeSteps, firstTimeStepIndex
        )
        self.TimeAxisType = TimeAxisType.TimeNonEquidistant
        self.TimeSpan = timeSpan

    def IncrementNumberOfTimeSteps(self, time):
        self.NumberOfTimeSteps += 1
        self.TimeSpan = time - self.StartTimeOffset;


class DfsEqCalendarAxis(DfsTemporalAxis):
    def __init__(
        self,
        timeUnit,
        startDateTime,
        startTimeOffset,
        timeStep,
        numberOfTimeSteps,
        firstTimeStepIndex,
    ):
        super().__init__(
            timeUnit, startTimeOffset, numberOfTimeSteps, firstTimeStepIndex
        )
        self.TimeAxisType = TimeAxisType.CalendarEquidistant
        self._StartDateTime = startDateTime
        self._TimeStep = timeStep

    def __getStartDateTime(self):
        return self._StartDateTime;
    def __setStartDateTime(self, startDateTime):
        self._StartDateTime = startDateTime;
        self._InvokeOnUpdate();
    StartDateTime = property(__getStartDateTime, __setStartDateTime)

    def __getTimeStep(self):
        return self._TimeStep;
    def __setTimeStep(self, timeStep):
        self._TimeStep = timeStep
        self._InvokeOnUpdate();
    TimeStep = property(__getTimeStep, __setTimeStep)

    def TimeStepInSeconds(self):
        return self.TimeStep * self._toSecondsFactor;

class DfsNonEqCalendarAxis(DfsTemporalAxis):
    def __init__(
        self,
        timeUnit,
        startDateTime,
        startTimeOffset,
        timeSpan,
        numberOfTimeSteps,
        firstTimeStepIndex,
    ):
        super().__init__(
            timeUnit, startTimeOffset, numberOfTimeSteps, firstTimeStepIndex
        )
        self.TimeAxisType = TimeAxisType.CalendarNonEquidistant
        self._StartDateTime = startDateTime
        self.TimeSpan = timeSpan

    def __getStartDateTime(self):
        return self._StartDateTime;
    def __setStartDateTime(self, startDateTime):
        self._StartDateTime = startDateTime;
        self._InvokeOnUpdate();
    StartDateTime = property(__getStartDateTime, __setStartDateTime)

    def IncrementNumberOfTimeSteps(self, time):
        self.NumberOfTimeSteps += 1
        self.TimeSpan = time - self.StartTimeOffset;


class DfsSpatialAxis:
    def __init__(self, axisType, shape, sizeOfData, axisUnit):
        self.AxisType   = axisType
        self.Shape      = shape
        self.Dimension  = len(shape)
        self.SizeOfData = sizeOfData
        self.AxisUnit   = axisUnit


class DfsAxisEqD0(DfsSpatialAxis):
    def __init__(self, axisUnit = eumUnit.eumUmeter):
        super().__init__(SpaceAxisType.EqD0, (0,), 1, axisUnit)

    @staticmethod
    def Create():
        return DfsAxisEqD0()


class DfsAxisEqD1(DfsSpatialAxis):
    def __init__(self, axisUnit, xCount, x0, dx):
        super().__init__(SpaceAxisType.EqD1, (xCount,), xCount, axisUnit)
        self.XCount = xCount
        self.X0 = x0
        self.Dx = dx
    
    @staticmethod
    def CreateDummyAxis(xCount):
        axis = DfsAxisEqD1(
            eumUnit.eumUUnitUndefined,
            xCount, 0.0, 1.0);
        return (axis);


class DfsAxisEqD2(DfsSpatialAxis):
    def __init__(self, axisUnit, xCount, x0, dx, yCount, y0, dy):
        super().__init__(SpaceAxisType.EqD2, (xCount,yCount), xCount*yCount, axisUnit)
        self.XCount = xCount
        self.X0 = x0
        self.Dx = dx
        self.YCount = yCount
        self.Y0 = y0
        self.Dy = dy


class DfsAxisEqD3(DfsSpatialAxis):
    def __init__(self, axisUnit, xCount, x0, dx, yCount, y0, dy, zCount, z0, dz):
        super().__init__(SpaceAxisType.EqD3, (xCount,yCount,zCount), xCount*yCount*zCount, axisUnit)
        self.XCount = xCount
        self.X0 = x0
        self.Dx = dx
        self.YCount = yCount
        self.Y0 = y0
        self.Dy = dy
        self.ZCount = zCount
        self.Z0 = z0
        self.Dz = dz


class DfsAxisNeqD1(DfsSpatialAxis):
    def __init__(self, axisUnit, coords):
        super().__init__(SpaceAxisType.NeqD1, (len(coords),), len(coords), axisUnit)
        self.Coordinates = coords


class DfsAxisNeqD2(DfsSpatialAxis):
    def __init__(self, axisUnit, xCoords, yCoords):
        super().__init__(SpaceAxisType.NeqD2, ((len(xCoords)-1),(len(yCoords)-1)), (len(xCoords)-1)*(len(yCoords)-1), axisUnit)
        self.XCoordinates = xCoords
        self.YCoordinates = yCoords


class DfsAxisNeqD3(DfsSpatialAxis):
    def __init__(self, axisUnit, xCoords, yCoords, zCoords):
        super().__init__(SpaceAxisType.NeqD2, ((len(xCoords)-1),(len(yCoords)-1),(len(zCoords)-1)), (len(xCoords)-1)*(len(yCoords)-1)*(len(zCoords)-1), axisUnit)
        self.XCoordinates = xCoords
        self.YCoordinates = yCoords
        self.ZCoordinates = zCoords


class DfsAxisCurveLinearD2(DfsSpatialAxis):
    def __init__(self, axisUnit, xCount, yCount, xCoords, yCoords):
        super().__init__(SpaceAxisType.CurveLinearD2, (xCount,yCount), xCount*yCount, axisUnit)
        self.XCount = xCount
        self.YCount = yCount
        self.XCoordinates = xCoords
        self.YCoordinates = yCoords

class DfsAxisCurveLinearD3(DfsSpatialAxis):
    def __init__(self, axisUnit, xCount, yCount, zCount, xCoords, yCoords, zCoords):
        super().__init__(SpaceAxisType.CurveLinearD3,  (xCount,yCount,zCount), xCount*yCount*zCount, axisUnit)
        self.XCount = xCount
        self.YCount = yCount
        self.ZCount = zCount
        self.XCoordinates = xCoords
        self.YCoordinates = yCoords
        self.ZCoordinates = zCoords

class DfsDynamicItemInfo:
    def __init__(self, itemPointer = None, itemNumber = 0):
        self.ItemPointer = itemPointer
        self.ItemNumber  = itemNumber
        self.DataType    = DfsSimpleType.UShort
        self.Name        = ""
        self.ElementCount = -1
        self.Quantity = None
        self.ReferenceCoordinateX = np.float32(-1e-35)
        self.ReferenceCoordinateY = np.float32(-1e-35)
        self.ReferenceCoordinateZ = np.float32(-1e-35)
        self.OrientationAlpha = np.float32(-1e-35)
        self.OrientationPhi   = np.float32(-1e-35)
        self.OrientationTheta = np.float32(-1e-35)
        self.ConversionType = UnitConversionType.NoConversion
        self.ConversionUnit = 0
        self.AxisConversionType = UnitConversionType.NoConversion
        self.AxisConversionUnit = 0
        self.AssociatedStaticItemNumbers = []
        self.SpatialAxis = None

    def __repr__(self):
        return (
            'DfsItem("'
            + self.Name
            + '", ('
            + str(self.Quantity)
            + "), "
            + self.DataType.name
            + ")"
        )

    def init(self, itemName, eumQuantity):
        self.Name     = itemName
        self.Quantity = eumQuantity

    def SetReferenceCoordinates(self, x, y, z):
        self.ReferenceCoordinateX = x
        self.ReferenceCoordinateY = y
        self.ReferenceCoordinateZ = z

    def SetOrientation(self, alpha, phi, theta):
        self.OrientationAlpha = alpha;
        self.OrientationPhi   = phi;
        self.OrientationTheta = theta;

    def SetUnitConversion(self, conversionType, conversionUnit):
        self.ConversionType = conversionType
        self.ConversionUnit = conversionUnit

    def SetAxisUnitConversion(self, conversionType, conversionUnit):
        self.AxisConversionType = conversionType
        self.AxisConversionUnit = conversionUnit

    def CreateEmptyItemData(self, reshape = False):
        data = self.CreateEmptyItemDataData(reshape)
        return DfsItemData(0, self.ItemNumber, 0.0, data)

    def CreateEmptyItemDataData(self, reshape = False):
        if self.DataType == DfsSimpleType.Float:
            values = np.zeros(self.ElementCount, dtype=np.float32)
        elif self.DataType == DfsSimpleType.Double:
            values = np.zeros(self.ElementCount, dtype=np.float64)
        elif self.DataType == DfsSimpleType.Int:
            values = np.zeros(self.ElementCount, dtype=np.int32)
        elif self.DataType == DfsSimpleType.UInt:
            values = np.zeros(self.ElementCount, dtype=np.uint32)
        elif self.DataType == DfsSimpleType.Byte:
            values = np.zeros(self.ElementCount, dtype=np.int8)
        elif self.DataType == DfsSimpleType.Short:
            values = np.zeros(self.ElementCount, dtype=np.int16)
        elif self.DataType == DfsSimpleType.UShort:
            values = np.zeros(self.ElementCount, dtype=np.uint16)
        else:
            print("Ahhrrggg!!!!: {}-{}".format(self.DataType,self.ElementCount))
        if (reshape):
            values = values.reshape(self.SpatialAxis.Shape, order = 'F')
        return values;

class DfsStaticItem(DfsDynamicItemInfo):
    def __init__(self, dfsFile = None, vectorPointer = None, itemPointer = None, itemNumber = None):
        super().__init__(itemPointer, itemNumber)
        self.DfsFile = dfsFile
        self.VectorPointer = vectorPointer
        self.Data = None
    @staticmethod
    def Create(name, quantity, data, spatialAxis = None):
        if (spatialAxis is None):
            if (data.size == 1):
                spatialAxis = DfsAxisEqD0.Create();
            else:
                spatialAxis = DfsAxisEqD1.CreateDummyAxis(data.size);
        staticItem = DfsStaticItem()
        staticItem.Name = name
        staticItem.Quantity = quantity
        staticItem.Data = data
        staticItem.DataType = DfsDLLUtil.GetDfsType(data)
        staticItem.SpatialAxis = spatialAxis
        staticItem.ElementCount = spatialAxis.SizeOfData
        return staticItem

class DfsItemData:
    def __init__(self, timestepIndex, itemNumber, time, data):
        self.TimeStepIndex = timestepIndex
        self.ItemNumber = itemNumber
        self.Time = time
        self.Data = data

    def __repr__(self):
        return (
            "DfsItemData("
            + str(self.TimeStepIndex)
            + ","
            + str(self.ItemNumber)
            + ","
            + str(self.Time)
            + ")"
        )


class DfsFileInfo:
    """File info, containing header data."""

    def __init__(self):
        self.DfsFile = None
        self.FileName = ""
        self.FileTitle = ""
        self.ApplicationTitle = "MIKE Core Python"
        self.ApplicationVersion = int(1)
        self.DataType = 0

        # self.FileType = None;
        self.StatsType = StatType.NoStat;

        # TODO: Check which items are loaded and which delete value to store, and if only one, store in DeleteValue
        self.DeleteValueFloat       = DfsFile.DefaultDeleteValueFloat
        self.DeleteValueDouble      = DfsFile.DefaultDeleteValueDouble
        self.DeleteValueByte        = DfsFile.DefaultDeleteValueByte
        self.DeleteValueInt         = DfsFile.DefaultDeleteValueInt
        self.DeleteValueUnsignedInt = DfsFile.DefaultDeleteValueUnsignedInt

        self.Projection = None
        self.TimeAxis = None
        self.CustomBlocks = []

        self.IsFileCompressed = False
        self.xKey = None
        self.yKey = None
        self.zKey = None

    def InitRead(self, dfsFile, headerPointer, parameters=DfsParameters()):

        # header pointer is assigned before any other code is issued, in order to
        # make sure that the destructor can destroy it in case of failures.
        self.DfsFile = dfsFile

        # The dfsParamModifyTimes must be called before getting the temporal axis.
        DfsDLL.Wrapper.dfsParamModifyTimes(headerPointer, ctypes.c_int32(parameters.ModifyTimes))

        self.FileName = dfsFile.FileName
        self.FileTitle = DfsDLL.Wrapper.dfsGetFileTitle(headerPointer).decode("cp1252", "replace")
        self.ApplicationTitle = DfsDLL.Wrapper.dfsGetAppTitle(headerPointer).decode("cp1252", "replace")
        self.ApplicationVersion = DfsDLL.Wrapper.dfsGetAppVersionNo(headerPointer)
        self.DataType = DfsDLL.Wrapper.dfsGetDataType(headerPointer)

        # self.FileType = None;
        # self.StatsType = None;

        # TODO: Check which items are loaded and which delete value to store, and if only one, store in DeleteValue
        self.DeleteValueFloat = DfsDLL.Wrapper.dfsGetDeleteValFloat(headerPointer)
        self.DeleteValueByte = DfsDLL.Wrapper.dfsGetDeleteValByte(headerPointer)
        self.DeleteValueDouble = DfsDLL.Wrapper.dfsGetDeleteValDouble(headerPointer)
        self.DeleteValueInt = DfsDLL.Wrapper.dfsGetDeleteValInt(headerPointer)
        self.DeleteValueUnsignedInt = DfsDLL.Wrapper.dfsGetDeleteValUnsignedInt(headerPointer)

        # TODO: implement
        self.Projection = DfsDLLUtil.GetProjection(headerPointer)
        self.TimeAxis   = DfsDLLUtil.GetTemporalAxis(headerPointer)
        self.CustomBlocks = DfsDLLUtil.BuildCustomBlocks(headerPointer)
        self.IsFileCompressed = (DfsDLL.Wrapper.dfsIsFileCompressed(headerPointer) != 0)

        self.TimeAxis._OnUpdate = self.__UpdateTemporalAxis;

        # TODO: Test on dfs3 file from MIKE SHE
        if self.IsFileCompressed:
            encodeKeySize = DfsDLL.Wrapper.dfsGetEncodeKeySize(headerPointer)
            self.xKey = np.zeros(encodeKeySize, dtype=np.int32)
            self.yKey = np.zeros(encodeKeySize, dtype=np.int32)
            self.zKey = np.zeros(encodeKeySize, dtype=np.int32)
            DfsDLL.Wrapper.dfsGetEncodeKey(
                headerPointer,
                self.xKey.ctypes.data,
                self.yKey.ctypes.data,
                self.zKey.ctypes.data,
            )

    def GetEncodeKey(self):
        return self.xKey, self.yKey, self.zKey

    def SetEncodingKey(self, xKey, yKey, zKey):
        if xKey == None:
            raise ArgumentNullException("xKey")
        if yKey == None:
            raise ArgumentNullException("yKey")
        if zKey == None:
            raise ArgumentNullException("zKey")

        encodeKeySize = len(xKey)
        if encodeKeySize != len(yKey) or encodeKeySize != len(zKey):
            raise ValueError("Encoding key arguments must have same length")

        self.xKey = xKey
        self.yKey = yKey
        self.zKey = zKey

    def __UpdateTemporalAxis(self):
        DfsDLLUtil.dfsSetTemporalAxis(self.DfsFile.headPointer, self.TimeAxis)

class DfsCustomBlock():
    def __init__(self, name, datatype, values):
        self.Name = name
        self.SimpleType = datatype
        self.Values = values
        self.Count = values.size
    def __getitem__(self, key):
        return self.Values[key]
    def __setitem__(self, key, value):
        self.Values[key] = value


class DfsFilePointerState(IntEnum):
    StaticItem = 0
    DynamicItem = 1
    CreatingItems = 2


class DfsFile:
    """Class for reading DFS file data using the dfs C API"""

    # Default values for DeleteValues
    DefaultDeleteValueByte = 0
    DefaultDeleteValueFloat = -1.0e-35
    DefaultDeleteValueDouble = -1.0e-255
    DefaultDeleteValueInt = 2147483647
    DefaultDeleteValueUnsignedInt = 2147483647

    def __init__(self):
        DfsDLL.Init()
        self.fpState = DfsFilePointerState.StaticItem
        self.fpItemNumber = 1
        self.fpTimeStepIndex = 0
        self.headPointer = ctypes.c_void_p(0)
        self.filePointer = ctypes.c_void_p(0)

    def __del__(self):
        self.Close()

    def Open(self, filename, mode = DfsFileMode.Read, parameters=None):
        """
        Open file
        
        Parameters
        ---------
        filename: name and path of file to open
        """

        # Close file, if already open
        if (self.filePointer.value != None):
            self.Close()

        if (not os.path.isfile(filename)):
            raise Exception("File not found {}".format(filename))

        # Check if trying to edit a read-only file.
        if ((mode == DfsFileMode.Edit or mode == DfsFileMode.Append) 
            and (not os.access(filename, os.W_OK))):
            raise Exception("File is readonly and can not be opened for editing: " + filename);

        if (parameters is None):
            parameters = DfsParameters()

        self.FileName = filename
        self.FileMode = mode
        self.filePointer = ctypes.c_void_p()
        self.headPointer = ctypes.c_void_p()
        # Marshal filename string to C char*
        fnp = ctypes.c_char_p()
        fnp.value = filename.encode("cp1252")

        if mode is DfsFileMode.Read:
            # Open file for reading
            rok = DfsDLL.Wrapper.dfsFileRead(
                fnp.value, ctypes.byref(self.headPointer), ctypes.byref(self.filePointer)
            )
        if mode is DfsFileMode.Edit:
            rok = DfsDLL.Wrapper.dfsFileEdit(
                fnp.value, ctypes.byref(self.headPointer), ctypes.byref(self.filePointer)
            )
        if mode is DfsFileMode.Append:
            rok = DfsDLL.Wrapper.dfsFileAppend(
                fnp.value, ctypes.byref(self.headPointer), ctypes.byref(self.filePointer)
            )

        if (rok != 0):
            raise Exception("Could not load file {} (Error code {})".format(filename, rok))

        self.FileInfo = DfsFileInfo()
        self.FileInfo.InitRead(self, self.headPointer, parameters)

        # Load Items
        noOfItems = DfsDLL.Wrapper.dfsGetNoOfItems(self.headPointer)
        self.ItemInfo = []
        for i in range(noOfItems):
            self.ItemInfo.append(self.__DynamicItemInfoReadAndCreate(i + 1, noOfItems))

        if mode is DfsFileMode.Read:
            # file pointer is after header part
            self.fpState = DfsFilePointerState.StaticItem;
            self.fpItemNumber = 1;
            self.fpTimeStepIndex = 0;
        if mode is DfsFileMode.Edit:
            # file pointer is after header part
            self.fpState = DfsFilePointerState.StaticItem;
            self.fpItemNumber = 1;
            self.fpTimeStepIndex = 0;
        if mode is DfsFileMode.Append:
            # file pointer is after last time step
            self.fpState = DfsFilePointerState.DynamicItem;
            self.fpItemNumber = 1;
            self.fpTimeStepIndex = self.FileInfo.TimeAxis.NumberOfTimeSteps;

    def Building(self, filename, headPointer, filePointer):
        self.FileName = filename
        self.FileMode = DfsFileMode.Append
        self.headPointer = headPointer
        self.filePointer = filePointer
        self.fpState = DfsFilePointerState.CreatingItems;
        self.fpItemNumber = 1;
        self.fpTimeStepIndex = -1;

        self.FileInfo = DfsFileInfo()
        self.FileInfo.InitRead(self, headPointer)

        # Load Items
        self.ItemInfo = []
        noOfItems = DfsDLL.Wrapper.dfsGetNoOfItems(headPointer)
        for i in range(noOfItems):
            self.ItemInfo.append(self.__DynamicItemInfoReadAndCreate(i + 1, noOfItems))


    def Close(self):
        """
        Close the file and release all ressources associated with it. The header information
        is still valid (for reading) even though the file has been closed.
        """
        if (self.filePointer.value != None):
            DfsDLL.Wrapper.dfsFileClose(self.headPointer, ctypes.byref(self.filePointer))
        if (self.headPointer.value != None):
            DfsDLL.Wrapper.dfsHeaderDestroy(ctypes.byref(self.headPointer))


    def GetNextItemNumber(self):
        return self.fpItemNumber


    def GetNextTimeStepIndex(self):
        return self.fpTimeStepIndex


    def ReadStaticItemNext(self):
        """
        Reads the next static item. First time called it returns the first
        static item. 
        
        If `ReadStaticItem` is called for example with argument 
        staticItemNo 3, the next call to this method will return static item number 4.
        
        If one of the methods reading/writing dynamic item data is called, see 
        `IDfsFileIO`, the static item number is reset, and 
        the next call to this method again returns the first item number.

        :returns: The next static item, null if no more items are present.
        """
        self.__CheckIfOpen()

        if (self.fpState == DfsFilePointerState.CreatingItems):
            raise Exception("Can not read static items when file is being created.")

        if (self.fpState != DfsFilePointerState.StaticItem):
            DfsDLL.Wrapper.dfsFindBlockStatic(self.headPointer, self.filePointer)
            self.fpState = DfsFilePointerState.StaticItem
            self.fpItemNumber = 1
            self.fpTimeStepIndex = -1

        staticItem = self.__StaticItemReadAndCreate(self.fpItemNumber, False)

        if (staticItem != None):
            self.fpItemNumber += 1
        return (staticItem)

    def ReadStaticItem(self, staticItemNo):
        """
        Read the number <paramref name="staticItemNo"/> static item from the file.

        :param staticItemNo: Number of static item in the file to read. First static item has number 1
        :returns: The static item number <paramref name="staticItemNo"/>, null if there are not that many static items.
        """
        self.__CheckIfOpen();
        if (self.fpState == DfsFilePointerState.CreatingItems):
            raise Exception("Can not read static items when file is being created.");

        if (self.fpState != DfsFilePointerState.StaticItem or self.fpItemNumber != staticItemNo):
            DfsDLL.Wrapper.dfsFindItemStatic(self.headPointer, self.filePointer, staticItemNo);
            self.fpState = DfsFilePointerState.StaticItem;
            self.fpItemNumber = staticItemNo;
            self.fpTimeStepIndex = -1;
        return (self.ReadStaticItemNext());


    def WriteStaticItemData(self, staticItem, data: np.ndarray):
        """
        Write the static item back to the file. the <paramref name="staticItem"/> must
        originate from this file. This will update and overwrite the static item information and 
        the data of the static item. 
        :param staticItem: Static item to update
        :param data: New data to insert. Data length must match the data size of the static item.
        """
        self.__CheckIfOpen();
        stItem = staticItem
        if (data is None):
            raise Exception("data is not defined");
        if (self.fpState != DfsFilePointerState.CreatingItems):
            if (stItem.ItemNumber <= 0):
                raise Exception("ItemNumber for static item is zero or negative.");
            # We are updating an existing static vector, position file pointer
            if (self.fpState != DfsFilePointerState.StaticItem or self.fpItemNumber != stItem.ItemNumber):
                DfsDLL.Wrapper.dfsFindItemStatic(self.headPointer, self.filePointer, stItem.ItemNumber);
                self.fpState = DfsFilePointerState.StaticItem;
                self.fpItemNumber = stItem.ItemNumber;
                self.fpTimeStepIndex = -1;

        # Check length of data
        # data.Length can be larger than the number of elements.
        if (stItem.ElementCount > data.size):
            raise Exception("Length of data does not match size of static vector.");
        # Check type of data, and save to disc.
        if (DfsDLLUtil.GetDfsType(data) != stItem.DataType):
            raise Exception("Type of data defined in static item does not match type of data argument.");

        rok = DfsDLL.Wrapper.dfsStaticWrite(stItem.VectorPointer, self.filePointer, data.ctypes.data);
        DfsDLL.CheckReturnCode(rok);
        self.fpItemNumber += 1;


    def ReadItemTimeStepNext(self, itemData: DfsItemData = None, reshape: bool = False) -> DfsItemData:
        """
        Reads the next dynamic item-timestep. First time called it returns the first
        timestep of the first item. It cycles through each timestep, and each 
        item in the timestep. For a file with 3 items, it returns (itemnumber, timestepIndex)
        in the following order:
        (1,0), (2,0), (3,0), (1,1), (2,1), (3,1), (1,2), etc. 

        If one of the ReadItemTimeStep is called with for example (1,4) 
        the next call to this method will continue from there and return (2,4).

        If one of the methods reading/writing static item data is called,
        the iterator is reset, and the next call to this method again
        returns the first item-timestep.

        This is the most efficient way to iterate through all the items and timesteps in a file,
        since it iterates exactly as the data is stored on the disk.

        :param itemData DfsItemData: DfsItemData for item to store timestep values in, for reuse of memory.
        :param reshape bool: Reshape data array to dimension of data, 2D or 3D depending on spatial axis.
        :returns DfsIemData: The next dynamic item-timestep, None if no more items are present.
        """
        self.__CheckIfOpen()
        if (self.fpState == DfsFilePointerState.CreatingItems):
            raise Exception("No dynamic items have been written to the file yet (file is being created).");

        if self.fpState != DfsFilePointerState.DynamicItem:
            # Position file pointer at first timestep and first item.
            self.__FpFindBlockDynamic()

        # TODO: size of item and hence the values array
        item = self.ItemInfo[self.fpItemNumber - 1]

        if (itemData is None):
            values = item.CreateEmptyItemDataData()
        else:
            values = itemData.Data

        if (values.size != item.ElementCount):
            raise Exception("itemData.Data is of incorrect size")

        timep = ctypes.c_double(0)
        success = DfsDLL.Wrapper.dfsReadItemTimeStep(
            self.headPointer, self.filePointer, ctypes.byref(timep), values.ctypes.data
        )

        if success != 0:
            return None
        time = self.__GetTime(timep.value, self.fpTimeStepIndex)
        if (itemData is None):
            res = DfsItemData(self.fpTimeStepIndex, self.fpItemNumber, time, values)
        else:
            res = itemData
            res.Time = time
            res.TimeStepIndex = self.fpTimeStepIndex
        self.__FpDynamicIncrement()
        return res


    def ReadItemTimeStep(self, itemNumber: Union[int,DfsItemData], timestepIndex: int, reshape: bool = False) -> DfsItemData:
        """
        Reads the dynamic item-timestep as specified from the file. It throws an
        exception if itemNumber or timestepIndex
        is out of range.

        :param itemNumber Union[int,DfsItemData]: Item number (1-based), or DfsItemData for item
        :param timestepIndex int: Time step index (0-based)
        :param reshape bool: Reshape data array to dimension of data, 2D or 3D depending on spatial axis.
        :return DfsItemData: The dynamic item-timestep as specified
        """
        self.__CheckIfOpen();
        if (self.fpState == DfsFilePointerState.CreatingItems):
            raise Exception("No dynamic items have been written to the file yet (file is being created).");

        if isinstance(itemNumber, DfsItemData):
            itemData = itemNumber
            itemNumber = itemNumber.ItemNumber
        else:
            itemData = None

        itemInfoCount = len(self.ItemInfo);

        # Check item number and timestep index ranges
        if (itemInfoCount == 0): 
            raise Exception("File has no dynamic items.");
        if (itemNumber <= 0 or itemNumber > itemInfoCount):
            raise Exception("itemNumber","Must be within [1,NumberOfItems].");
        if (timestepIndex < 0 or timestepIndex >= self.FileInfo.TimeAxis.NumberOfTimeSteps):
            raise Exception("timestepIndex", "Must be within [0," + (self.FileInfo.TimeAxis.NumberOfTimeSteps-1) + "].");

        # Position file pointer
        self.__FpFindItemTimeStep(itemNumber, timestepIndex);
        return (self.ReadItemTimeStepNext(itemData, reshape));

    def __GetTime(self, time, timestepIndex):
        # TODO: This assumes time in seconds?
        timeaxis = self.FileInfo.TimeAxis
        if timeaxis.TimeAxisType == TimeAxisType.TimeEquidistant:
            return timeaxis.StartTimeOffset + timestepIndex * timeaxis.TimeStep
        elif timeaxis.TimeAxisType == TimeAxisType.CalendarEquidistant:
            return timeaxis.StartTimeOffset + timestepIndex * timeaxis.TimeStep
        return time


    def WriteItemTimeStep(self, itemNumber, timestepIndex, time, data):
        """
        Writes data to the specified item and timestep in the file. 

        If the item-timestep exists already, data is updated. If it does not
        exist, the item number and timestep index must match exactly the next
        item-timestep after the last one in the file.

        The size of the data must match the data size of the item that is to be written.

        The time value is only relevant for files with non-equidistant time axis.
        For files with an equidistant time axis, the time value is ignored, and a zero can be used.

        :param itemNumber int: Number of item to write. 1-based.
        :param timestepIndex int: Index of time step to write. 0-based.Værso
        :param time float: Time relative to start of file, in unit specified in time axis
        :param data numpy.ndarray: Data to write to file
        """
        self.__CheckIfOpen();
        if (self.fpState == DfsFilePointerState.CreatingItems 
            and itemNumber != 1 
            and timestepIndex != 0):
            raise Exception("No dynamic items have been written to the file yet (file is being created).");

        itemInfoCount = len(self.ItemInfo);

        if (itemInfoCount == 0): 
            raise Exception("File has no dynamic items.");

        # Check item number and timestep index ranges
        if (itemNumber <= 0 or itemNumber > itemInfoCount):
            raise Exception("itemNumber must be within [1,NumberOfItems].");
        if (timestepIndex < 0 or timestepIndex > self.FileInfo.TimeAxis.NumberOfTimeSteps):
            raise Exception("timestepIndex must be within [0," + (self.FileInfo.TimeAxis.NumberOfTimeSteps - 1) + "].");

        # More elaborate action is required, when appending to file. If appending then
        # (itemNumber == _fpItemNumber && timestepIndex == _fileInfo.TimeAxis.NumberOfTimeSteps == _fpTimeStepIndex)
        if (timestepIndex == self.FileInfo.TimeAxis.NumberOfTimeSteps):
            if (timestepIndex == self.fpTimeStepIndex 
                and itemNumber != self.fpItemNumber  
                or timestepIndex != self.fpTimeStepIndex 
                and itemNumber != 1):
                raise IndexError("Wrong item number while trying to append item data to file. Item data must be appended in order, and for all items in the time step");

        # Position file pointer
        self.__FpFindItemTimeStep(itemNumber, timestepIndex);

        self.WriteItemTimeStepNext(time, data);

    def WriteItemTimeStepNext(self, time, data):
        """
        Writes the next dynamic item-timestep. 

        If the file pointer points to the end of the file, this will append
        a new item-timestep to the file. If the file pointer points to an
        existing item-timestep, the data of that item-timestep is updated.

        Remember that the file pointer position depends on the mode that the file
        was opened: In edit mode the file pointer points at the first item-timestep.
        In append mode the file pointer points initially at the end of file. 

        It iterates over the item-timesteps as the ReadItemTimeStepNext, 
        see there for more details.

        This is the most efficient way to iterate through and update/append the items and 
        timesteps in a file, since it iterates exactly as the data is stored on the disk.

        The size of the data must match the data size of the item that is to be written.

        The time value is only relevant for files with non-equidistant time axis.
        For files with an equidistant time axis, the time value is ignored, and a zero can be used.

        :param time float: Time relative to start of file, in unit specified in time axis
        :param data numpy.ndarray: Data to write to file
        """
        self.__CheckIfOpen();
        if (len(self.ItemInfo) == 0):
           raise Exception("File has no dynamic items.");

        if (self.fpState == DfsFilePointerState.CreatingItems):
            # The file is being created, we are writing the first item, first timestep
            self.fpState = DfsFilePointerState.DynamicItem;
            self.fpItemNumber = 1;
            self.fpTimeStepIndex = 0;
        if (self.fpState != DfsFilePointerState.DynamicItem):
            # Position file pointer at first timestep and first item.
            self.__FpFindBlockDynamic();

        dynamicItem = self.ItemInfo[self.fpItemNumber - 1];

        # data.Length can be larger than the number of elements.
        if (dynamicItem.ElementCount > data.size):
            raise Exception(
                "Data is of wrong size. Item has {} elements, data is {} long.".format(dynamicItem.ElementCount,data.Length));

        if   (dynamicItem.DataType == DfsSimpleType.Float  and data.dtype != np.float32):
            raise Exception("Expecting float data, got " + str(data.dtype))
        elif (dynamicItem.DataType == DfsSimpleType.Double and data.dtype != np.float64):
            raise Exception("Expecting double data, got " + str(data.dtype))
        elif (dynamicItem.DataType == DfsSimpleType.Byte   and data.dtype != np.int8):
            raise Exception("Expecting byte (int8) data, got " + str(data.dtype))
        elif (dynamicItem.DataType == DfsSimpleType.Int    and data.dtype != np.int32):
            raise Exception("Expecting int32 data, got " + str(data.dtype))
        elif (dynamicItem.DataType == DfsSimpleType.UInt   and data.dtype != np.uint32):
            raise Exception("Expecting uint32 data, got " + str(data.dtype))
        elif (dynamicItem.DataType == DfsSimpleType.Short  and data.dtype != np.int16):
            raise Exception("Expecting int16 data, got " + str(data.dtype))
        elif (dynamicItem.DataType == DfsSimpleType.UShort and data.dtype != np.uint16):
            raise Exception("Expecting uint16 data, got " + str(data.dtype))

        DfsDLL.Wrapper.dfsWriteItemTimeStep(self.headPointer, self.filePointer, ctypes.c_double(time), data.ctypes.data);

        if (self.__FpDynamicIncrement()):
            if (self.fpTimeStepIndex > self.FileInfo.TimeAxis.NumberOfTimeSteps):
                # One entire time step (all items) has just been written to file, 
                # increment the number of time steps
                self.FileInfo.TimeAxis.IncrementNumberOfTimeSteps(time);

    def Reset(self):
        """
        Resets the file pointer to point on the first dynamic item time step in the file.

        Can also be used if it is required to restart reading the static items.

        """
        self.__CheckIfOpen()
        self.__FpFindItemTimeStep(1, 0)

    def FindItem(self, itemNumber, timestepIndex):
        """
        Positions the file pointer at the location in the file where the 
        specified dynamic item at the specified time step starts.

        :param itemNumber: Number of item to find (1-based)
        :param timestepIndex: Index of time step to find (0-based)
        """
        self.__CheckIfOpen()
        self.__FpFindItemTimeStep(itemNumber, timestepIndex)

    def FindTimeStep(self, timestepIndex):
        """
        Positions the file pointer at the location in the file where the 
        specified time step starts.
        :param timestepIndex: Index of time step to find (0-based)
        """
        self.__CheckIfOpen()
        self.__FpFindTimeStep(timestepIndex)

    def Flush(self):
        """
        Flush cached data to the file. This will especially update the header information, 
        such that if another process is reading the file while it is being read, the new
        header information can be retrieved.
        """
        self.__CheckIfOpen()
        DfsDLL.Wrapper.dfsFileFlush(self.headPointer, self.filePointer)

    def FlushTimeStep(self):
        """
        Flush cached data to the file. This will update the time part of the header information, 
        but not other parts of the header. 

        Compared to the `Flush` method; the `Flush` will update
        statistics of all items (if enabled) and all modifications to the header data.
        This method will only update the time part. The `Flush` method can
        be an expensive operations especially for files with many dynamic items. This
        method is independent of the file at hand.
        """
        self.__CheckIfOpen()
        DfsDLL.Wrapper.dfsFileFlushTimeStep(self.headPointer, self.filePointer)

    def CreateEmptyItemData(self, item, reshape = False):
        """Create an empty DfsItemData object with the size matching the item.

        :param item Union[DfsDynamicItem,int]: Dynamic item to create item data for. The int version is the item number, 1-based.
        :returns DfsItemData: an empty item data object of the correct size
        """
        if (isinstance(item, int)):
            item = self.ItemInfo[item-1]
        return item.CreateEmptyItemData(reshape)


    def ReadDfs0DataDouble(self, itemsToLoad=None):
        """
        Bulk read the times and data for a dfs0 file, putting it all in
        a matrix structure.

        First column in the result are the times, then a column for each
        item in the file to load. There are as many rows as there are timesteps.
        All item data are converted to doubles.

        :param itemsToLoad: npArray of item numbers (1-based, integers) to store in data array. Can be null to store all items.
        """

        self.__CheckIfOpen();

        # Size of matrix is numTimeSteps x (numItems + 1)
        numItems = len(self.ItemInfo)
        numTimeSteps = self.FileInfo.TimeAxis.NumberOfTimeSteps
        if (itemsToLoad is None):
            numItemsToLoad = numItems
        elif (type(itemsToLoad) is list):
            itemsToLoad = np.array(itemsToLoad, dtype=np.int32)
            numItemsToLoad = len(itemsToLoad)
        else:
            numItemsToLoad = len(itemsToLoad)

        npSize = (numItemsToLoad+1) * numTimeSteps;

        if os.name == 'nt':
            data = np.zeros(npSize, dtype=np.float64)
            if (itemsToLoad is None):
                success = DfsDLL.MCCUWrapper.ReadDfs0DataDouble(
                    self.headPointer, self.filePointer, data.ctypes.data
                )
            else:
                success = DfsDLL.MCCUWrapper.ReadDfs0ItemsDouble(
                    self.headPointer, self.filePointer, data.ctypes.data, itemsToLoad.ctypes.data, numItemsToLoad
                )
            if success != 0:
                return None
            
            data = data.reshape( (numTimeSteps, numItemsToLoad + 1))
        else:
            data = np.zeros(shape=(numTimeSteps, numItemsToLoad + 1), dtype=np.float64)

            # Preload a set of item data
            if itemsToLoad is None:
                itemsToLoad = list(range(numItems))
            itemDatas = []
            for j in itemsToLoad:
                itemDatas.append(self.CreateEmptyItemData(j + 1))

            self.Reset()

            for i in range(numTimeSteps):
                for j in range(numItemsToLoad):
                    itemData = itemDatas[j]
                    self.ReadItemTimeStep(itemData, i)
                    if j == 0:
                        data[i, 0] = itemData.Time

                    data[i, j + 1] = itemData.Data[0]            

        return data

    def WriteDfs0DataDouble(self, data):
        """
        Bulk write the times and data for a dfs0 file, loading it all data from a matrix structure.

        First column in the result are the times, then a column for each
        item in the file. There are as many rows as there are timesteps.
        All item data are converted to doubles.
        """

        self.__CheckIfOpen();

        # Size of matrix is numTimeSteps x (numItems + 1)
        numItems = len(self.ItemInfo)
        numTimeSteps = data.shape[0]
        
        if data.shape[1] != numItems+1:
            raise Exception("Number of items in file does not match number of items in data")
        if data.dtype != np.float64:
            raise Exception("Type of input data is incorrect. Must be float(64), but is: " + str(data.dtype))
        
        if os.name == 'nt':
            data = np.require(data, requirements=['C'])
            success = DfsDLL.MCCUWrapper.WriteDfs0DataDouble(
                self.headPointer, self.filePointer, data.ctypes.data, numTimeSteps
            )
        else:
            isFloatItem = []
            for j in range(numItems):
                isFloatItem.append(self.ItemInfo[j].DataType == DfsSimpleType.Float)

            fdata = np.array([0], np.float32)
            ddata = np.array([0], np.float64)

            for i in range(numTimeSteps):
                time = data[i,0];
                for j in range(numItems):
                    if isFloatItem[j]:
                        fdata[0] = data[i, j+1]
                        self.WriteItemTimeStepNext(time, fdata)
                    else:
                        ddata[0] = data[i, j+1]
                        self.WriteItemTimeStepNext(time, ddata)
            
            success = 0 # consistent with DfsDLL

        return success


    def __CheckIfOpen(self):
        if self.filePointer.value == None:
            raise IOError("File is closed")

    def __FpFindBlockDynamic(self):
        DfsDLL.Wrapper.dfsFindBlockDynamic(self.headPointer, self.filePointer)
        self.fpState = DfsFilePointerState.DynamicItem
        self.fpItemNumber = 1
        self.fpTimeStepIndex = 0

    def __FpFindItemTimeStep(self, itemNumber: int, timestepIndex: int):
        # If itemNumber is first item, search for time step instead
        if itemNumber == 1:
            self.__FpFindTimeStep(timestepIndex)

        # Position the file pointer at the dynamic item
        if (
            self.fpState != DfsFilePointerState.DynamicItem
            or self.fpItemNumber != itemNumber
            or self.fpTimeStepIndex != timestepIndex
        ):
            DfsDLL.Wrapper.dfsFindItemDynamic(
                self.headPointer, self.filePointer, int(timestepIndex), itemNumber
            )
            self.fpState = DfsFilePointerState.DynamicItem
            self.fpItemNumber = itemNumber
            self.fpTimeStepIndex = timestepIndex

    def __FpFindTimeStep(self, timestepIndex: int):
        # Position the file pointer at the dynamic item
        if (
            self.fpState != DfsFilePointerState.DynamicItem
            or self.fpItemNumber != 1
            or self.fpTimeStepIndex != timestepIndex
        ):
            DfsDLL.Wrapper.dfsFindTimeStep(
                self.headPointer, self.filePointer, int(timestepIndex)
            )
            self.fpState = DfsFilePointerState.DynamicItem
            self.fpItemNumber = 1
            self.fpTimeStepIndex = timestepIndex

    def __FpDynamicIncrement(self):
        self.fpItemNumber += 1
        if self.fpItemNumber > len(self.ItemInfo):
            self.fpTimeStepIndex += 1
            self.fpItemNumber = 1
            return True
        return False

    def __DynamicItemInfoReadAndCreate(self, itemNumber, noOfItems):
        if itemNumber < 1 or itemNumber > noOfItems:
            raise ValueError("Item number must be in the range of 1 - {}".format(noOfItems))
        itemPointer = ctypes.c_void_p(
            DfsDLL.Wrapper.dfsItemD(self.headPointer, itemNumber)
        )
        item = DfsDynamicItemInfo(itemPointer, itemNumber)
        self.__GetItemInfo(item)
        return item

    def __StaticItemReadAndCreate(self, number, ubgConversion):

        # Check if we can read it. staticVectorPointer contains both item info and data
        fioError = ctypes.c_int32()
        staticVectorPointer = DfsDLL.Wrapper.dfsStaticRead(self.filePointer, ctypes.byref(fioError));
        DfsDLL.CheckReturnCode(fioError.value);

        if (staticVectorPointer == None):
            return (None);

        # Get pointer to static item info
        staticItemPointer = ctypes.c_void_p(DfsDLL.Wrapper.dfsItemS(staticVectorPointer))

        staticItem = DfsStaticItem(self, staticVectorPointer, staticItemPointer, number);
        staticItem.DfsFile = self;
        staticItem.StaticVectorPointer = staticVectorPointer;

        # The header pointer is not automatically set in the static item, so do that here.
        # Otherwise unit conversion of static item info (spatial axis) will fail (in ufs.dll
        # a delete value from header (pdfs) is required for dfsGet/SetItemAxisXXX).
        DfsDLL.Wrapper.dfsStaticSetHeader(self.headPointer, staticItem.ItemPointer);
        
        # if (ubgConversion):
        #     staticItem.SetUnitConversion(UnitConversionType.UbgConversion, default(eumUnit));
        #     staticItem.SetAxisUnitConversion(UnitConversionType.UbgConversion, default(eumUnit));

        self.__GetItemInfo(staticItem)
        self.__GetStaticData(staticItem)

        return (staticItem)

    def __GetItemInfo(self, item):
        eumItemIntP = ctypes.c_int32()
        eumItemDescP = ctypes.c_char_p()
        itemNameP = ctypes.c_char_p()
        eumUnitIntP = ctypes.c_int32()
        eumUnitDescP = ctypes.c_char_p()
        itemDataTypeP = ctypes.c_int()

        # DfsDLL.Wrapper.dfsGetItemInfo_(itemPointer, ctypes.byref(eumItemIntP), ctypes.byref(itemNameP), ctypes.byref(eumUnitDescP), ctypes.byref(itemDataTypeP));
        DfsDLL.Wrapper.dfsGetItemInfo(
            item.ItemPointer,
            ctypes.byref(eumItemIntP),
            ctypes.byref(eumItemDescP),
            ctypes.byref(itemNameP),
            ctypes.byref(eumUnitIntP),
            ctypes.byref(eumUnitDescP),
            ctypes.byref(itemDataTypeP),
        )
        eumItemDesc = eumItemDescP.value.decode("ascii")
        eumUnitDesc = eumUnitDescP.value.decode("ascii")
        itemName = itemNameP.value.decode("cp1252", "replace")
        itemDataType = DfsSimpleType(itemDataTypeP.value)

        quantity = eumQuantity(eumItem(eumItemIntP.value), eumUnit(eumUnitIntP.value))
        quantity.ItemDescription = eumItemDesc
        quantity.UnitDescription = eumUnitDesc

        item.init(itemName, quantity)
        item.DataType = itemDataType
        item.ValueType = DfsDLLUtil.dfsGetItemValueType(item.ItemPointer)
        item.ElementCount = DfsDLL.Wrapper.dfsGetItemElements(item.ItemPointer)
        item.SpatialAxis = DfsDLLUtil.GetItemSpatialAxis(item.ItemPointer)


    def __GetStaticData(self, item):
        data = item.CreateEmptyItemDataData();
        DfsDLL.Wrapper.dfsStaticGetData(item.StaticVectorPointer, data.ctypes.data);
        item.Data = data;


class DfsDLLUtil():
    """Utilities class, creating various Dfs classes based on pointers to DFS native data"""

    @staticmethod
    def GetDfsType(arrayData):
        if   (arrayData.dtype == np.float32):
            datatype = DfsSimpleType.Float
        elif (arrayData.dtype == np.float64):
            datatype = DfsSimpleType.Double
        elif (arrayData.dtype == np.int32):
            datatype = DfsSimpleType.Int
        elif (arrayData.dtype == np.uint32):
            datatype = DfsSimpleType.UInt
        elif (arrayData.dtype == np.int16):
            datatype = DfsSimpleType.Short
        elif (arrayData.dtype == np.uint16):
            datatype = DfsSimpleType.UShort
        elif (arrayData.dtype == np.int8):
            datatype = DfsSimpleType.Byte
        else:
            raise Exception("Data type not supported: {0}".format(arrayData.dtype))
        return datatype

    @staticmethod
    def GetProjection(headerPointer):
        type = ProjectionType(DfsDLL.Wrapper.dfsGetGeoInfoType(headerPointer));
        if (type == ProjectionType.Projection):
            wktString = ctypes.c_char_p();
            lon0 = ctypes.c_double();
            lat0 = ctypes.c_double();
            orientation = ctypes.c_double();
            DfsDLL.Wrapper.dfsGetGeoInfoUTMProj(
                headerPointer, 
                ctypes.byref(wktString), 
                ctypes.byref(lon0), 
                ctypes.byref(lat0), 
                ctypes.byref(orientation));
            projection = DfsProjection(
                type, 
                wktString.value.decode("ascii"), 
                lon0.value, 
                lat0.value, 
                orientation.value);
        else:
            projection = DfsProjection(type, "", 0, 0, 0);

        return projection

    @staticmethod
    def GetTemporalAxis(headPointer):
        timeAxisType = TimeAxisType(DfsDLL.Wrapper.dfsGetTimeAxisType(headPointer))

        if timeAxisType is TimeAxisType.Undefined:
            pass
        elif timeAxisType is TimeAxisType.TimeEquidistant:
            eumTimeUnitInt = ctypes.c_int()
            eumTimeUnitDescr = ctypes.c_char_p()
            starttime = ctypes.c_double()
            timestep = ctypes.c_double()
            numTimeSteps = ctypes.c_int32()
            firstIndex = ctypes.c_int32()
            DfsDLL.Wrapper.dfsGetEqTimeAxis(
                headPointer,
                ctypes.byref(eumTimeUnitInt),
                ctypes.byref(eumTimeUnitDescr),
                ctypes.byref(starttime),
                ctypes.byref(timestep),
                ctypes.byref(numTimeSteps),
                ctypes.byref(firstIndex),
            )

            res = DfsEqTimeAxis(
                eumUnit(eumTimeUnitInt.value),
                starttime.value,
                timestep.value,
                numTimeSteps.value,
                firstIndex.value,
            )
            return res
        elif timeAxisType is TimeAxisType.TimeNonEquidistant:
            eumTimeUnitInt = ctypes.c_int()
            eumTimeUnitDescr = ctypes.c_char_p()
            starttime = ctypes.c_double()
            timeSpan = ctypes.c_double()
            numTimeSteps = ctypes.c_int32()
            firstIndex = ctypes.c_int32()
            DfsDLL.Wrapper.dfsGetNeqTimeAxis(
                headPointer,
                ctypes.byref(eumTimeUnitInt),
                ctypes.byref(eumTimeUnitDescr),
                ctypes.byref(starttime),
                ctypes.byref(timeSpan),
                ctypes.byref(numTimeSteps),
                ctypes.byref(firstIndex),
            )

            res = DfsNonEqTimeAxis(
                eumUnit(eumTimeUnitInt.value),
                starttime.value,
                numTimeSteps.value,
                timeSpan.value,
                firstIndex.value,
            )
            return res
        elif timeAxisType is TimeAxisType.CalendarEquidistant:
            startDateStr     = ctypes.c_char_p()
            startTimeStr     = ctypes.c_char_p()
            eumTimeUnitInt   = ctypes.c_int()
            eumTimeUnitDescr = ctypes.c_char_p()
            starttime        = ctypes.c_double()
            timestep         = ctypes.c_double()
            numTimeSteps     = ctypes.c_int32()
            firstIndex       = ctypes.c_int32()

            DfsDLL.Wrapper.dfsGetEqCalendarAxis(
                headPointer,
                ctypes.byref(startDateStr),
                ctypes.byref(startTimeStr),
                ctypes.byref(eumTimeUnitInt),
                ctypes.byref(eumTimeUnitDescr),
                ctypes.byref(starttime),
                ctypes.byref(timestep),
                ctypes.byref(numTimeSteps),
                ctypes.byref(firstIndex),
            )
            dateStr = startDateStr.value.decode("ascii")
            timeStr = startTimeStr.value.decode("ascii")
            # startDateTime = datetime.fromisoformat("{dateStr}T{timeStr}".format(dateStr,timeStr));
            startDateTime = datetime.datetime.strptime(
                "{} {}".format(dateStr,timeStr), "%Y-%m-%d %H:%M:%S"
            )
            res = DfsEqCalendarAxis(
                eumUnit(eumTimeUnitInt.value),
                startDateTime,
                starttime.value,
                timestep.value,
                numTimeSteps.value,
                firstIndex.value,
            )
            return res

        elif timeAxisType is TimeAxisType.CalendarNonEquidistant:
            startDateStr = ctypes.c_char_p()
            startTimeStr = ctypes.c_char_p()
            eumTimeUnitInt = ctypes.c_int()
            eumTimeUnitDescr = ctypes.c_char_p()
            startTimeOffset = ctypes.c_double()
            timeSpan = ctypes.c_double()
            numTimeSteps = ctypes.c_int32()
            firstIndex = ctypes.c_int32()
            DfsDLL.Wrapper.dfsGetNeqCalendarAxis(
                headPointer,
                ctypes.byref(startDateStr),
                ctypes.byref(startTimeStr),
                ctypes.byref(eumTimeUnitInt),
                ctypes.byref(eumTimeUnitDescr),
                ctypes.byref(startTimeOffset),
                ctypes.byref(timeSpan),
                ctypes.byref(numTimeSteps),
                ctypes.byref(firstIndex),
            )

            dateStr = startDateStr.value.decode("ascii")
            timeStr = startTimeStr.value.decode("ascii")
            # startDateTime = datetime.fromisoformat("{}T{}".format(dateStr,timeStr));
            startDateTime = datetime.datetime.strptime(
                "{} {}".format(dateStr,timeStr), "%Y-%m-%d %H:%M:%S"
            )
            res = DfsNonEqCalendarAxis(
                eumUnit(eumTimeUnitInt.value),
                startDateTime,
                startTimeOffset.value,
                timeSpan.value,
                numTimeSteps.value,
                firstIndex.value,
            )
            return res

    @staticmethod
    def GetItemSpatialAxis(itemPointer):
        axisType = SpaceAxisType(DfsDLL.Wrapper.dfsGetItemAxisType(itemPointer));

        if axisType == SpaceAxisType.Undefined:
            raise Exception("Undefined spatial axis, invalid file format");

        if axisType == SpaceAxisType.EqD0:
            eumUnitInt = ctypes.c_int32()
            eumUnitDescr = ctypes.c_char_p()
            DfsDLL.Wrapper.dfsGetItemAxisEqD0(itemPointer, ctypes.byref(eumUnitInt), ctypes.byref(eumUnitDescr))
            axis = DfsAxisEqD0(eumUnit(eumUnitInt.value))
            return (axis)

        if axisType == SpaceAxisType.EqD1:
            eumUnitInt = ctypes.c_int32()
            eumUnitDescr = ctypes.c_char_p()
            xCount = ctypes.c_int32()
            x0 = ctypes.c_float()
            dx = ctypes.c_float()
            DfsDLL.Wrapper.dfsGetItemAxisEqD1(
                itemPointer, 
                ctypes.byref(eumUnitInt), 
                ctypes.byref(eumUnitDescr), 
                ctypes.byref(xCount),
                ctypes.byref(x0), 
                ctypes.byref(dx))
            axis = DfsAxisEqD1(eumUnit(eumUnitInt.value), xCount.value, x0.value, dx.value)
            return (axis)

        if axisType == SpaceAxisType.NeqD1:
            raise NotSupportedException();

        if axisType == SpaceAxisType.EqD2:
            eumUnitInt = ctypes.c_int32()
            eumUnitDescr = ctypes.c_char_p()
            xCount = ctypes.c_int32()
            x0 = ctypes.c_float()
            dx = ctypes.c_float()
            yCount = ctypes.c_int32()
            y0 = ctypes.c_float()
            dy = ctypes.c_float()
            DfsDLL.Wrapper.dfsGetItemAxisEqD2(
                itemPointer, 
                ctypes.byref(eumUnitInt), 
                ctypes.byref(eumUnitDescr), 
                ctypes.byref(xCount), 
                ctypes.byref(yCount), 
                ctypes.byref(x0), 
                ctypes.byref(y0), 
                ctypes.byref(dx), 
                ctypes.byref(dy))
            axis = DfsAxisEqD2(eumUnit(eumUnitInt.value), xCount.value, x0.value, dx.value, yCount.value, y0.value, dy.value)
            return (axis)

        if axisType == SpaceAxisType.NeqD2:
            raise NotSupportedException();

        if axisType == SpaceAxisType.EqD3:
            eumUnitInt = ctypes.c_int32()
            eumUnitDescr = ctypes.c_char_p()
            xCount = ctypes.c_int32()
            x0 = ctypes.c_float()
            dx = ctypes.c_float()
            yCount = ctypes.c_int32()
            y0 = ctypes.c_float()
            dy = ctypes.c_float()
            zCount = ctypes.c_int32()
            z0 = ctypes.c_float()
            dz = ctypes.c_float()
            DfsDLL.Wrapper.dfsGetItemAxisEqD3(
                itemPointer, 
                ctypes.byref(eumUnitInt), 
                ctypes.byref(eumUnitDescr), 
                ctypes.byref(xCount), 
                ctypes.byref(yCount), 
                ctypes.byref(zCount), 
                ctypes.byref(x0), 
                ctypes.byref(y0), 
                ctypes.byref(z0), 
                ctypes.byref(dx), 
                ctypes.byref(dy),
                ctypes.byref(dz),
                )
            axis = DfsAxisEqD3(eumUnit(eumUnitInt.value), xCount.value, x0.value, dx.value, yCount.value, y0.value, dy.value, zCount.value, z0.value, dz.value)
            return axis

        if axisType == SpaceAxisType.NeqD3:
            raise NotSupportedException();

        #if axisType == SpaceAxisType.EqD4:
        #    raise NotSupportedException();

        if axisType == SpaceAxisType.CurveLinearD2:
            raise NotSupportedException();

        if axisType == SpaceAxisType.CurveLinearD3:
            raise NotSupportedException();

        #if (   axisType == SpaceAxisType.TvarD1
        #    or axisType == SpaceAxisType.TvarD2
        #    or axisType == SpaceAxisType.TvarD3):
        #    raise NotSupportedException();

        return None

    @staticmethod
    def dfsSetItemSpatialAxis(itemPointer, spatialAxis):
        axis = spatialAxis
        if   spatialAxis.AxisType is SpaceAxisType.Undefined:
            raise Exception("Axis can not be undefined");
        elif spatialAxis.AxisType is SpaceAxisType.EqD0:
            rok = DfsDLL.Wrapper.dfsSetItemAxisEqD0(itemPointer, ctypes.c_int32(axis.AxisUnit.value));
            DfsDLL.CheckReturnCode(rok);
            return
        elif spatialAxis.AxisType is SpaceAxisType.EqD1:
            rok = DfsDLL.Wrapper.dfsSetItemAxisEqD1(
                itemPointer, ctypes.c_int32(axis.AxisUnit.value), 
                ctypes.c_int32(axis.XCount), ctypes.c_float(axis.X0), ctypes.c_float(axis.Dx));
            DfsDLL.CheckReturnCode(rok);
            return
        #elif spatialAxis.AxisType is SpaceAxisType.NeqD1:
        #    rok = DfsDLL.Wrapper.dfsSetItemAxisNeqD1(itemPointer, ctypes.c_int32(axis.AxisUnit.values), axis.Coordinates.Length, axis.Coordinates, true);
        #    DfsDLL.CheckReturnCode(rok);
        elif spatialAxis.AxisType is SpaceAxisType.EqD2:
            rok = DfsDLL.Wrapper.dfsSetItemAxisEqD2(
                itemPointer, ctypes.c_int32(axis.AxisUnit.value),
                ctypes.c_int32(axis.XCount), ctypes.c_int32(axis.YCount),
                ctypes.c_float(axis.X0), ctypes.c_float(axis.Y0),
                ctypes.c_float(axis.Dx), ctypes.c_float(axis.Dy));
            DfsDLL.CheckReturnCode(rok);
            return
        #elif spatialAxis.AxisType is SpaceAxisType.NeqD2:
        #    DfsDLL.Wrapper.dfsSetItemAxisNeqD2(itemPointer, ctypes.c_int32(axis.AxisUnit.value),
        #                                     axis.XCoordinates.Length-1, axis.YCoordinates.Length-1,
        #                                     axis.XCoordinates, axis.YCoordinates, true);
        #    DfsDLL.CheckReturnCode(rok);
        elif spatialAxis.AxisType is SpaceAxisType.EqD3:
            rok = DfsDLL.Wrapper.dfsSetItemAxisEqD3(
                itemPointer, ctypes.c_int32(axis.AxisUnit.value),
                ctypes.c_int32(axis.XCount), ctypes.c_int32(axis.YCount), axis.ZCount,
                ctypes.c_float(axis.X0), ctypes.c_float(axis.Y0), ctypes.c_float(axis.Z0),
                ctypes.c_float(axis.Dx), ctypes.c_float(axis.Dy), ctypes.c_float(axis.Dz));
            DfsDLL.CheckReturnCode(rok);
        #elif spatialAxis.AxisType is SpaceAxisType.NeqD3:
        #    rok = DfsDLL.Wrapper.dfsSetItemAxisNeqD3(itemPointer, ctypes.c_int32(axis.AxisUnit.value),
        #                                     axis.XCoordinates.Length - 1, axis.YCoordinates.Length - 1, axis.ZCoordinates.Length - 1,
        #                                     axis.XCoordinates, axis.YCoordinates, axis.ZCoordinates, true);
        #    DfsDLL.CheckReturnCode(rok);
        #elif spatialAxis.AxisType is SpaceAxisType.EqD4:
        #    rok = DfsDLL.Wrapper.dfsSetItemAxisEqD4(
        #        itemPointer, ctypes.c_int32(axis.AxisUnit.value),
        #        ctypes.c_int32(axis.XCount), ctypes.c_int32(axis.YCount), ctypes.c_int32(axis.ZCount), ctypes.c_int32(axis.FCount),
        #        ctypes.c_float(axis.X0), ctypes.c_float(axis.Y0), ctypes.c_float(axis.Z0), ctypes.c_float(axis.F0),
        #        ctypes.c_float(axis.Dx), ctypes.c_float(axis.Dy), ctypes.c_float(axis.Dz), ctypes.c_float(axis.Df));
        #    DfsDLL.CheckReturnCode(rok);
        #elif spatialAxis.AxisType is SpaceAxisType.CurveLinearD2:
        #    rok = DfsDLL.Wrapper.dfsSetItemAxisCurveLinearD2(itemPointer, (int) axis.AxisUnit.value,
        #                                              ctypes.c_int32(axis.XCount), ctypes.c_int32(axis.YCount),
        #                                              axis.XCoordinates, axis.YCoordinates, 
        #                                              true);
        #    DfsDLL.CheckReturnCode(rok);
        #elif spatialAxis.AxisType is SpaceAxisType.CurveLinearD3:
        #    rok = DfsDLL.Wrapper.dfsSetItemAxisCurveLinearD3(itemPointer, (int) axis.AxisUnit.value,
        #                                              ctypes.c_int32(axis.XCount), ctypes.c_int32(axis.YCount), axis.ZCount,
        #                                              axis.XCoordinates, axis.YCoordinates, axis.ZCoordinates, 
        #                                              true);
        #    DfsDLL.CheckReturnCode(rok);
        #elif (   spatialAxis.AxisType is SpaceAxisType.TvarD1
        #      or spatialAxis.AxisType is SpaceAxisType.TvarD2
        #      or spatialAxis.AxisType is SpaceAxisType.TvarD3):
        #    raise Exception("Not supported: Axis type: " + spatialAxis.AxisType);



    @staticmethod
    def BuildCustomBlocks(headPointer):
        customBlockP = ctypes.c_void_p();
        rok = DfsDLL.Wrapper.dfsGetCustomBlockRef(headPointer, ctypes.byref(customBlockP))
        DfsDLL.CheckReturnCode(rok);
        customBlocks = []
        while (customBlockP.value != None):
            customBlockP, dfsCustomBlock = DfsDLLUtil.__CustomBlockRead(customBlockP)
            customBlocks.append(dfsCustomBlock)
        return (customBlocks);

    @staticmethod
    def dfsAddCustomBlock(headerPointer, customBlock):
        values = customBlock.Values
        rok = DfsDLL.Wrapper.dfsAddCustomBlock(
            headerPointer, 
            ctypes.c_int32(customBlock.SimpleType.value), 
            ctypes.c_char_p(customBlock.Name.encode("ascii")), 
            ctypes.c_int32(values.size), 
            values.ctypes.data);
        DfsDLL.CheckReturnCode(rok);

    @staticmethod
    def __CustomBlockRead(customBlockPointer):
        name = ctypes.c_char_p();
        size = ctypes.c_int32();
        customBlockDataPointer = ctypes.c_void_p();
        dataTypeP = ctypes.c_int32();
        DfsDLL.Wrapper.dfsGetCustomBlock(
            customBlockPointer, 
            ctypes.byref(dataTypeP), 
            ctypes.byref(name),
            ctypes.byref(size), 
            ctypes.byref(customBlockDataPointer),
            ctypes.byref(customBlockPointer))

        size = size.value
        dataType = DfsSimpleType(dataTypeP.value)
        data = None

        if   dataType is DfsSimpleType.Float:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_float))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))

        elif dataType is DfsSimpleType.Double:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_double))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))

        elif dataType is DfsSimpleType.Byte:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_byte))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))

        elif dataType is DfsSimpleType.Int:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_int32))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))

        elif dataType is DfsSimpleType.UInt:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_uint32))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))

        elif dataType is DfsSimpleType.Short:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_uint16))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))

        elif dataType is DfsSimpleType.UShort:
            datap = ctypes.cast(customBlockDataPointer, ctypes.POINTER(ctypes.c_uint16))
            # wrap numpy array around C array
            data  = np.ctypeslib.as_array(datap,shape=(size,))


        customBlock = DfsCustomBlock(
            name.value.decode("ascii"),
            DfsSimpleType(dataType.value),
            data)

        return customBlockPointer, customBlock

    @staticmethod
    def dfsSetTemporalAxis(headerPointer, temporalAxis: DfsTemporalAxis):
        if temporalAxis.TimeAxisType is TimeAxisType.Undefined:
            raise Exception("Temporal axis can not be undefined");
        if temporalAxis.TimeAxisType is TimeAxisType.TimeEquidistant:
            rok = DfsDLL.Wrapper.dfsSetEqTimeAxis(
                headerPointer, 
                ctypes.c_int32(temporalAxis.TimeUnit.value), 
                ctypes.c_double(temporalAxis.StartTimeOffset), 
                ctypes.c_double(temporalAxis.TimeStep), 
                ctypes.c_int32(temporalAxis.FirstTimeStepIndex))
            DfsDLL.CheckReturnCode(rok)
        elif temporalAxis.TimeAxisType is TimeAxisType.TimeNonEquidistant:
            rok = DfsDLL.Wrapper.dfsSetNeqTimeAxis(
                headerPointer, 
                ctypes.c_int32(temporalAxis.TimeUnit.value), 
                ctypes.c_double(temporalAxis.StartTimeOffset), 
                ctypes.c_int32(temporalAxis.FirstTimeStepIndex))
            DfsDLL.CheckReturnCode(rok)
        elif temporalAxis.TimeAxisType is TimeAxisType.CalendarEquidistant:
            dateStr, timeStr = DfsDLLUtil.ToDfsDateStrings(temporalAxis.StartDateTime)
            rok = DfsDLL.Wrapper.dfsSetEqCalendarAxis(
                headerPointer, 
                ctypes.c_char_p(dateStr.encode("ascii")), 
                ctypes.c_char_p(timeStr.encode("ascii")), 
                ctypes.c_int32(temporalAxis.TimeUnit.value), 
                ctypes.c_double(temporalAxis.StartTimeOffset), 
                ctypes.c_double(temporalAxis.TimeStep), 
                ctypes.c_int32(temporalAxis.FirstTimeStepIndex))
            DfsDLL.CheckReturnCode(rok)
        elif temporalAxis.TimeAxisType is TimeAxisType.CalendarNonEquidistant:
            dateStr, timeStr = DfsDLLUtil.ToDfsDateStrings(temporalAxis.StartDateTime)
            rok = DfsDLL.Wrapper.dfsSetNeqCalendarAxis(
                headerPointer, 
                ctypes.c_char_p(dateStr.encode("ascii")), 
                ctypes.c_char_p(timeStr.encode("ascii")), 
                ctypes.c_int32(temporalAxis.TimeUnit.value), 
                ctypes.c_double(temporalAxis.StartTimeOffset), 
                ctypes.c_int32(temporalAxis.FirstTimeStepIndex))
            DfsDLL.CheckReturnCode(rok)


    @staticmethod
    def ToDfsDateStrings(datetime):
        date = datetime.strftime("%Y-%m-%d");
        time = datetime.strftime("%H:%M:%S")
        return date, time

    @staticmethod
    def dfsGetItemValueType(itemPointer):
        valueTypeInt = ctypes.c_int()
        err = DfsDLL.Wrapper.dfsGetItemValueType(
            itemPointer, ctypes.byref(valueTypeInt)
        )
        return DataValueType(valueTypeInt.value)
