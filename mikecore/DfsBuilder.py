from mikecore.DfsDLL import DfsDLL
from mikecore.DfsFile import *

class DfsBuilder():
    '''
    Builder for dfs files. 

    The builder works in two stages. The first stage all header information
    and information of the dynamic items are provided. In the second stage
    static items are added. Then a dfs file is ready, and data for the dynamic
    items can be added.

    To go from the first to the second stage by calling
    CreateFile, which will actually create a file on the disc.

    To get the final file, call GetFile. After GetFile
    has been called, no more static items can be added to the file.

    Stage 1: The following must be set during stage 1:
    SetGeographicalProjection,
    SetDataType,
    SetTemporalAxis.
    Furthermore, a number of dynamic items must be added.

    Stage 2: Any number of static items can be added. Create the item
    by using one of the AddCreateStaticItem(string,array) functions.
    To create a new static item from scratch, use  
    CreateStaticItemBuilder together with  
    AddStaticItem(dfsStaticItem).
    '''


    def __init__(self, fileTitle, applicationTitle = "MIKE Core Python", applicationVersionNo = 1):
        self.FileInfo = DfsFileInfo();
        self.FileInfo.FileTitle = fileTitle;
        self.FileInfo.ApplicationTitle = applicationTitle;
        self.FileInfo.ApplicationVersion = applicationVersionNo;
        self.SpatialAxis = None

        self.NumberOfTimeSteps = -1;
        self.FirstTime = 0;
        self.TimeSpan = -1;

        self.isSetProjection   = False
        self.isSetDataType     = False
        self.isSetTemporalAxis = False

        self.isFileCreated = False;
        self.DfsFile = None;

        self.DynamicItems = [];

        self.__SetDefaultValues();

    def __SetDefaultValues(self):
        self.FileInfo.DeleteValueByte        = DfsFile.DefaultDeleteValueByte;
        self.FileInfo.DeleteValueInt         = DfsFile.DefaultDeleteValueInt;
        self.FileInfo.DeleteValueUnsignedInt = DfsFile.DefaultDeleteValueUnsignedInt;
        self.FileInfo.DeleteValueFloat       = DfsFile.DefaultDeleteValueFloat;
        self.FileInfo.DeleteValueDouble      = DfsFile.DefaultDeleteValueDouble;


    def __CheckBuildStage1(self):
        '''Check whether the builder is in stage 1, and throws an exception if not.'''
        if (self.isFileCreated):
            if (self.DfsFile == None):
                raise Exception("File has been returned, action is not allowed");
            raise Exception("CreateFile has been called, action is not allowed");


    def __CheckBuildStage2(self):
        '''Check whether the builder is in stage 2, and throws an exception if not.'''
        if (self.DfsFile == None):
            if (self.isFileCreated):
                raise Exception("File has been returned, action is not allowed");
            raise Exception("CreateFile has not yet been called, action is not allowed");


    def SetFileTitle(self, fileTitle):
        self.__CheckBuildStage1();
        if (fileTitle == None):
            fileTitle = ""
        self.FileInfo.FileTitle = fileTitle;


    def SetApplicationTitle(self, appTitle):
        self.__CheckBuildStage1()
        if (appTitle == None):
            appTitle = "";
        self.FileInfo.ApplicationTitle = appTitle;


    def SetApplicationVersionNo(self, appVersion):
        self.__CheckBuildStage1()
        self.FileInfo.ApplicationVersion = appVersion;


    def SetItemStatisticsType(self, statType):
        self.__CheckBuildStage1()
        if (  statType is StatType.NoStat
           or statType is StatType.RegularStat):
            ...
        elif statType is StatType.LargevalStat:
            statType = StatType.RegularStat;

        self.FileInfo.StatsType = statType;


    def SetDataType(self, dataType):
        '''
        Set the data type. 

        This is a stage 1 method.

        The data type tags the file as a special dfs file type.
        There exists no global system for maintaining these tag-variables. 
        The tag-variables should only be interpreted locally within one 
        model-complex e.g. MIKE 21. The application programmer can tag 
        bathymetries, result files, input files freely. 
        '''

        self.__CheckBuildStage1()
        self.FileInfo.DataType = dataType;
        self.isSetDataType = True;

    def GetDeleteValueFloat(self):
        return self.FileInfo.DeleteValueFloat;

    def SetDeleteValueFloat(self, value):
        self.__CheckBuildStage1
        self.FileInfo.DeleteValueFloat = value;

    DeleteValueFloat = property(GetDeleteValueFloat, SetDeleteValueFloat)


    def GetDeleteValueDouble(self):
        return self.FileInfo.DeleteValueDouble;

    def SetDeleteValueDouble(self, value):
        self.__CheckBuildStage1
        self.FileInfo.DeleteValueDouble = value;

    DeleteValuedouble = property(GetDeleteValueDouble, SetDeleteValueDouble)


    def GetDeleteValueByte(self):
        return self.FileInfo.DeleteValueByte;

    def SetDeleteValueByte(self, value):
        self.__CheckBuildStage1
        self.FileInfo.DeleteValueByte = value;

    DeleteValueByte = property(GetDeleteValueByte, SetDeleteValueByte)


    def GetDeleteValueInt(self):
        return self.FileInfo.DeleteValueInt;

    def SetDeleteValueInt(self, value):
        self.__CheckBuildStage1
        self.FileInfo.DeleteValueInt = value;

    DeleteValueInt = property(GetDeleteValueInt, SetDeleteValueInt)


    def GetDeleteValueUnsignedInt(self):
        return self.FileInfo.DeleteValueUnsignedInt;

    def SetDeleteValueUnsignedInt(self, value):
        self.__CheckBuildStage1
        self.FileInfo.DeleteValueUnsignedInt = value;

    DeleteValueUnsignedInt = property(GetDeleteValueUnsignedInt, SetDeleteValueUnsignedInt)


    def SetGeographicalProjection(self, projection):
        self.__CheckBuildStage1()
        self.FileInfo.Projection = projection;
        self.isSetProjection = True;

    def SetTemporalAxis(self, temporalAxis: DfsTemporalAxis):
        self.__CheckBuildStage1()
        self.FileInfo.TimeAxis = temporalAxis;
        self.isSetTemporalAxis = True;

    def SetSpatialAxis(self, spatialAxis):
        '''
        For dfs1+2+3 files where the spatial axis is shared by all items
        the spatial axis can be set here, and reused for all dynamic 
        and static items.
        '''
        self.__CheckBuildStage1()
        self.SpatialAxis = spatialAxis;


    #def SetNumberOfTimeSteps(self, numberOfTimeSteps):
    #    self.__CheckBuildStage1()
    #    self.NumberOfTimeSteps = numberOfTimeSteps;


    def SetTimeInfo(self, firstTime, timeSpan):
        self.__CheckBuildStage1()
        self.firstTime = firstTime;
        self.timeSpan = timeSpan;


    def CreateDynamicItemBuilder(self):
        self.__CheckBuildStage1()
        return (DfsDynamicItemBuilder())

    def AddDynamicItem(self, dynamicItem):
        self.DynamicItems.append(dynamicItem);

    def AddCreateDynamicItem(self, name, quantity, dataType = DfsSimpleType.Float, valueType = DataValueType.Instantaneous, spatialAxis = None):
        if (spatialAxis is None):
            spatialAxis = self.SpatialAxis
        if (spatialAxis is None):
            raise Exception("Spatial axis must be defined when creating dynamic items")

        itemBuilder = self.CreateDynamicItemBuilder()
        itemBuilder.Set(name, quantity, dataType)
        itemBuilder.SetValueType(valueType)
        itemBuilder.SetAxis(spatialAxis)
        self.AddDynamicItem(itemBuilder.GetDynamicItemInfo())


    def AddCustomBlock(self, customBlock):
        self.__CheckBuildStage1()
        self.FileInfo.CustomBlocks.append(customBlock);

    def AddCreateCustomBlock(self, name, arrayData):
        self.__CheckBuildStage1()
        if (name == None):
            raise Exception("Name of custom block can not be null or empty");

        datatype = DfsDLLUtil.GetDfsType(arrayData);

        customBlock = DfsCustomBlock(name, datatype, arrayData)
        self.FileInfo.CustomBlocks.append(customBlock);


    def SetEncodingKey(self, xKey, yKey, zKey):
        self.FileInfo.SetEncodingKey(xKey, yKey, zKey);

    def Validate(self, dieOnError = True, seekable = True):

        errors = []
        if (not self.isSetDataType):
            errors.append("DataType has not been set.")
        if (not self.isSetProjection):
            errors.append("Projection information has not been set.")
        if (not self.isSetTemporalAxis):
            errors.append("Temporal axis has not been set.")

        fileIsCompressed = self.FileInfo.IsFileCompressed

        for customBlock in self.FileInfo.CustomBlocks:
            if (customBlock.Name == None or customBlock.Name == ""):
                errors.append("Custom block name can not be null or empty");
            if (len(customBlock.Values) == 0):
                errors.append("Custom block without data (count is zero) is invalid");

        if (len(self.DynamicItems) == 0):
            errors.append("No dynamic items defined")

        for i, itemInfo in enumerate(self.DynamicItems):
            if (itemInfo.Name == None or itemInfo.Name == ""):
                errors.append("Name of dynamic item number {} is null or empty".format(i + 1));
            if (itemInfo.SpatialAxis == None):
                errors.append("Spatial axis of dynamic item number {} can not be null".format(i+1));
                continue;

            if (fileIsCompressed):

                axis = itemInfo.SpatialAxis;
                xKey, yKey, zKey = self.FileInfo.GetEncodeKey()
                encodeKeysize = len(xKey)
                xSize = axis.SizeOfDimension(1);
                ySize = axis.SizeOfDimension(2);
                zSize = axis.SizeOfDimension(3);
                ok = True;
                for j in range(encodeKeysize):
                    if (xKey[i] >= xSize or yKey[i] >= ySize or zKey[i] >= zSize):
                        ok = False;
                        break;

                if (not ok):
                    errors.append("Encode key values are not valid for axis of dynamic item number {}".format(i + 1));

                if (itemInfo.DataType != DfsSimpleType.Float):
                    errors.append("Compressed files dynamic items must all be of type float. Dynamic item number {0} is not of type float".format(i + 1));

        #if (not seekable and self.FileInfo.StatsType != DfsStatType.NoStat):
        #    errors.append("StatsType {} is not possible for a non-seekable stream. Set StatsType to StatType.NoStat".format(self.FileInfo.StatsType));

        if (dieOnError and len(errors) > 0):
            msgs = self.ErrorMessage(errors);
            raise Exception(msgs);

        return (errors);
    
    @staticmethod
    def ErrorMessage(errors):
        if (len(errors) == 1):
            return (errors[0])
        msgs = "Several issues:"
        for err in errors:
            msgs += "\n  " + err
        return (msgs)


    def CreateFile(self, filename):
        self.__CheckBuildStage1()

        # Validate and throw an exception in case of errors
        self.Validate(True);

        filePointer = ctypes.c_void_p(0);
        headerPointer = ctypes.c_void_p(0);
        fnp = ctypes.c_char_p(filename.encode("cp1252"))
        try:
            headerPointer = self.__CreateHeader();
            DfsDLL.Wrapper.dfsFileCreate(fnp.value, headerPointer, ctypes.byref(filePointer));

        except Exception as e:

            # In case of any exception, destroy the header.
            if (headerPointer.value != None):
                  DfsDLL.Wrapper.dfsHeaderDestroy(ctypes.byref(headerPointer));
            raise e

        # The create function will free ressources, if something fails.
        dfsFile = DfsFile()
        dfsFile.Building(filename, headerPointer, filePointer)

        self.DfsFile = dfsFile;
        self.isFileCreated = True;


    def __CreateHeader(self):

        if (self.FileInfo.TimeAxis.IsEquidistant()):
            fileTypeNumber = ctypes.c_int32(1)
        else:
            fileTypeNumber = ctypes.c_int32(4)
        headerPointer = ctypes.c_void_p()
        rok = DfsDLL.Wrapper.dfsHeaderCreate(
            fileTypeNumber, 
            ctypes.c_char_p(self.FileInfo.FileTitle.encode("cp1252")), 
            ctypes.c_char_p(self.FileInfo.ApplicationTitle.encode("cp1252")), 
            ctypes.c_int32(self.FileInfo.ApplicationVersion),
            ctypes.c_int32(len(self.DynamicItems)), 
            ctypes.c_int32(self.FileInfo.StatsType.value),
            ctypes.byref(headerPointer));
        DfsDLL.CheckReturnCode(rok)

        rok = DfsDLL.Wrapper.dfsSetDataType(headerPointer, ctypes.c_int32(self.FileInfo.DataType));
        DfsDLL.CheckReturnCode(rok)

        DfsDLL.Wrapper.dfsSetDeleteValFloat      (headerPointer, ctypes.c_float(self.FileInfo.DeleteValueFloat));
        DfsDLL.Wrapper.dfsSetDeleteValDouble     (headerPointer, ctypes.c_double(self.FileInfo.DeleteValueDouble));
        DfsDLL.Wrapper.dfsSetDeleteValByte       (headerPointer, ctypes.c_int8(self.FileInfo.DeleteValueByte));
        DfsDLL.Wrapper.dfsSetDeleteValInt        (headerPointer, ctypes.c_int32(self.FileInfo.DeleteValueInt));
        DfsDLL.Wrapper.dfsSetDeleteValUnsignedInt(headerPointer, ctypes.c_uint32(self.FileInfo.DeleteValueUnsignedInt));

        projection = self.FileInfo.Projection;
        if (projection == None or projection.Type == ProjectionType.Undefined):
            rok = DfsDLL.Wrapper.dfsSetGeoInfoUndefined(headerPointer);
            DfsDLL.CheckReturnCode(rok)
        else:
            rok = DfsDLL.Wrapper.dfsSetGeoInfoUTMProj(
                headerPointer, 
                ctypes.c_char_p(projection.WKTString.encode("ascii")), 
                ctypes.c_double(projection.Longitude), 
                ctypes.c_double(projection.Latitude),
                ctypes.c_double(projection.Orientation));
            DfsDLL.CheckReturnCode(rok)

        DfsDLLUtil.dfsSetTemporalAxis(headerPointer, self.FileInfo.TimeAxis);
        #if (self.NumberOfTimeSteps < 0):
        #    DfsDLL.Wrapper.dfsSetNumberOfTimeSteps(headerPointer, self.NumberOfTimeSteps)
        if (self.FirstTime != 0 or self.TimeSpan > 0):
            rok = DfsDLL.Wrapper.dfsSetTimeStartEnd(headerPointer, ctypes.c_double(self.FirstTime), ctypes.c_double(self.TimeSpan));
            DfsDLL.CheckReturnCode(rok)

        if (self.FileInfo.IsFileCompressed):
            xkey, ykey, zkey = self.FileInfo.GetEncodeKey();
            rok = DfsDLL.Wrapper.dfsSetEncodeKey(
                headerPointer, 
                xkey.ctypes.data, 
                ykey.ctypes.data, 
                zkey.ctypes.data, 
                ctypes.c_int32(len(zkey)));
            DfsDLL.CheckReturnCode(rok)
  
        # Loop over and configure all dynamic items
        for i in range(len(self.DynamicItems)):
            itemNo = i + 1
            itemInfo = self.DynamicItems[i]
            itemPointer = ctypes.c_void_p(DfsDLL.Wrapper.dfsItemD(headerPointer, itemNo));

            DfsBuilder.__SetValuesToItem(headerPointer, itemPointer, itemInfo);
            DfsBuilder.__SetValuesToDynamicItem(headerPointer, itemPointer, itemNo, itemInfo);

        # Loop over all custom blocks
        for customBlock in self.FileInfo.CustomBlocks:
            DfsDLLUtil.dfsAddCustomBlock(headerPointer, customBlock)

        return headerPointer


    #region Static item functionality


    def AddStaticItem(self, staticItem):
        '''
        Add static item to the file.

        The static item can come from another file, then the item 
        definition and data is copied over.

        A reference to the static item written to the file. 
        This can be used at a later point if the static data needs to
        be updated, using the WriteStaticItemData
        '''
        self.__CheckBuildStage2();

        if (staticItem == None):
            raise Exception("staticItem");
        if (staticItem.Name == None or staticItem.Name == ""):
            raise Exception("Name of static item is null or empty.", "staticItem");

        staticVectorPointer = ctypes.c_void_p(0)
        itemPointer = ctypes.c_void_p(0);
        try:

            # Create a new static item
            rok = DfsDLL.Wrapper.dfsStaticCreate(ctypes.byref(staticVectorPointer));
            DfsDLL.CheckReturnCode(rok)
            if (staticVectorPointer.value == None):
                raise Exception("Unknown error creating a static item (DfsDLL.Wrapper.dfsStaticCreate returned null)");

            # Copy values to the new static item
            itemPointer = ctypes.c_void_p(DfsDLL.Wrapper.dfsItemS(staticVectorPointer));
            DfsBuilder.__SetValuesToItem(self.DfsFile.headPointer, itemPointer, staticItem);

            # From now on the responsibility of the staticVectorPointer is taken over bye the DfsStaticItem (ending the try-catch)
        except Exception as e:
            # As long as the static vector pointer is not null, the 
            # responsibility for destroying the header structure is here.
            if (staticVectorPointer.value != None):
                DfsDLL.Wrapper.dfsStaticDestroy(ctypes.byref(staticVectorPointer));
            raise e;

        # Create a DfsStaticItem that belongs to the current dfs file
        myStaticItem = DfsStaticItem(self.DfsFile, staticVectorPointer, itemPointer);
        myStaticItem.DataType = staticItem.DataType
        myStaticItem.ElementCount = staticItem.ElementCount

        # Write the definition and the data
        self.DfsFile.WriteStaticItemData(myStaticItem, staticItem.Data);

        return (myStaticItem);


    def AddCreateStaticItem(self, name, quantity, arrayData, spatialAxis = None):
        if (spatialAxis is None):
            spatialAxis = self.SpatialAxis
        if (quantity is None):
             quantity = eumQuantity.UnDefined()
        self.__CheckBuildStage2();
        staticItem = DfsStaticItem.Create(name, quantity, arrayData, spatialAxis);
        return (self.AddStaticItem(staticItem));

    def CreateStaticItemBuilder(self):
        self.__CheckBuildStage2();
        return (DfsStaticItemBuilder());


    def GetFile(self):
        if (self.DfsFile == None):
            if (self.isFileCreated):
                raise Exception("File has been returned, action is not allowed");
            raise Exception("CreateFile has not yet been called. Can not return any file");

        # Mark the start of the dynamic data, and end of header/static data
        DfsDLL.Wrapper.dfsWriteStartBlockDynamic(self.DfsFile.headPointer, self.DfsFile.filePointer);

        dfsFile = self.DfsFile;
        self.DfsFile = None;
        return (dfsFile);

    @staticmethod
    def Create(fileTitle = None, appTitle = "MIKE Core Python", appVersionNo = 1):

        if (fileTitle == None):
            fileTitle = "";
        if (appTitle == None):
            appTitle = "";

        builder = DfsBuilder(fileTitle, appTitle, appVersionNo);
        return (builder);

    @staticmethod
    def __SetValuesToItem(headerPointer, itemPointer, itemInfo):
        quantity = itemInfo.Quantity;
        rok = DfsDLL.Wrapper.dfsSetItemInfo(
            headerPointer, 
            itemPointer, 
            ctypes.c_int32(quantity.Item.value), 
            ctypes.c_char_p(itemInfo.Name.encode("cp1252")), 
            ctypes.c_int32(quantity.Unit.value), 
            ctypes.c_int32(itemInfo.DataType.value));
        DfsDLL.CheckReturnCode(rok);

        # Setting conversion before any axis values, in order to get the axis values converted.
        if (itemInfo.ConversionType != UnitConversionType.NoConversion):
            rok = DfsDLL.Wrapper.dfsSetItemUnitConversion(
                itemPointer, 
                ctypes.c_int32(itemInfo.ConversionType.value), 
                ctypes.c_int32(itemInfo.ConversionUnit.value));
            DfsDLL.CheckReturnCode(rok);
        if (itemInfo.AxisConversionType != UnitConversionType.NoConversion):
            rok = DfsDLL.Wrapper.dfsSetItemAxisUnitConversion(
                itemPointer, 
                ctypes.c_int32(itemInfo.AxisConversionType.value), 
                ctypes.c_int32(itemInfo.AxisConversionUnit.value));
            DfsDLL.CheckReturnCode(rok)

        DfsDLLUtil.dfsSetItemSpatialAxis(itemPointer, itemInfo.SpatialAxis);
        rok = DfsDLL.Wrapper.dfsSetItemRefCoords(
            itemPointer, 
            ctypes.c_float(itemInfo.ReferenceCoordinateX), 
            ctypes.c_float(itemInfo.ReferenceCoordinateY), 
            ctypes.c_float(itemInfo.ReferenceCoordinateZ));
        DfsDLL.CheckReturnCode(rok)
        rok = DfsDLL.Wrapper.dfsSetItemAxisOrientation(
            itemPointer, 
            ctypes.c_float(itemInfo.OrientationAlpha), 
            ctypes.c_float(itemInfo.OrientationPhi), 
            ctypes.c_float(itemInfo.OrientationTheta));
        DfsDLL.CheckReturnCode(rok)

    @staticmethod
    def __SetValuesToDynamicItem(headerPointer, itemPointer, itemNumber, itemInfo):

        rok = DfsDLL.Wrapper.dfsSetItemValueType(itemPointer, ctypes.c_int32(itemInfo.ValueType.value))
        DfsDLL.CheckReturnCode(rok)

        if (itemInfo.AssociatedStaticItemNumbers != None and len(itemInfo.AssociatedStaticItemNumbers) > 0):
            for staticItemNumber in itemInfo.AssociatedStaticItemNumbers:
                rok = DfsDLL.Wrapper.dfsSetAssocStatic(headerPointer, ctypes.c_int32(itemNumber), ctypes.c_int32(staticItemNumber));
                DfsDLL.CheckReturnCode(rok)


class DfsAbstractItemBuilder:
    '''
    Item builder that handles common functionality for
    the static and the dynamic items.

    The following functions must be set:
    Set,
    SetAxis.
    '''
    def __init__(self):
        self.ItemInfo = None
        self.isSetNameQuantityDataType = False;
        self.isSetSpatialAxis = False;

    def SetDefaults(self):
        self.ItemInfo.SetUnitConversion(UnitConversionType.NoConversion, 0);
        self.ItemInfo.SetAxisUnitConversion(UnitConversionType.NoConversion, 0);

    def Set(self, name, quantity, dataType):
        self.ItemInfo.Name = name;
        self.ItemInfo.Quantity = quantity;
        self.ItemInfo.DataType = dataType;
        self.isSetNameQuantityDataType = True;

    def SetAxis(self, spatialAxis):
        self.ItemInfo.SpatialAxis  = spatialAxis;
        self.ItemInfo.ElementCount = spatialAxis.SizeOfData;
        self.isSetSpatialAxis = True;

    def SetReferenceCoordinates(self, x, y, z):
        self.ItemInfo.SetReferenceCoordinates(x, y, z);

    def SetOrientation(self, alpha, phi, theta):
        self.ItemInfo.SetOrientation(alpha, phi, theta);

    def SetUnitConversion(self, convType, unit):
        self.ItemInfo.SetUnitConversion(convType, unit);

    def SetAxisUnitConversion(self, convType, unit):
        self.ItemInfo.SetAxisUnitConversion(convType, unit);

    def Validate(self):
        errors = []
        if (not self.isSetNameQuantityDataType):
            errors.append("Name, Quantity and DataType has not been set.");
        if (not self.isSetSpatialAxis):
            errors.append("Spatial axis has not been set.");

        return (errors);

class DfsDynamicItemBuilder(DfsAbstractItemBuilder):
    '''
    Builder to configure an existing dynamic item structure.

    The following functions must be set:
    Set,
    SetAxis, 
    SetValueType.

    This configures an existing dynamic item that has not yet been
    written to file, i.e., length of strings can be changed.
    '''
    def __init__(self):
        super().__init__()
        self.isSetDataValueType = False
        self.ItemInfo = DfsDynamicItemInfo();

    def SetValueType(self, valueType):
        self.ItemInfo.ValueType = valueType;
        self.isSetDataValueType = True;

    def SetAssociatedStaticItem(self, staticItemNumber):
        if (self.ItemInfo.AssociatedStaticItemNumbers == None):
            self.ItemInfo.AssociatedStaticItemNumbers = [];
        self.ItemInfo.AssociatedStaticItemNumbers.append(staticItemNumber);

    def Validate(self):
        errors = super().Validate();
        if (not self.isSetDataValueType):
            errors.append("Data valueType has not been set.");
        return (errors);


    def GetDynamicItemInfo(self):
        errors = self.Validate();

        if (len(errors) > 0):
            msgs = DfsBuilder.ErrorMessage(errors);
            raise Exception(msgs);

        # Create and store a clone, such that item-builder can be reused when creating more than one item
        # Otherwise updates to the new item-builder would just update the same item.
        res = self.ItemInfo;
        self.ItemInfo = DfsDynamicItemInfo();
        return (res);



class DfsStaticItemBuilder(DfsAbstractItemBuilder):
    '''
    Builder to configure an existing dynamic item structure.

    The following functions must be set:
    Set,
    SetAxis, 
    SetData.

    This creates a new static item when instantiated, but the item
    is not yet a part of the file. When <see cref="GetStaticItem
    is called, a <see cref="DfsStaticItemWrapper is returned that
    can be added to the <see cref="DfsBuilder.
    '''
    def __init__(self):
        super().__init__()
        self.isSetData = False
        self.ItemInfo = DfsStaticItem()
        self.SetDefaults();

    def SetData(self, data):

        self.ItemInfo.Data = data;
        self.isSetData = True;

    def Validate(self):
        errors = super().Validate();
        if (not self.isSetData):
            errors.append("Data has not been set.");
        if (self.ItemInfo.Data.size != self.ItemInfo.SpatialAxis.SizeOfData):
            errors.append("Size of data ({}) does not match spatial axis size ({}).".format(self.ItemInfo.Data.size, self.ItemInfo.SpatialAxis.SizeOfData));

        return (errors);


    def GetStaticItem(self):
        errors = self.Validate();

        if (len(errors) > 0):
            msgs = DfsBuilder.ErrorMessage(errors);
            raise Exception(msgs);

        return (self.ItemInfo);

