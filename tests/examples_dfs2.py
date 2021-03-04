from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.DfsFactory import *
from mikecore.DfsBuilder import *
from mikecore.DfsFile import *
from numpy.testing import *

class ExamplesDfs2:

    @staticmethod
    def ReadingDfs2File(filename):

        # Open the file as a dfs2 file
        dfs2File = DfsFileFactory.Dfs2FileOpen(filename);
        dfs2File.Reshape(True)

        # Spatial axis for this file is a 2D equidistant axis
        axisEqD2 = dfs2File.SpatialAxis;
        dx = axisEqD2.Dx;                                           # 900
        dy = axisEqD2.Dy;                                           # 900

        # Header information is contained in the IDfsFileInfo
        fileInfo = dfs2File.FileInfo;
        steps = fileInfo.TimeAxis.NumberOfTimeSteps;                # 13
        projectionString = fileInfo.Projection.WKTString;           # "UTM-33"

        # Information on each of the dynamic items, here the first one
        dynamicItemInfo = dfs2File.ItemInfo[0];
        nameOfFirstDynamicItem = dynamicItemInfo.Name;              # "H Water Depth m"
        typeOfFirstDynamicItem = dynamicItemInfo.DataType;          # Float

        # Read data of first item, third time step (items start by 1, timesteps by 0),
        # assuming data is of type float.
        data2D = dfs2File.ReadItemTimeStep(1, 2);
        # Get the value at (i,j) = (3,4) of the item and timestep
        value = data2D.Data[3, 4];                                   # 11.3634329
        print("ReadingDfs2File: data2D.Data[3, 4] = {}".format(value))

        # This iterates through all the timesteps and items in the file
        # For performance reasons it is important to iterate over time steps
        # first and items second.
        for i in range(steps):
          for j in range(1,len(dfs2File.ItemInfo)):
            data2D = dfs2File.ReadItemTimeStep(j, i);
            value = data2D.Data[3, 4];

    @staticmethod
    def ModifyDfs2ItemInfo(filename):

        # Open the file for editing
        file = DfsFileFactory.Dfs2FileOpenEdit(filename);

        # Original name is "Landuse" (7 characters), "GroundUse" is truncated to "GroundU"
        file.ItemInfo[0].Name = "GroundUse";
        # Provide a new quantity (updating the item and unit of the quantity directly does not work!)
        file.ItemInfo[0].Quantity = eumQuantity(eumItem.eumIAreaFraction, eumUnit.eumUPerCent);

        # done
        file.Close();

    @staticmethod
    def ModifyDfs2ItemAxis(filename):

        file = DfsFileFactory.Dfs2FileOpenEdit(filename);
        
        axisEqD2 = (file.SpatialAxis);
        axisEqD2.X0 = 55;
        axisEqD2.Dx = 905;
        axisEqD2.Y0 = -55;
        axisEqD2.Dy = 915;
        
        file.Close();



    
    #/ <summary>
    #/ Example of how to modify data of a certain item and time
    #/ step in a dfs2 file.
    #/ <para>
    #/ The method assumes that the Landuse.dfs2 test file
    #/ (or preferably a copy of it) is the input file.
    #/ </para>
    #/ </summary>
    #/ <param name="filename">Path and name of Landuse.dfs2 test file</param>
    @staticmethod
    def ModifyDfs2FileData(filename):

        # Open the file for editing
        file = DfsFileFactory.Dfs2FileOpenEdit(filename);

        # Load and modify data from the first item and timestep
        data2D = file.ReadItemTimeStepNext(reshape = True);
        data2D.Data[21, 61] = 7;
        data2D.Data[21, 62] = 6;
        data2D.Data[21, 63] = 5;
        data2D.Data[21, 64] = 4;
        data2D.Data[21, 65] = 3;

        # Write modified data back
        file.WriteItemTimeStep(1, 0, data2D.Time, data2D.Data);

        # done
        file.Close();


    #/ <summary>
    #/ Update DFS2 bathymetry, lowering bathymetry with 5.61 meters everywhere,
    #/ taking land value into account.
    #/ <para>
    #/ The method assumes that the OresundBathy900.dfs2 test file
    #/ (or preferably a copy of it) is the input file.
    #/ </para>
    #/ </summary>
    #/ <param name="bathyFilename">Path and name of OresundBathy900.dfs2 test file</param>
    @staticmethod
    def ModifyDfs2Bathymetry(bathyFilename):

        # Open file
        dfs2 = DfsFileFactory.Dfs2FileOpenEdit(bathyFilename);

        # Second custom block (index 1) contains the M21_MISC values, 
        # where the 4th (index 3) is the land value
        landValue = dfs2.FileInfo.CustomBlocks[1][3];

        # Read bathymetry data
        bathyData = dfs2.ReadItemTimeStepNext();

        # Modify bathymetry data
        for i in range(bathyData.Data.size):
          if (bathyData.Data[i] != landValue):
            bathyData.Data[i] -= 5.61;

        # Write back bathymetry data
        dfs2.WriteItemTimeStep(1, 0, 0, bathyData.Data);
        dfs2.Close();

    #/ <summary>
    #/ Example of how to create a Dfs2 file from scratch. This method
    #/ creates a copy of the OresundHD.dfs2 test file.
    #/ <para>
    #/ Data for static and dynamic item is taken from a source dfs file,
    #/ which here is the OresundHD.dfs2 test file. The data could come
    #/ from any other source. 
    #/ </para>
    #/ </summary>
    #/ <param name="sourceFilename">Path and name of the OresundHD.dfs2 test file</param>
    #/ <param name="filename">Path and name of the new file to create</param>
    @staticmethod
    def CreateDfs2File(sourceFilename, filename):

        source = DfsFileFactory.Dfs2FileOpen(sourceFilename);

        factory = DfsFactory();
        builder = DfsBuilder.Create("", r"C:\Program Files\DHI\2010\bin\nmodel.exe", 0);

        # Set up the header
        builder.SetDataType(1);
        builder.SetGeographicalProjection(factory.CreateProjectionGeoOrigin("UTM-33", 12.438741600559766, 55.225707842436385, 326.99999999999955));
        builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(1993, 12,  2, 0, 0, 0), 0, 86400));
        builder.SetSpatialAxis(factory.CreateAxisEqD2(eumUnit.eumUmeter, 71, 0, 900, 91, 0, 900));
        builder.DeleteValueFloat = -1e-30;

        # Add custom block 
        # M21_Misc : {orientation (should match projection), drying depth, -900=has projection, land value, 0, 0, 0}
        builder.AddCustomBlock(factory.CreateCustomBlock("M21_Misc", np.array([ 327, 0.2, -900, 10, 0, 0, 0 ], np.float32)));

        # Set up dynamic items
        builder.AddCreateDynamicItem("H Water Depth m", eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter), DfsSimpleType.Float, DataValueType.Instantaneous);
        builder.AddCreateDynamicItem("P Flux m^3/s/m", eumQuantity.Create(eumItem.eumIFlowFlux, eumUnit.eumUm3PerSecPerM), DfsSimpleType.Float, DataValueType.Instantaneous);
        builder.AddCreateDynamicItem("Q Flux m^3/s/m", eumQuantity.Create(eumItem.eumIFlowFlux, eumUnit.eumUm3PerSecPerM), DfsSimpleType.Float, DataValueType.Instantaneous);

        # Create file
        builder.CreateFile(filename);

        # Add static items containing bathymetri data, use data from source
        sourceStaticItem = source.ReadStaticItemNext();
        builder.AddCreateStaticItem("Static item", eumQuantity.UnDefined(), sourceStaticItem.Data);

        # Get the file
        file = builder.GetFile();

        # Loop over all time steps
        for i in range(source.FileInfo.TimeAxis.NumberOfTimeSteps):
          # Loop over all items
          for j in range(len(source.ItemInfo)):
            # Add data for all item-timesteps, copying data from source file.

            # Read data from source file
            sourceData = source.ReadItemTimeStepNext(reshape=True);

            # Create empty item data, and copy over data from source
            # The IDfsItemData2D can handle 2D indexing, on the form data2D[k,l].
            # An ordinary array, float[], can also be used, though indexing from 2D to 1D must be 
            # handled by user code i.e. using data1D[k + l*xCount] compared to data2D[k,l]
            itemData2D = file.CreateEmptyItemData(j+1, reshape = True);
            for k in range(71):
              for l in range(91):
                itemData2D.Data[k, l] = sourceData.Data[k, l];

            # the itemData2D.Data is a float[], so any float[] of the correct size is valid here.
            file.WriteItemTimeStep(j + 1, i, sourceData.Time, itemData2D.Data);

        source.Close();
        file.Close();

#    #/ <summary>
#    #/ Create maximum velocity field for a dfs2 file
#    #/ <para>
#    #/ FFrom a dfs2 file containing items (H-P-Q), (P-Q-Speed) or  (u-v-Speed), 
#    #/ find maximum velocity for each cell and store in [outputFilename] 
#    #/ </para>
#    #/ </summary>
#    def MaxVelocityField(sourceFilename, outfilename):
#
#        # Open source file
#        source = DfsFileFactory.Dfs2FileOpen(sourceFilename);
#
#        # Create output file
#        builder = Dfs2Builder.Create("Max Velocity", r"MIKE SDK", 0);
#
#        # Set up the header
#        builder.SetDataType(1);
#        builder.SetGeographicalProjection(source.FileInfo.Projection);
#        builder.SetTemporalAxis(source.FileInfo.TimeAxis);
#        builder.SetSpatialAxis(source.SpatialAxis);
#        builder.DeleteValueFloat = -1e-30;
#
#        # Add custom block 
#        for customBlock in source.FileInfo.CustomBlocks:
#          builder.AddCustomBlock(customBlock);
#
#        # Set up dynamic items
#        builder.AddDynamicItem("Maximum Speed"  , eumQuantity.Create(eumItem.eumIFlowVelocity, eumUnit.eumUmeterPerSec), DfsSimpleType.Float, DataValueType.Instantaneous);
#        builder.AddDynamicItem("u-velocity"     , eumQuantity.Create(eumItem.eumIFlowVelocity, eumUnit.eumUmeterPerSec), DfsSimpleType.Float, DataValueType.Instantaneous);
#        builder.AddDynamicItem("v-velocity"     , eumQuantity.Create(eumItem.eumIFlowVelocity, eumUnit.eumUmeterPerSec), DfsSimpleType.Float, DataValueType.Instantaneous);
#        #builder.AddDynamicItem("H Water Depth m", eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter), DfsSimpleType.Float, DataValueType.Instantaneous);
#
#        # Create file
#        builder.CreateFile(outfilename);
#
#        # Add static items containing bathymetri data, use data from source
#
#        sourceStaticItem;
#        while(True):
#            sourceStaticItem = source.ReadStaticItemNext()
#            if sourceStaticItem == None:
#                break;
#        builder.AddCreateStaticItem(sourceStaticItem.Name, sourceStaticItem.Quantity, sourceStaticItem.Data);
#
#        # Get the file
#        file = builder.GetFile();
#
#        # Arrays storing max-speed values
#        numberOfCells = file.SpatialAxis.SizeOfData;
#        maxSpeed     = np.zeros(numberOfCells, dtype = np.float32);
#        uAtMaxSpeed  = np.zeros(numberOfCells, dtype = np.float32);
#        vAtMaxSpeed  = np.zeros(numberOfCells, dtype = np.float32);
#        # Initialize with delete values
#        for i in range(numberOfCells):
#
#          maxSpeed[i] = source.FileInfo.DeleteValueFloat;
#          uAtMaxSpeed[i] = source.FileInfo.DeleteValueFloat;
#          vAtMaxSpeed[i] = source.FileInfo.DeleteValueFloat;
#
#
#        # Create empty ItemData's, for easing reading of source data
#        datas = [];
#        for i in range(source.ItemInfo.Count):
#          datas.append(source.CreateEmptyItemData(i + 1));
#
#        # Find HPQ items in file - uses StartsWith, since the string varies slightly with the version of the engine.
#        itemInfo = source.ItemInfo;
#        if (itemInfo == null):
#            return;
#        dIndex = itemInfo.FindIndex(item => item.Name.StartsWith("H Water Depth", StringComparison.OrdinalIgnoreCase));
#        pIndex = itemInfo.FindIndex(item => item.Name.StartsWith("P Flux", StringComparison.OrdinalIgnoreCase));
#        qIndex = itemInfo.FindIndex(item => item.Name.StartsWith("Q Flux", StringComparison.OrdinalIgnoreCase));
#        sIndex = itemInfo.FindIndex(item => item.Name.StartsWith("Current Speed", StringComparison.OrdinalIgnoreCase));
#        uIndex = itemInfo.FindIndex(item => item.Name.StartsWith("U velocity", StringComparison.OrdinalIgnoreCase));
#        vIndex = itemInfo.FindIndex(item => item.Name.StartsWith("V velocity", StringComparison.OrdinalIgnoreCase));
#        # Either p and q must be there, or u and v, and either d or s must be there.
#        haspq = (pIndex >= 0 and qIndex >= 0);
#        hasuv = (uIndex >= 0 and vIndex >= 0);
#        if (not hasuv and not haspq or dIndex < 0 and sIndex < 0):
#            raise Exception("Could not find items. File must have H-P-Q items, P-Q-Speed or U-V-Speed items");
#
#        dItem = datas[dIndex] if dIndex >= 0 else null;
#        pItem = datas[pIndex] if pIndex >= 0 else null;
#        qItem = datas[qIndex] if qIndex >= 0 else null;
#        sItem = datas[sIndex] if sIndex >= 0 else null;
#        uItem = datas[uIndex] if uIndex >= 0 else null;
#        vItem = datas[vIndex] if vIndex >= 0 else null;
#
#        # Spatial 2D axis
#        axis =  source.SpatialAxis;
#        dx = axis.Dx;
#        dy = axis.Dy;
#
#        # Loop over all time steps
#        for i in range(source.FileInfo.TimeAxis.NumberOfTimeSteps):
#
#          # Read data for all items from source file. That will also update the depth, p and q.
#          for j in range(source.ItemInfo.Count):
#
#            source.ReadItemTimeStep(datas[j], i);
#
#
#          # For each cell, find maximum speed and store u, v and depth at that poin time.
#          for j in range(numberOfCells):
#
#            # Skip delete values
#            if (dItem.Data[j] == source.FileInfo.DeleteValueFloat or
#                sItem.Data[j] == source.FileInfo.DeleteValueFloat):
#              continue;
#
#            p = pItem.Data[j];
#            q = qItem.Data[j];
#            speed, u, v;
#            if (sItem != null):
#              # Use speed from result file
#              speed = sItem.Data[j];
#
#              if (hasuv):
#                # Use u and v from result file
#                u = uItem.Data[j];
#                v = vItem.Data[j];
#              else: # (haspq)
#                # Calculate u and v from speed and direction of p and q
#                pqLength = Math.Sqrt(p * p + q * q);
#                u = uItem.Data[j] if hasuv else speed * p / pqLength;
#                v = vItem.Data[j] if hasuv else speed * q / pqLength;
#
#            else: # (dItem != null)
#              # Current speed is not directly available in source file, calculate from u and v
#              if (hasuv):
#                u = uItem.Data[j];
#                v = vItem.Data[j];
#              else:
#                # u and v is not available, calculate fromdh, p and q.
#                d = dItem.Data[j];
#                u = pItem.Data[j] / d;
#                v = qItem.Data[j] / d;
#              speed = Math.Sqrt(u * u + v * v);
#
#            if (speed > maxSpeed[j]):
#              maxSpeed[j]    = speed;
#              uAtMaxSpeed[j] = u;
#              vAtMaxSpeed[j] = v;
#
#        file.WriteItemTimeStepNext(0, maxSpeed);
#        file.WriteItemTimeStepNext(0, uAtMaxSpeed);
#        file.WriteItemTimeStepNext(0, vAtMaxSpeed);
#        #file.WriteItemTimeStepNext(0, maxDepth);
#
#        source.Close();
#        file.Close();

    @staticmethod
    def CreateM21Bathymetry(bathyDataArray, filename):

        factory = DfsFactory();
        builder = DfsBuilder.Create(r"C:\0\Training\Bat1_0.dfs2", r"Grid editor", 1);

        # Set up the header
        builder.SetDataType(0);
        builder.SetGeographicalProjection(factory.CreateProjectionGeoOrigin("UTM-33", 12.438741600559911, 55.2257078424238, 327));
        builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime.datetime(2003,  1,  1, 0, 0, 0), 0, 1));
        builder.SetSpatialAxis(factory.CreateAxisEqD2(eumUnit.eumUmeter, 72, 0, 900, 94, 0, 900));
        builder.DeleteValueFloat = -1e-30;

        builder.AddCustomBlock(factory.CreateCustomBlock("Display Settings", np.array([ 1, 0, 0 ], np.int32)));
        builder.AddCustomBlock(factory.CreateCustomBlock("M21_Misc", np.array([ 327, 0, -900, 10, 0, 0, 0 ], np.float32)));

        # Set up dynamic items
        builder.AddCreateDynamicItem("Bathymetry", eumQuantity.Create(eumItem.eumIWaterLevel, eumUnit.eumUmeter),
                                     DfsSimpleType.Float, DataValueType.Instantaneous);

        # Create and get file
        builder.CreateFile(filename);
        file = builder.GetFile();

        # Add bathymetry data
        file.WriteItemTimeStepNext(0, bathyDataArray);

        file.Close();

#    #/ <summary>
#    #/ Example of how to resample a dfs2 file in x/y space
#    #/ </summary>
#    #/ <param name="inputFilename">Path and name of the file to resample</param>
#    #/ <param name="outputFilename">Path and name of the new file to create</param>
#    #/ <param name="xCount">Number of cells in x-direction</param>
#    #/ <param name="yCount">Number of cells in y-direction</param>
#    def Resample(inputFilename, outputFilename, xCount, yCount):
#
#        # Load dfs2 file
#        dfs2File = DfsFileFactory.Dfs2FileOpen(inputFilename);
#        axis = dfs2File.SpatialAxis;
#        
#        # Create reprojector
#        reproj = Dfs2Reprojector(dfs2File, outputFilename);
#
#        # scale change
#        dxScale = axis.XCount / xCount;
#        dyScale = axis.YCount / yCount;
#
#        # Calculate new lon/lat origin - center of lower left cell
#        cart = Projections.Cartography(dfs2File.FileInfo.Projection.WKTString, dfs2File.FileInfo.Projection.Longitude, dfs2File.FileInfo.Projection.Latitude, dfs2File.FileInfo.Projection.Orientation);
#        # Change in center of lower left cell
#        dxOrigin = 0.5 * axis.Dx * (dxScale-1);
#        dyOrigin = 0.5 * axis.Dy * (dyScale-1);
#        cart.Xy2Geo(dxOrigin, dyOrigin, out double lonOrigin, out double latOrigin);
#
#        # Set new target
#        reproj.SetTarget(dfs2File.FileInfo.Projection.WKTString, lonOrigin, latOrigin, dfs2File.FileInfo.Projection.Orientation, xCount, 0, axis.Dx*dxScale, yCount, 0, axis.Dy*dyScale);
#        reproj.Interpolate = true;
#        # Create new file
#        reproj.Process();


#    #/ <summary>
#    #/ Example of how to get from a geographical coordinate to an (j,k) index
#    #/ in the 2D grid. It also shows how to get the closest cell value and how 
#    #/ to perform bilinear interpolation.
#    #/ <para>
#    #/ The method assumes that the OresundHD.dfs2 test file is the input file.
#    #/ </para>
#    #/ </summary>
#    #/ <param name="filename">Path and name of OresundHD.dfs2 test file</param>
#    def GetjkIndexForGeoCoordinate(filename):
#
#        file = DfsFileFactory.Dfs2FileOpen(filename);
#
#        # The spatial axis is a EqD2 axis
#        axis = file.SpatialAxis;
#
#        # Data for first time step
#        data = file.ReadItemTimeStep(1, 0);
#
#        # Get the projection and create a cartography object
#        projection = file.FileInfo.Projection;
#        cart = DHI.Projections.Cartography(projection.WKTString, projection.Longitude, projection.Latitude, projection.Orientation);
#
#        # Coordinates just south of Amager
#        lon = 12.59;
#        lat = 55.54;
#
#        # Get the (x,y) grid coordinates
#        x;
#        y;
#        cart.Geo2Xy(lon, lat, out x, out y);
#
#        Console.Out.WriteLine("Grid coordinates          (x,y) = ({0:0.000},{1:0.000})", x, y);
#        Console.Out.WriteLine("Relative grid coordinates (x,y) = ({0:0.000},{1:0.000})", x / axis.Dx, y / axis.Dy);
#
#        # Calculate the cell indices of the lon-lat coordinate. 
#        # The cell extents from its center and +/- 1/2 dx and dy 
#        # in each direction
#        j = (int)(x / axis.Dx + 0.5);  # 30
#        k = (int)(y / axis.Dy + 0.5);  # 27
#
#        Console.Out.WriteLine("Value in cell ({0},{1})           = {2}", j, k, data[j, k]);
#
#        # If you want to interpolate between the values, calculate
#        # the (j,k) indices of lower left corner and do bilinear interpolation.
#        # This procedure does not take delete values into account!!!
#        j = (int)(x / axis.Dx);  # 30
#        k = (int)(y / axis.Dy);  # 26
#
#        xFrac = (x % axis.Dx) / axis.Dx;  # fraction of j+1 value
#        yFrac = (y % axis.Dy) / axis.Dy;  # fraction of k+1 value
#
#        vk = (1 - xFrac) * data[j, k] + xFrac * data[j + 1, k];
#        vkp1 = (1 - xFrac) * data[j, k + 1] + xFrac * data[j + 1, k + 1];
#        v = (1 - yFrac) * vk + yFrac * vkp1;
#
#        Console.Out.WriteLine("Interpolated value              = {0}", v);
#
#        file.Close();

