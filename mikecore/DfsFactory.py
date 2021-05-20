from mikecore.DfsFile import *
from mikecore.DfsBuilder import *

class DfsFactory:
    def __init__(self):
        pass

    #region Builder creation factory methods

    def CreateGenericDfsBuilder(self, fileTitle, applicationTitle, applicationVersionNo):
      return (DfsBuilder.Create(fileTitle, applicationTitle, applicationVersionNo));

    #endregion

    #region Projection factory methods

    def CreateProjection(self, wktProjectionString):
      if (wktProjectionString == None or wktProjectionString == ""):
          raise Exception("Projection string can not be null or empty");
      return (DfsProjection.Create(wktProjectionString));

    def CreateProjectionGeoOrigin(self, wktProjectionString, lon0, lat0, orientation):
      return (DfsProjection.CreateWithGeoOrigin(wktProjectionString, lon0, lat0, orientation));

    def CreateProjectionUndefined(self):
        return DfsProjection(ProjectionType.Undefined, "", 0, 0, 0)

    #endregion

    #region Custom blocks factory methods

    def CreateCustomBlock(self, name, data):
        if   (data.dtype == np.float32): dataType = DfsSimpleType.Float  
        elif (data.dtype == np.float64): dataType = DfsSimpleType.Double 
        elif (data.dtype == np.int8):    dataType = DfsSimpleType.Byte   
        elif (data.dtype == np.int32):   dataType = DfsSimpleType.Int    
        elif (data.dtype == np.uint32):  dataType = DfsSimpleType.UInt   
        elif (data.dtype == np.int16):   dataType = DfsSimpleType.Short  
        elif (data.dtype == np.uint16):  dataType = DfsSimpleType.UShort 
        return DfsCustomBlock(name, dataType, data)

    #endregion

    #region Spatial axis factory methods

    def CreateAxisDummy(self, numberOfValues):
        return (DfsAxisEqD1(0, numberOfValues, 0, 1));

    def CreateAxisEqD0(self):
        return(DfsAxisEqD0());

    def CreateAxisEqD1(
        self, axisUnit, 
        xCount, x0, dx):
        return (DfsAxisEqD1(axisUnit, xCount, x0, dx))

    def CreateAxisEqD2(
        self, axisUnit, 
        xCount, x0, dx, 
        yCount, y0, dy 
        ):
        return (DfsAxisEqD2(axisUnit, xCount, x0, dx, yCount, y0, dy));

    def CreateAxisEqD3(
        self, axisUnit,
        xCount, x0, dx,
        yCount, y0, dy,
        zCount, z0, dz
        ):
        return (DfsAxisEqD3(axisUnit, xCount, x0, dx, yCount, y0, dy, zCount, z0, dz));

    def CreateAxisNeqD1(self, axisUnit, coords):
        return (DfsAxisNeqD1(axisUnit, coords));

    def CreateAxisNeqD2(self, axisUnit, xCoords, yCoords):
        return (DfsAxisNeqD2(axisUnit, xCoords, yCoords));

    def CreateAxisNeqD3(self, axisUnit, xCoords, yCoords, zCoords):
        return (DfsAxisNeqD3(axisUnit, xCoords, yCoords, zCoords));

    def CreateAxisCurveLinearD2(self, axisUnit, xCount, yCount, xCoords, yCoords):
        arrSize = (xCount + 1) * (yCount + 1);
        if (xCoords.size != arrSize):
            raise Exception("size of xCoords array does not match x,y,z-count values");
        if (yCoords.size != arrSize):
            raise Exception("size of yCoords array does not match x,y,z-count values");

        return (DfsAxisCurveLinearD2(axisUnit, xCount, yCount, xCoords, yCoords));

    @staticmethod
    def CreateAxisCurveLinearD3(axisUnit, xCount, yCount, zCount, xCoords, yCoords, zCoords):
        arrSize = (xCount + 1) * (yCount + 1) * (zCount + 1);
        if (xCoords.size != arrSize):
            raise Exception("size of xCoords array does not match x,y,z-count values");
        if (yCoords.size != arrSize):
            raise Exception("size of yCoords array does not match x,y,z-count values");
        if (zCoords.size != arrSize):
            raise Exception("size of zCoords array does not match x,y,z-count values");

        return (DfsAxisCurveLinearD3(axisUnit, xCount, yCount, zCount, xCoords, yCoords, zCoords));

    #endregion

    #region Temporal axis factory methods

    def CreateTemporalEqCalendarAxis(
        self,
        timeUnit,
        startDateTime,
        startTimeOffset,
        timeStep,
        numberOfTimeSteps = 0,
        firstTimeStepIndex = 0):
        return DfsEqCalendarAxis(
            timeUnit,
            startDateTime,
            startTimeOffset,
            timeStep,
            numberOfTimeSteps,
            firstTimeStepIndex)

    def CreateTemporalEqTimeAxis(
        self,
        timeUnit,
        startTimeOffset,
        timeStep,
        numberOfTimeSteps = 0,
        firstTimeStepIndex = 0):
        return DfsEqTimeAxis(
            timeUnit,
            startTimeOffset,
            timeStep,
            numberOfTimeSteps,
            firstTimeStepIndex)

    def CreateTemporalNonEqCalendarAxis(
        self,
        timeUnit,
        startDateTime,
        startTimeOffset = 0,
        timespan = 0,
        numberOfTimeSteps = 0,
        firstTimeStepIndex = 0):
        return DfsNonEqCalendarAxis(
            timeUnit,
            startDateTime,
            startTimeOffset,
            timespan,
            numberOfTimeSteps,
            firstTimeStepIndex)

    def CreateTemporalNonEqTimeAxis(
        self,
        timeUnit,
        startTimeOffset = 0,
        timespan = 0,
        numberOfTimeSteps = 0,
        firstTimeStepIndex = 0):
        return DfsNonEqTimeAxis(
            timeUnit,
            startTimeOffset,
            timespan,
            numberOfTimeSteps,
            firstTimeStepIndex)

    #endregion

    @staticmethod
    def CreateStaticItem(name, quantity, data):
        if (data.size == 0):
            raise Exception("data size is zero, it must have at least one element");
        staticItem = DfsStaticItem.Create(name, quantity, data)
        return (staticItem);

