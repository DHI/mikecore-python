from datetime import datetime
from mikecore.DfsFileFactory import *
from mikecore.DfsuBuilder import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.DfsuFile import *
from mikecore.Projections import *
from mikecore.eum import *

class ExamplesDfsu:
    #/ Introductory example of how to load a dfsu file.
    #/ The method assumes that the OresundHD.dfsu test file
    #/ is the input file.
    def ReadingDfsuFile(filename):
      file = DfsuFile.Open(filename);

      # Read geometry
      numberOfElements = file.NumberOfElements;        # 3636
      numberOfNodes = file.NumberOfNodes;              # 2057
      firstNodeXCoordinate = file.X[0];             # 359978.8
      firstElementNodes = file.ElementTable[0];      # [1, 2, 3]

      # Read dynamic item info
      firstItemName = file.ItemInfo[0].Name;        # "Surface elevation"
      quantity = file.ItemInfo[0].Quantity;    # eumISurfaceElevation in eumUmeter

      # load data for the first item, 6th timestep
      itemTimeStepData = file.ReadItemTimeStep(1, 5).Data;
      # Read the value of the third element
      thirdElementValue = itemTimeStepData[2];       # 0.0014070312

      file.Close();

    #/ Find element (index) for a specified coordinate
    #/ The method assumes that the OresundHD.dfsu test file
    #/ is the input file.
    #/ <param name="filename">path and name of OresundHD.dfsu test file</param>
    def FindElementForCoordinate(filename):
      file = DfsuFile.Open(filename);
      X = file.X;
      Y = file.Y;

      # Coordinate to search for
      xc = 346381;
      yc = 6153637;

      # Loop over all elements - linear search, which may be slow!
      # If to find element for a large number of coordinates and if especially the
      # file has many elements, then a search tree procedure should be used to
      # optimize the searching performance.
      elmt = -1;  # result of search
      for i in range(file.NumberOfElements):
        # Take out nodes for element
        nodes = file.ElementTable[i];

        # Loop over all faces in element. The coordinate (x,y) is
        # inside an element if the coordinate is "left of" all faces,
        # when travelling faces counter-clockwise

        isInside = True;
        for j in range(nodes.size):
          # face start/end node indices
          a = nodes[j] - 1;
          b = nodes[(j + 1)%nodes.size] - 1;

          # Assuming face is A->B and coordinate is C, then "left of" test:
          # (B-A) X (C-A) > 0
          # where X is the cross product
          cross = (X[b] - X[a])*(yc - Y[a]) - (Y[b] - Y[a])*(xc - X[a]);
          if (cross < 0):
            # (xc, yc) is "right of", hence not inside, skip to next element
            isInside = False;
            break;
        if (isInside):
          # All "left of" tests succeded, element found!
          elmt = i;
          break;
      
      if (elmt >= 0):
        print("Found     element index: = {}".format(elmt));
        print("(xc,yc) = ({},{})".format(xc, yc));
        resNodes = file.ElementTable[elmt];
        for j in range(resNodes.size):
          node = resNodes[j] - 1;
          print("(x,y)   = ({0},{1})".format(X[node], Y[node]));

      return elmt

      file.Close();


    #/ Example of how to modify the geometry of a dfsu file.
    #/ The method will rotate the geometry by 125 degrees.
    #/ The method will work on any dfsu file. The OresundHD.dfsu test file
    #/ (preferably a copy of it) can be used as input file.
    #/ <param name="filename">Path and name of a dfsu file</param>
    def ModifyDfsuFileGeometry(filename):
      # Open file for editing
      dfsuFile = DfsuFile.OpenEdit(filename);
      dfsuFile.TimeStepInSeconds /= 2;
      dfsuFile.StartDateTime = datetime.datetime(2019,6,27,13,50,30);

      # Make a rotation matrix
      rotation = 125.0 / 180.0 * Math.PI;
      x1 = Math.Cos(rotation);
      y1 = -Math.Sin(rotation);
      x2 = Math.Sin(rotation);
      y2 = Math.Cos(rotation);

      # Get the x- and y-coordinates from the file
      x = dfsuFile.X;
      y = dfsuFile.Y;

      # Poto rotate around
      x0 = x[0];
      y0 = y[0];

      # Rotate coordinates
      for i in range(dfsuFile.NumberOfNodes):
        xx = x[i] - x0;
        yy = y[i] - y0;
        x[i] = x1 * xx + y1 * yy + x0;
        y[i] = x2 * xx + y2 * yy + y0;
  
      # Set the x- and y-coordinates back to the file
      dfsuFile.X = x;
      dfsuFile.Y = y;

      # Close the file
      dfsuFile.Close();

    #/ Example on how to extract dfs0 data from a 2D dfsu file for certain elements. All items
    #/ from dfsu file are extracted.
    #/ <param name="dfsuFileNamePath">Name, including path, of 2D dfsu file</param>
    #/ <param name="elmtsIndices">Indices of elements to extract data from</param>
    def ExtractDfs0FromDfsu(dfsuFileNamePath, elmtsIndices):
      # If not using stream approach, at most 400 elements at a time can be processed.
      # There is a limit on how many files you can have open at the same time using
      # the standard approach. It will fail in a nasty way, if the maximum number of
      # file handles are exceeded. This is not an issue when using .NET streams.
      if (elmtsIndices.size > 400):
        raise Exception("At most 400 elements at a time");

      # Open source dfsu file
      source = DfsuFile.Open(dfsuFileNamePath);

      # Figure out "basic" dfs0 file name
      dfs0BaseFilename = "testdata/testtmp/test_dfsuTodfs0-";

      # Factory for creating dfs objects
      factory = DfsFactory();

      # Create a dfs0 file for each element in elmtsIndices
      dfs0Files   = []
      timeSpan = source.TimeStepInSeconds * source.NumberOfTimeSteps;
      for k in range(elmtsIndices.size):
        # Index of element to create dfs0 for
        elmtsIndex = elmtsIndices[k];

        # Calculate element center coordinates, to be stored in dfs0 items.
        # Stored as in dfs0, hence possible loss of precision...
        x=0; y=0; z=0;
        nodeNumbers = source.ElementTable[elmtsIndex];
        for i in range(nodeNumbers.size):
          nodeIndex = nodeNumbers[i]-1; # from number to index
          x += source.X[nodeIndex];
          y += source.Y[nodeIndex];
          z += source.Z[nodeIndex];
        x /= nodeNumbers.size;
        y /= nodeNumbers.size;
        z /= nodeNumbers.size;

        # Start building dfs0 file header
        builder = DfsBuilder.Create("fileTitle", "appTitle", 1);
        builder.SetDataType(1); # standard dfs0 value
        builder.SetGeographicalProjection(source.Projection);
        builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, source.StartDateTime, 0, source.TimeStepInSeconds));

        # Add all dynamic items from dfsu file to dfs0 file
        for j in range(len(source.ItemInfo)):
          sourceItem = source.ItemInfo[j];
          itemBuilder = builder.CreateDynamicItemBuilder();
          itemBuilder.Set(sourceItem.Name, sourceItem.Quantity, sourceItem.DataType);
          itemBuilder.SetAxis(factory.CreateAxisEqD0());
          itemBuilder.SetValueType(sourceItem.ValueType);
          itemBuilder.SetReferenceCoordinates(x, y, z); # optional
          builder.AddDynamicItem(itemBuilder.GetDynamicItemInfo());

        # Create and get file, store them in dfs0s array
        dfs0Filename = dfs0BaseFilename + "{:0>5d}".format(elmtsIndex) + ".dfs0";
        # Create file in the ordinary way. Will include statistics (of delete values etc).
        builder.CreateFile(dfs0Filename);
        dfs0Files.append(builder.GetFile());
  
      # For performance, use predefined itemdata objects when reading data from dfsu
      dfsuItemDatas = []
      for j in range(len(source.ItemInfo)):
        dfsuItemDatas.append(source.ItemInfo[j].CreateEmptyItemData());
  
      dfs0Data = np.zeros(1, dtype=np.float32)
      # Read data from dfsu and store in dfs0
      for i in range(source.NumberOfTimeSteps):
        for j in range(len(source.ItemInfo)):
          dfsuItemData = dfsuItemDatas[j];
          ok = source.ReadItemTimeStep(dfsuItemData, i);
          floats = dfsuItemData.Data;

          # write data to dfs0's
          for k in range(elmtsIndices.size):
            elmtsIndex = elmtsIndices[k];
            dfs0Data[0] = floats[elmtsIndex];
            dfs0Files[k].WriteItemTimeStepNext(0, dfs0Data);
            
      # Close dfsu files
      source.Close();
      # Close all dfs0 files
      for k in range(elmtsIndices.size):
        dfs0Files[k].Close();


    #/ Example of how to create a Dfsu file from scratch. This method
    #/ creates a copy of the OresundHD.dfsu test file.
    #/ Data for static and dynamic item is taken from a source dfs file,
    #/ which here is the OresundHD.dfsu test file. The data could come
    #/ from any other source.
    #/ <param name="sourceFilename">Path and name of the OresundHD.dfsu test file</param>
    #/ <param name="filename">Path and name of the new file to create</param>
    #/ <param name="zInMeters">Flag specifying whether the z values are in meters or feet </param>
    def CreateDfsuFile(sourceFilename, filename, zInMeters):
      source = DfsuFile.Open(sourceFilename);

      builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D);
      builder.FileTitle = source.FileTitle

      # Setup header and geometry, copy from source file
      builder.SetNodes(source.X, source.Y, source.Z, source.Code);
      builder.SetElements(source.ElementTable);
      builder.SetProjection(source.Projection);
      builder.SetTimeInfo(source.StartDateTime, source.TimeStepInSeconds);
      if (zInMeters):
        builder.SetZUnit(eumUnit.eumUmeter);
      else:
        builder.SetZUnit(eumUnit.eumUfeet);

      # Add dynamic items, copying from source
      for itemInfo in source.ItemInfo:
        builder.AddDynamicItem(itemInfo.Name, itemInfo.Quantity);

      dfsufile = builder.CreateFile(filename);

      # Add data for all item-timesteps, copying from source
      while (True):
        sourceData = source.ReadItemTimeStepNext()
        if (sourceData is None):
          break;
        dfsufile.WriteItemTimeStepNext(sourceData.Time, sourceData.Data);

      source.Close();
      dfsufile.Close();


    #/ Extract a single layer from a 3D dfsu file, and write it to a 2D dfsu file.
    #/ If a layer value does not exist for a certain 2D element, delete value is written
    #/ to the 2D resut file. This is relevant for Sigma-Z type of files.
    #/ <param name="filenameDfsu3">Name of 3D dfsu source file</param>
    #/ <param name="filenameDfsu2">Name of 2D dfsu result file</param>
    #/ <param name="layerNumber">Layer to extract.
    #/   <para>
    #/     Positive values count from bottom up i.e. 1 is bottom layer, 2 is second layer from bottom etc.
    #/   </para>
    #/   <para>
    #/     Negative values count from top down, i.e. -1 is toplayer, -2 is second layer from top etc.
    #/   </para>
    #/ </param>
    def ExtractDfsu2DLayerFrom3D(filenameDfsu3, filenameDfsu2, layerNumber):
      dfsu3File = DfsFileFactory.DfsuFileOpen(filenameDfsu3);

      # Check that dfsu3 file is a 3D dfsu file.
      switch (dfsu3File.DfsuFileType)
      if (    dfsu3File.DfsuFileType == DfsuFileType.Dfsu2D
        or dfsu3File.DfsuFileType == DfsuFileType.DfsuVerticalColumn
        or dfsu3File.DfsuFileType == DfsuFileType.DfsuVerticalProfileSigma
        or dfsu3File.DfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ):
          raise Exception("Input file is not a 3D dfsu file");
  
      # Calculate offset from toplayer element. Offset is between 0 (top layer) and
      # dfsu3File.NumberOfLayers-1 (bottom layer)
      topLayerOffset;
      if (layerNumber > 0 and layerNumber <= dfsu3File.NumberOfLayers):
        topLayerOffset = dfsu3File.NumberOfLayers - layerNumber;
      elif (layerNumber < 0 and -layerNumber <= dfsu3File.NumberOfLayers):
        topLayerOffset = -layerNumber - 1;
      else:
        raise Exception("Layer number is out of range");
  
      xv = dfsu3File.X;
      yv = dfsu3File.Y;
      zv = dfsu3File.Z;
      cv = dfsu3File.Code;

      # --------------------------------------------------
      # Create 2D mesh from 3D mesh

      # List of new 2D nodes
      node2DCount = 0;
      xv2 = []
      yv2 = []
      zv2 = []
      cv2 = []

      # Renumbering array, from 3D node numbers to 2D node numbers
      # i.e. if a 3D element refers to node number k, the 2D element node number is renumber[k]
      renumber = np.zeros(dfsu3File.NumberOfNodes, dtype=np.int32);

      # Coordinates of last created node
      xr2 = -1e-10;
      yr2 = -1e-10;

      # Create 2D nodes, by skipping nodes with equal x,y coordinates
      for i in range(dfsu3File.NumberOfNodes):
        # If 3D x,y coordinates are equal to the last created 2D node,
        # map this node to the last created 2D node, otherwise
        # create new 2D node and map to that one
        if (xv[i] != xr2 or yv[i] != yr2):
          # Create new node
          node2DCount += 1;
          xr2 = xv[i];
          yr2 = yv[i];
          zr2 = zv[i];
          cr2 = cv[i];
          xv2.append(xr2);
          yv2.append(yr2);
          zv2.append(zr2);
          cv2.append(cr2);
        # Map this 3D node to the last created 2D node.
        renumber[i] = node2DCount;
  
      # Find indices of top layer elements
      topLayer = dfsu3File.FindTopLayerElements();

      # Create element table for 2D dfsu file
      elmttable2 = np.zeros(dfsu3File.NumberOfNodes, dtype=object);
      for i in range(len(topLayer)):
        # 3D element nodes
        elmt3 = dfsu3File.ElementTable[topLayer[i]];
        # 2D element nodes, only half as big, so copy over the first half
        elmt2 = np.zeros(elmt3.size / 2, dtype=np.int32);
        for j in range(elmt2.size):
          elmt2[j] = renumber[elmt3[j]];
        elmttable2[i] = elmt2;
  
      # --------------------------------------------------
      # Create 2D dfsu file
      builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D);

      # Setup header and geometry
      builder.SetNodes(xv2.ToArray(), yv2.ToArray(), zv2.ToArray(), cv2.ToArray());
      builder.SetElements(elmttable2);
      builder.SetProjection(dfsu3File.Projection);
      builder.SetTimeInfo(dfsu3File.StartDateTime, dfsu3File.TimeStepInSeconds);
      if (dfsu3File.ZUnit == eumUnit.eumUUnitUndefined):
        builder.SetZUnit(eumUnit.eumUmeter);
      else:
        builder.SetZUnit(dfsu3File.ZUnit);

      # Add dynamic items, copying from source, though not the first one, if it
      # contains the z-variation on the nodes
      for i in range(len(dfsu3File.ItemInfo)):
        itemInfo = dfsu3File.ItemInfo[i];
        if (itemInfo.ElementCount == dfsu3File.NumberOfElements):
          builder.AddDynamicItem(itemInfo.Name, itemInfo.Quantity);
  
      # Create file
      dfsu2File = builder.CreateFile(filenameDfsu2);

      # --------------------------------------------------
      # Process data

      # Check if the layer number exists for 2D element, i.e. if that element
      # in 2D has that number of columnes in the 3D (relevant for sigma-z files)
      # If elementExists[i] is false, write delete value to file
      elementExists = np.zeros(len(topLayer), dtype=bool);
      numLayersInColumn = topLayer[0] + 1;
      elementExists[0] = (numLayersInColumn - topLayerOffset) > 0;
      for i in range(1,len(topLayer)):
        numLayersInColumn = (topLayer[i] - topLayer[i - 1]);
        elementExists[i] = (numLayersInColumn - topLayerOffset) > 0;
  
      # For performance, use predefined itemdata objects when reading data from dfsu 3D file
      dfsu3ItemDatas = []
      for j in range(len(dfsu3File.ItemInfo)):
        dfsu3ItemDatas.append(dfsu3File.ItemInfo[j].CreateEmptyItemData());
  
      # data to write to dfsu 2D file
      data2 = np.zeros(dfsu2File.NumberOfElements, dtype=np.float32);
      deleteValueFloat = dfsu2File.DeleteValueFloat;

      for i in range(dfsu3File.NumberOfTimeSteps):
        for j in range(len(dfsu3File.ItemInfo)):
          # Read data from 3D dfsu
          data3Item = dfsu3ItemDatas[j];
          ok = dfsu3File.ReadItemTimeStep(data3Item, i);
          # 3D data
          data3 = data3Item.Data;

          # Skip any items not having size = NumberOfElments (the z-variation on the nodes)
          if (data3.size != dfsu3File.NumberOfElements):
            continue;

          # Loop over all 2D elements
          for k in range(elmtsIndices.size):
            # Extract layer data from 3D column into 2D element value
            if (elementExists[k]):
              data2[k] = data3[topLayer[k] - topLayerOffset];
            else:
              data2[k] = deleteValueFloat;
      
          dfsu2File.WriteItemTimeStepNext(data3Item.Time, data2);
      
      dfsu3File.Close();
      dfsu2File.Close();


    #/ Create dfsu and mesh file from dfs2 file.
    #/ Note 1: Boundary code is set to land value at
    #/         all boundaries of mesh and dfsu file.
    #/         These must be updated to something "better"
    #/         if to use as input in another simulation.
    #/ Note 2: P and Q values are not rotated with the
    #/         grid, but should be so, if used in the
    #/         projected coordinate system. It must take
    #/         the 327 degrees rotation into account.
    #/ <param name="dfs2Filename">Name of input dfs2 file, e.g. the OresundHD.dfs2</param>
    #/ <param name="meshFilename">Name ou output mesh file</param>
    #/ <param name="dfsuFilename">Name of output dfsu file</param>
    def CreateDfsuFromDfs2(dfs2Filename, meshFilename, dfsuFilename):

      # Open file
      dfs2 = DfsFileFactory.Dfs2FileOpen(dfs2Filename);

      # Read bathymetry from first static item
      bathymetryItem = dfs2.ReadStaticItemNext();
      bathymetry = bathymetryItem.Data;

      # Extract spatial axis
      spatialAxis = dfs2.SpatialAxis;
      # Some convenience variables
      dx = spatialAxis.Dx;
      dy = spatialAxis.Dy;
      x0 = spatialAxis.X0;
      y0 = spatialAxis.Y0;
      xCount = spatialAxis.XCount;
      yCount = spatialAxis.YCount;

      # First custom block (index 0) contains the M21_MISC values,
      # where the 4th (index 3) is the land value
      landValue = dfs2.FileInfo.CustomBlocks[0][3];

      #-----------------------------------------
      # Find out which elements in the dfs2 grid that is not a land value
      # and include all those elements and their surrounding nodes in mesh

      # Arrays indicating if element and node in grid is used or not in mesh
      elmts = np.zeros((xCount, yCount), dtype=bool);
      nodes = np.zeros((xCount + 1, yCount + 1), dtype=np.int32);

      # Loop over all elements in 2D grid
      for l in range(yCount):
        for k in range(xCount):
          # If bathymetry is not land value, use element.
          if (bathymetry[k + l * xCount] != landValue):
            # element [l,k] is used, and also the 4 nodes around it
            elmts[k  , l  ] = True;
            nodes[k  , l  ] = 1;
            nodes[k+1, l  ] = 1;
            nodes[k  , l+1] = 1;
            nodes[k+1, l+1] = 1;
            
      #-----------------------------------------
      # Create new mest nodes

      # Cartography object can convert grid (x,y) to projection (east,north)
      proj = dfs2.FileInfo.Projection;
      cart = Cartography(proj.WKTString, proj.Longitude, proj.Latitude, proj.Orientation);

      # New mesh nodes
      X = [];
      Y = [];
      Zf = [];   # values for dfsu file
      Zd = []; # values for mesh file
      Code = [];

      # Loop over all nodes
      nodesCount = 0;
      for l in range(yCount+1):
        for k in range(xCount+1):
          # Check if node is included in mesh
          if (nodes[k, l] > 0):
            # Convert from mesh (x,y) to projection (east,north)
            east, north = cart.Xy2Proj((k - 0.5) * dx + x0, (l - 0.5) * dy + y0);

            # Average Z on node from neighbouring grid cell values, cell value is used
            # unless they are outside grid or has land values
            z = 0;
            zCount = 0;
            if (k > 0 and l > 0           and bathymetry[k-1 + (l-1) * xCount] != landValue):
              zCount+=1;                 z += bathymetry[k-1 + (l-1) * xCount];
            if (k < xCount and l > 0      and bathymetry[k   + (l-1) * xCount] != landValue):
              zCount+=1;                 z += bathymetry[k   + (l-1) * xCount];
            if (k > 0 and l < yCount      and bathymetry[k-1 + (l  ) * xCount] != landValue):
              zCount+=1;                 z += bathymetry[k-1 + (l  ) * xCount]; 
            if (k < xCount and l < yCount and bathymetry[k   + (l  ) * xCount] != landValue):
              zCount+=1;                 z += bathymetry[k   + (l  ) * xCount]; 

            if (zCount > 0):
              z /= zCount;
            else:
              z = landValue;

            # Store new node number and add node
            nodesCount += 1;
            nodes[k, l] = nodesCount; # this is the node number to use in the element table
            X.append(east);
            Y.append(north);
            Zf.append(z);
            Zd.append(z);
            Code.append(0 if zCount == 4 else 1); # Land boundary if zCount < 4
            
      # New mesh elements
      elmttableList = [];

      for l in range(yCount):
        for k in range(xCount):
          # Check if element is included in mesh
          if (elmts[k, l]):
            # For this element, add the four surrounding nodes,
            # counter-clockwise order
            newNodes = np.zeros(4, dtype=np.int32);
            newNodes[0] = nodes[k  , l  ];
            newNodes[1] = nodes[k+1, l  ];
            newNodes[2] = nodes[k+1, l+1];
            newNodes[3] = nodes[k  , l+1];
            elmttableList.append(newNodes);

      # Copy to np array
      elmttable2 = np.zeros(len(elmttableList), dtype=object);
      for i in range(len(elmttableList)):
        elmttable2[i] = elmttableList[i];
            
#      #-----------------------------------------
#      # Create mesh
#      # Create 2D dfsu file
#      builder = MeshBuilder();
#
#      # Setup header and geometry
#      builder.SetNodes(X.ToArray(), Y.ToArray(), Zd.ToArray(), Code.ToArray());
#      builder.SetElements(elmttable2.ToArray());
#      builder.SetProjection(dfs2.FileInfo.Projection);
#
#      # Create new file
#      mesh = builder.CreateMesh();
#      mesh.Write(meshFilename);

  
      #-----------------------------------------
      # Create dfsu file
      # dfs2 time axis
      timeAxis = dfs2.FileInfo.TimeAxis;

      # Create 2D dfsu file
      builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D);

      # Setup header and geometry
      builder.SetNodes(np.array(X), np.array(Y), np.array(Zf, dtype=np.float32), np.array(Code, dtype=np.int32));
      builder.SetElements(elmttable2);
      builder.SetProjection(dfs2.FileInfo.Projection);
      builder.SetTimeInfo(timeAxis.StartDateTime, timeAxis.TimeStepInSeconds());
      builder.SetZUnit(eumUnit.eumUmeter);

      # Add dynamic items, copying from dfs2 file
      for i in range(len(dfs2.ItemInfo)):
        itemInfo = dfs2.ItemInfo[i];
        builder.AddDynamicItem(itemInfo.Name, itemInfo.Quantity);
    
      # Create new file
      dfsu = builder.CreateFile(dfsuFilename);

      # Add dfs2 data to dfsu file
      dfsuData = np.zeros(dfsu.NumberOfElements, dtype=np.float32);
      for i in range(dfs2.FileInfo.TimeAxis.NumberOfTimeSteps):
        for j in range(len(dfs2.ItemInfo)):
          # Read dfs2 grid data
          itemData = dfs2.ReadItemTimeStep(j + 1, i, reshape=True);
          # Extract 2D grid data to dfsu data array
          lk = 0;
          for l in range(yCount):
            for k in range(xCount):
              if (elmts[k, l]):
                dfsuData[lk] = itemData.Data[k, l];
                lk += 1
          # write data
          dfsu.WriteItemTimeStepNext(itemData.Time, dfsuData);
      dfsu.Close();
  
      dfs2.Close();

    #/ Extract sub-area of dfsu (2D) file to a new dfsu file
    #/ <param name="sourceFilename">Name of source file, i.e. OresundHD.dfsu test file</param>
    #/ <param name="outputFilename">Name of output file</param>
    #/ <param name="x1">Lower left x coordinate of sub area</param>
    #/ <param name="y1">Lower left y coordinate of sub area</param>
    #/ <param name="x2">upper right x coordinate of sub area</param>
    #/ <param name="y2">upper right y coordinate of sub area</param>
    def ExtractSubareaDfsu2D(sourceFilename, outputFilename, x1, y1, x2, y2):

      dfsu = DfsFileFactory.DfsuFileOpen(sourceFilename);

      # Node coordinates
      X = dfsu.X;
      Y = dfsu.Y;
      Z = dfsu.Z;
      Code = dfsu.Code;

      # Loop over all elements, and all its nodes: If one node is inside
      # region, element (and nodes) are to be included in new mesh
      elmtsIncluded = [];
      nodesIncluded = np.zeros(dfsu.NumberOfNodes, dtype=bool);
      for i in range(dfsu.NumberOfElements):
        # Nodes of element
        nodes = dfsu.ElementTable[i];

        # Check if one of the nodes of the element is inside region
        elmtIncluded = False;
        for j in range(nodes.size):
          node = nodes[j] - 1;
          if (x1 <= X[node] and X[node] <= x2 and y1 <= Y[node] and Y[node] <= y2):
            elmtIncluded = True;
    
        if (elmtIncluded):
          # Add element to list of included elements
          elmtsIncluded.append(i);
          # Mark all nodes of element as included
          for j in range(nodes.size):
            node = nodes[j] - 1;
            nodesIncluded[node] = True;
            
      # array containing numbers of existing nodes in new mesh (indices)
      renumber = np.zeros(dfsu.NumberOfNodes, dtype=int);

      # new mesh nodes
      X2 = [];
      Y2 = [];
      Z2 = [];
      Code2 = [];
      nodeIds = [];

      i2 = 0;
      for i in range(dfsu.NumberOfNodes):
        if (nodesIncluded[i]):
          X2.append(X[i]);
          Y2.append(Y[i]);
          Z2.append(Z[i]);
          Code2.append(Code[i]);
          nodeIds.append(dfsu.NodeIds[i]);
          # Node with index i will get index i2 in new mesh
          renumber[i] = i2;
          i2 += 1;
      
      # New mesh elements
      elmttable2 = np.zeros(len(elmtsIncluded), dtype=object);
      elmtIds    = np.zeros(len(elmtsIncluded), dtype=np.int32);
      for i in range(len(elmtsIncluded)):
        # Add new element
        elmt = elmtsIncluded[i];
        nodes = dfsu.ElementTable[elmt];
        # newNodes must be renumbered
        newNodes = np.zeros(nodes.size, dtype=np.int32);
        for j in range(nodes.size):
          # Do the renumbering of nodes from existing mesh to new mesh
          newNodes[j] = renumber[nodes[j] - 1] + 1;
        elmttable2[i] = newNodes;
        elmtIds[i] = dfsu.ElementIds[elmt];
  
      # Create 2D dfsu file
      builder = DfsuBuilder.Create(DfsuFileType.Dfsu2D);

      # Setup header and geometry
      X2    = np.array(X2,    dtype=np.float64)
      Y2    = np.array(Y2,    dtype=np.float64)
      Z2    = np.array(Z2,    dtype=np.float32)
      Code2 = np.array(Code2, dtype=np.int32)

      builder.SetNodes(X2, Y2, Z2, Code2);
      #builder.SetNodeIds(nodeIds.ToArray());
      builder.SetElements(elmttable2);
      builder.SetElementIds(elmtIds); # retain original element id's
      builder.SetProjection(dfsu.Projection);
      builder.SetTimeInfo(dfsu.StartDateTime, dfsu.TimeStepInSeconds);
      if (dfsu.ZUnit == eumUnit.eumUUnitUndefined):
        builder.SetZUnit(eumUnit.eumUmeter);
      else:
        builder.SetZUnit(dfsu.ZUnit);

      # Add dynamic items, copying from source
      for i in range(len(dfsu.ItemInfo)):
        itemInfo = dfsu.ItemInfo[i];
        builder.AddDynamicItem(itemInfo.Name, itemInfo.Quantity);
  
      # Create new file
      dfsuOut = builder.CreateFile(outputFilename);

      # Add new data
      data2 = np.zeros(len(elmtsIncluded), dtype=np.float32);
      for i in range(dfsu.NumberOfTimeSteps):
        for j in range(len(dfsu.ItemInfo)):
          # Read data from existing dfsu
          itemData = dfsu.ReadItemTimeStep(j + 1, i);
          # Extract value for elements in new mesh
          for k in range(len(elmtsIncluded)):
            data2[k] = itemData.Data[elmtsIncluded[k]];
          # write data
          dfsuOut.WriteItemTimeStepNext(itemData.Time, data2);
      dfsuOut.Close();
      dfsu.Close();
