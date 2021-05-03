from mikecore.DfsFactory import DfsFactory
from mikecore.DfsBuilder import DfsBuilder
from mikecore.DfsuFile import DfsuFile, DfsuFileType, DfsSimpleType, DataValueType, DfsuUtil
from mikecore.eum import eumUnit, eumQuantity, eumItem
import numpy as np

  #/ <summary>
  #/ Builder for creating a dfsu file.
  #/ <para>
  #/ The following must be set before calling <see cref="CreateFile"/>:
  #/ <see cref="SetProjection"/>,
  #/ <see cref="SetTimeInfo"/>,
  #/ <see cref="SetNodes(double[],double[],float[],int[])"/>,
  #/ <see cref="SetElements"/>.
  #/ </para>
  #/ <para>
  #/ For files with a vertical dimension, the <see cref="SetNumberOfSigmaLayers"/> must also be set.
  #/ </para>
  #/ <para>
  #/ Other setters are optional, and if not set, default values are written to the file.
  #/ </para>
  #/ <para>
  #/ Using the <see cref="SetFromMeshFile"/> will set the projection, nodes
  #/ and elements from the mesh file.
  #/ </para>
  #/ <para>
  #/ Be aware; setting the node and element id's to anything but the default
  #/ values can cause some tools to fail.
  #/ </para>
  #/ </summary>
class DfsuBuilder:
    def __init__(self, dfsuFileType):
      self.__isSetProjection = False
      self.__isSetTimeInfo = False
      self.__isSetNodes = False
      self.__isSetConnectivity = False
      self.__isSetNumberOfSigmaLayers = False

      self.__dfsuFileType = dfsuFileType
      self.__numberOfSigmaLayers = -1

      # Projection variables
      self.__dfsProjection = None

      # Time variables
      self.__timeAxis = None
      self.__startDateTime = None
      self.__timeStepInSeconds = -1
      self.__numberOfTimeSteps = -1

      # Node variables
      self.__nodeIds = None # this can be null, then set default id's, starting from 1
      self.__x = None
      self.__y = None
      self.__z = None
      self.__code = None
      self.__zUnit = eumUnit.eumUmeter
      self.__zQuantity = None

      # Element variables
      self.__connectivity = None
      self.__elementIds = None # this can be null, then set default id's, starting from 1

      # Dynamic item information
      self.__dynamicItemData = []

      self.__dfsuFileType = dfsuFileType
      if   dfsuFileType == DfsuFileType.Dfsu2D:
          self.FileTitle = "Area Series"
      elif dfsuFileType == DfsuFileType.DfsuVerticalColumn:
          self.FileTitle = "Vertical column series"
      elif dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma:
          self.FileTitle = "2D vertical profile series"
      elif dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ:
          self.FileTitle = "2D vertical profile series"
      elif dfsuFileType == DfsuFileType.Dfsu3DSigma:
          self.FileTitle = "3D volume series"
      elif dfsuFileType == DfsuFileType.Dfsu3DSigmaZ:
          self.FileTitle = "3D volume series"
      else:
          self.FileTitle = "Area Series"
      self.ApplicationTitle = ""
      self.ApplicationVersion = 0


    def SetProjection(self, projection):
      """Set the geographical projection"""
      if (projection is None):
        raise Exception("projection")
      self.__dfsProjection = projection
      self.__isSetProjection = True

    #/ <summary>
    #/ Set the number of sigma layers in a file with a vertical dimension
    #/ </summary>
    #/ <remarks>
    #/ If called with a <see cref="DfsuFileType"/> that does not have any
    #/ vertical dimension, an <see cref="InvalidOperationException"/> is thrown.
    #/ </remarks>
    def SetNumberOfSigmaLayers(self, numberOfSigmaLayers):
      if self.__dfsuFileType == DfsuFileType.Dfsu2D:
          raise Exception("Can not set number of sigma layers on a 2D dfsu file")
      elif (self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn # strictly speaking not required, but anyway...
            or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma
            or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ
            or self.__dfsuFileType == DfsuFileType.Dfsu3DSigma
            or self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ):
          self.__numberOfSigmaLayers = numberOfSigmaLayers
          self.__isSetNumberOfSigmaLayers = True
      else:
          raise Exception("dfsuFileType")

    #/ <summary>
    #/ Set a non-standard temporal axis for the dfsu file. WARNING: The dfsu file will not be valid in all contexts.
    #/ <para>
    #/ The standard dfsu file requires an <see cref="IDfsEqCalendarAxis"/> temporal axis.
    #/ You can use the <see cref="SetTimeInfo"/> method to define a valid <see cref="IDfsEqCalendarAxis"/>
    #/ axis for the dfsu file.
    #/ </para>
    #/ <para>
    #/ If you define another temporal axis than the <see cref="IDfsEqCalendarAxis"/> for a dfsu file,
    #/ be sure to test that the file works as intended in your context.
    #/ </para>
    #/ </summary>
    def SetTemporalAxis(self, timeAxis):
      self.__timeAxis = timeAxis
      self.__isSetTimeInfo = True

    def SetTimeInfo(self, startDateTime, timeStepInSeconds):
      """Set time info, specifying an equidistant calendar axis, which is the default (always valid) temporal axis of a dfsu file."""
      self.__startDateTime = startDateTime
      self.__timeStepInSeconds = timeStepInSeconds
      self.__isSetTimeInfo = True

    #/ <summary>
    #/ Sets the number of time steps in the file.
    #/ <para>
    #/ This is only required in streaming context, where it is not possible
    #/ to update the dfs header when everything is written to the file. 
    #/ In a non-streaming context this should not be used.
    #/ </para>
    #/ <para>
    #/ This is a stage 1 method.
    #/ </para>
    #/ </summary>
    def SetNumberOfTimeSteps(self, numberOfTimeSteps):
      self.__numberOfTimeSteps = numberOfTimeSteps

    def SetNodes(self, x, y, z, code):
      """Set node coordinates and code. Depending on the projection string, 
         node coordinates are in meters or degrees
      """
      if (x is None):
        raise Exception("x")
      if (y is None):
        raise Exception("y")
      if (z is None):
        raise Exception("z")
      if (code is None):
        raise Exception("code")

      if (x.dtype == np.float32):
        x = np.array(x, dtype=np.float64)
      if (y.dtype == np.float32):
        y = np.array(y, dtype=np.float64)

      numberOfNodes = x.size

      if (numberOfNodes != y.size or numberOfNodes != z.size or numberOfNodes != code.size):
          raise Exception(f"All arguments must have same length. Lengths are: x={x.size}, y={y.size}, z={z.size}, code={code.size}")

      if (self.__nodeIds != None and numberOfNodes != self.__nodeIds.size):
        raise Exception("Arguments does not have same length as the number of node ids. These must match")

      self.__x = x
      self.__y = y
      self.__z = z
      self.__code = code
      self.__isSetNodes = True


    #/ <inheritdoc/>
    def SetZUnit(self, zUnit):
      # TODO: Fix!
      if (zUnit != eumUnit.eumUmeter 
          and zUnit != eumUnit.eumUfeet
          and zUnit != eumUnit.eumUUnitUndefined):
          raise Exception("Currently only meter and feet unit is supported")
      self.__zUnit = zUnit
      #if (EUMWrapper.eumUnitsEqv(eumUnit.eumUmeter, zUnit)):
      #  self.__zUnit = zUnit
      #else:
      #  raise Exception("Unit of z coordinate is not a length unit")

    def SetNodeIds(self, nodeIds):
      """Set the node id's. Optional. If not set, default values are used (1,2,3,...)"""
      if (nodeIds is None):
        self.__nodeIds = None
        return
      if (self.__x != None and self.__x.size != nodeIds.size):
        raise Exception("Number of node id's does not match number of nodes", "nodeIds")
      self.__nodeIds = nodeIds

    def SetElements(self, connectivity):
      """Set element connectivity: For each element is specified which nodes
         the element consist of. The node is specified by its index into the list of nodes.
      """
      if (connectivity is None):
        raise Exception("connectivity")
      if (connectivity.size == 0):
        raise Exception("Element table has no rows. There must be at least one row")

      if (self.__elementIds != None and self.__elementIds.size != connectivity.size):
        raise Exception("Number of elements is not the same as number of element ids. They must match")

      # Validate that element numbers are ok.
      if self.__dfsuFileType == DfsuFileType.Dfsu2D:
            # Check number of elements
            for i in range(connectivity.size):
              elmnt = connectivity[i]
              if (3 > elmnt.size or elmnt.size > 4):
                raise Exception(f"All elements must have 3 or 4 nodes. Element number {i + 1} has {elmnt.size} nodes")
      elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigma:
            # Check number of elements
            for i in range(connectivity.size):
              elmnt = connectivity[i]
              if (elmnt.size != 6 and elmnt.size != 8):
                  raise Exception(f"All elements must have 6 or 8 nodes. Element number {i + 1} has {elmnt.size} nodes")

      self.__connectivity = connectivity
      self.__isSetConnectivity = True

    def SetElementIds(self, elementIds):
      """Set the element id's. Optional. If not set, default values are used (1,2,3,...)"""
      if (self.__connectivity != None and self.__connectivity.size != elementIds.size):
          raise Exception("Number of element id's does not match number of elements", "elementIds")

    def SetFromMeshFile(self, meshFile):
      """Set projection, nodes and elements from mesh file.
      This is equivalent to calling SetProjection, SetNodes, SetElements
      """
      self.__dfsProjection = DfsProjection.Create(meshFile.ProjectionString)
      self.__isSetProjection = True

      self.__nodeIds = meshFile.NodeIds
      self.__x = meshFile.X
      self.__y = meshFile.Y
      self.__z = MeshBuilder.Convert(meshFile.Z)
      self.__code = meshFile.Code
      self.__zUnit = meshFile.EumQuantity.Unit
      self.__isSetNodes = True

      self.__elementIds = meshFile.ElementIds
      self.__connectivity = meshFile.ElementTable
      self.__isSetConnectivity = True

    def AddDynamicItem(self, itemName, quantity):
      """Add a dynamic item. """
      self.__dynamicItemData.append((itemName, quantity))

    def Validate(self, dieOnError = False):
      """Validate will return a string of issues from the item builder.
      When this returns an empty list, the item has been properly build.
      """
      errors = []

      if (not self.__isSetProjection):
        errors.append("Projection has not been set")
      if (not self.__isSetTimeInfo):
        errors.append("Time information has not been set")
      if (not self.__isSetNodes):
        errors.append("Nodes have not been set")
      if (not self.__isSetConnectivity):
        errors.append("Elements have not been set")
      if (not self.__isSetNumberOfSigmaLayers and self.__dfsuFileType != DfsuFileType.Dfsu2D):
        errors.append("Number of sigma layers has not been set")

      # Check that all nodenumbers are within the range of
      # number of nodes.
      check = True
      for elmt in self.__connectivity:
        for nodeNumber in elmt:
          if (0 >= nodeNumber or nodeNumber > self.__x.size):
            check = False
            break
        if (not check):
          break
      if (not check):
        errors.append("At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]")

      # For vertical files, checking that elements are correctly on top of each other, 
      # and calculate the maxNumberOfLayers
      # TODO: Need to check that node coordinates are also on top of each other?
      # TODO: Need to check that the 2D elements are defined counter-clockwise
      if self.__dfsuFileType == DfsuFileType.Dfsu2D:
          pass
      elif self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn:
            topLayerElements = DfsuUtil.FindTopLayerElements(self.__connectivity)
            if (len(topLayerElements) != 1):
              errors.append("Elements does not seem to be on top of each other. Element table is invalid")
      elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma:
            topLayerElements = DfsuUtil.FindTopLayerElements(self.__connectivity)
            maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(topLayerElements)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if (maxNumberOfLayers != self.__numberOfSigmaLayers or minNumberOfLayers != self.__numberOfSigmaLayers):
              errors.append("The number of layers does not everywhere equal the number of sigma layers. Element table is invalid")
      elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ:
            topLayerElements = DfsuUtil.FindTopLayerElements(self.__connectivity)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if (minNumberOfLayers < self.__numberOfSigmaLayers):
              errors.append("The minimum number of layers is smaller than the number of sigma layers. Element table is invalid")
      elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigma:
            topLayerElements = DfsuUtil.FindTopLayerElements(self.__connectivity)
            maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(topLayerElements)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if (maxNumberOfLayers != self.__numberOfSigmaLayers or minNumberOfLayers != self.__numberOfSigmaLayers):
              errors.append("The number of layers does not everywhere equal the number of sigma layers. Element table is invalid")
      elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ:
            topLayerElements = DfsuUtil.FindTopLayerElements(self.__connectivity)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if (minNumberOfLayers < self.__numberOfSigmaLayers):
              errors.append("The minimum number of layers is smaller than the number of sigma layers. Element table is invalid")
      else:
          raise Exception(f"Dfsu file type {self.__dfsuFileType} not supported")


      if (dieOnError and len(errors) > 0):
        msgs = DfsBuilder.ErrorMessage(errors)
        raise Exception(msgs)

      return (errors)

    def SetupConnectivityArrays(self):
      # Creating default node id's, if empty
      if (self.__nodeIds is None):
          # Setting node ids 1,2,3,...
        self.__nodeIds = np.zeros(self.__x.size, dtype=np.int32)
        for i in range(self.__x.size):
              self.__nodeIds[i] = i + 1
        # Creating default element id's, if empty
      if (self.__elementIds is None):
          # Setting element ids 1,2,3,...
        self.__elementIds = np.zeros(self.__connectivity.size, dtype=np.int32)
        for i in range(self.__connectivity.size):
              self.__elementIds[i] = i + 1
  
      # Creating additional element information
      elementType = np.zeros(self.__connectivity.size, dtype=np.int32)
      nodesPerElmt = np.zeros(self.__connectivity.size, dtype=np.int32)
      nodeElmtCount = 0 # total number of nodes listed in the connectivity table
      for i in range(elementType.size):
        elmt = self.__connectivity[i]
        elmtsize = elmt.size
        if   elmtsize == 2: # vertical column
            elmtTypeNumber = 11
        elif elmtsize == 3: # triangle
            elmtTypeNumber = 21
        elif elmtsize == 4: # quadrilateral
            elmtTypeNumber = 25
        elif elmtsize == 6: # prisme (base element is a triangle)
            elmtTypeNumber = 32
        elif elmtsize == 8: # Hexahedron (base element is a quadrilateral)
            elmtTypeNumber = 33
        else:
            # this should have been caught in the validate phase, but just in case:
            raise Exception("Element with invalid number of nodes encountered")
        elementType[i] = elmtTypeNumber
        nodesPerElmt[i] = elmt.size
        nodeElmtCount += elmt.size

      connectivityArray = np.zeros(nodeElmtCount, dtype=np.int32)
      k = 0
      for i in range(elementType.size):
        elmt = self.__connectivity[i]
        for j in range (elmt.size):
           connectivityArray[k] = elmt[j]
           k += 1

      return elementType, nodesPerElmt, connectivityArray
  
    def SetupBuilder(self):
      self.__zQuantity = eumQuantity(eumItem.eumIItemGeometry3D, self.__zUnit)

      factory = DfsFactory()
      dfsBuilder = DfsBuilder.Create(self.FileTitle, self.ApplicationTitle, self.ApplicationVersion)

      dfsBuilder.SetDataType(2001)
      dfsBuilder.SetGeographicalProjection(self.__dfsProjection)
      if (self.__timeAxis != None):
        dfsBuilder.SetTemporalAxis(self.__timeAxis)
      else:
        dfsBuilder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, self.__startDateTime, 0, self.__timeStepInSeconds))
      dfsBuilder.DeleteValueFloat = np.float32(1e-35)

      # Set up custom block
      if self.__dfsuFileType == DfsuFileType.Dfsu2D:
          dfsBuilder.AddCreateCustomBlock("MIKE_FM",np.array([ self.__x.size, self.__connectivity.size, 2, 0, 0 ], np.int32))
      elif self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn:
          maxNumberOfLayers = self.__connectivity.size
          dfsBuilder.AddCreateCustomBlock("MIKE_FM",np.array([ self.__x.size, self.__connectivity.size, 1, maxNumberOfLayers, self.__numberOfSigmaLayers ], np.int32))
      elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma:
          maxNumberOfLayers = self.__numberOfSigmaLayers
          dfsBuilder.AddCreateCustomBlock("MIKE_FM",np.array([ self.__x.size, self.__connectivity.size, 2, maxNumberOfLayers, self.__numberOfSigmaLayers ], np.int32))
      elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ:
          maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(DfsuUtil.FindTopLayerElements(self.__connectivity))
          dfsBuilder.AddCreateCustomBlock("MIKE_FM",np.array([ self.__x.size, self.__connectivity.size, 2, maxNumberOfLayers, self.__numberOfSigmaLayers ], np.int32))
      elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigma:
          maxNumberOfLayers = self.__numberOfSigmaLayers
          dfsBuilder.AddCreateCustomBlock("MIKE_FM",np.array([ self.__x.size, self.__connectivity.size, 3, maxNumberOfLayers, self.__numberOfSigmaLayers ], np.int32))
      elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ:
          maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(DfsuUtil.FindTopLayerElements(self.__connectivity))
          dfsBuilder.AddCreateCustomBlock("MIKE_FM",np.array([ self.__x.size, self.__connectivity.size, 3, maxNumberOfLayers, self.__numberOfSigmaLayers ], np.int32))
      else:
          raise Exception()

      # For the files with a vertical dimension, the first dynamic item is the Z-coordinate
      if (  self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn
         or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma
         or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ
         or self.__dfsuFileType == DfsuFileType.Dfsu3DSigma
         or self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ):
          dfsItem = dfsBuilder.CreateDynamicItemBuilder()
          dfsItem.Set("Z coordinate", self.__zQuantity, DfsSimpleType.Float)
          dfsItem.SetValueType(DataValueType.Instantaneous)
          # Disabled to make the dfsu files exactly match those from the engine. Not necessary, 
          # but enables binary compares
          #if (false):
          #  dfsItem.SetAxis(factory.CreateAxisDummy(self.__connectivity.size))
          #else
            # Set axis to have meter unit (not necessary, just to make file exactly equal)
          dfsItem.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, self.__x.size, 0, 1))
          # Set to default ufs delete values (not used anyway, just to make file exactly equal)
          dfsItem.SetReferenceCoordinates(-1e-35, -1e-35, -1e-35)
          dfsItem.SetOrientation(-1e-35, -1e-35, -1e-35)
          dfsBuilder.AddDynamicItem(dfsItem.GetDynamicItemInfo())

      # Set up dynamic items
      for i in range(len(self.__dynamicItemData)):
        itemData = self.__dynamicItemData[i]
        dfsItem = dfsBuilder.CreateDynamicItemBuilder()
        dfsItem.Set(itemData[0], itemData[1], DfsSimpleType.Float)
        dfsItem.SetValueType(DataValueType.Instantaneous)
        # Disabled to make the dfsu files exactly match those from the engine. Not necessary, 
        # but enables binary compares
        #if (false):
        #  dfsItem.SetAxis(factory.CreateAxisDummy(self.__connectivity.size))
        #else
          # Set axis to have meter unit (not necessary, just to make file exactly equal)
        dfsItem.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, self.__connectivity.size, 0, 1))
        # Set to default ufs delete values (not used anyway, just to make file exactly equal)
        dfsItem.SetReferenceCoordinates(-1e-35, -1e-35, -1e-35)
        dfsItem.SetOrientation(-1e-35, -1e-35, -1e-35)
        dfsBuilder.AddDynamicItem(dfsItem.GetDynamicItemInfo())
      return dfsBuilder

    def CreateFile(self, filename):
      """Create and return a dfsu file"""

      self.Validate(True)
      elementType, nodesPerElmt, connectivityArray = self.SetupConnectivityArrays()
      dfsBuilder = self.SetupBuilder()
      dfsBuilder.CreateFile(filename)

      return self.CreateDfsu(dfsBuilder, elementType, nodesPerElmt, connectivityArray)


    def CreateDfsu(self, dfsBuilder, elementType, nodesPerElmt, connectivityArray):
      # Add static items
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

      intCode = eumQuantity(eumItem.eumIIntegerCode, eumUnit.eumUintCode)
      xyQuantity = eumQuantity(eumItem.eumIGeographicalCoordinate, eumUnit.eumUmeter)
      # TODO: reenable:
      #if (MapProjection.IsValid(self.__dfsProjection.WKTString)):
      #    if (MapProjection.IsGeographical(self.__dfsProjection.WKTString)):
      #        xyQuantity = eumQuantity(eumItem.eumILatLong, eumUnit.eumUdegree)
      
      # Node id
      nodeIdItem = dfsBuilder.AddCreateStaticItem("Node id", intCode, self.__nodeIds)

      # X-coord
      xItem = dfsBuilder.AddCreateStaticItem("X-coord", xyQuantity, self.__x)

      # Y-coord
      yItem = dfsBuilder.AddCreateStaticItem("Y-coord", xyQuantity, self.__y)

      # Z-coord
      zItem = dfsBuilder.AddCreateStaticItem("Z-coord", self.__zQuantity, self.__z)

      # Code
      codeItem = dfsBuilder.AddCreateStaticItem("Code", intCode, self.__code)

      # Element id
      elmtIdItem = dfsBuilder.AddCreateStaticItem("Element id", intCode, self.__elementIds)

      # Element type
      elmtTypeItem = dfsBuilder.AddCreateStaticItem("Element type", intCode, elementType)

      # No of nodes (per element)
      nodesPerElmtItem = dfsBuilder.AddCreateStaticItem("No of nodes", intCode, nodesPerElmt)

      # Connectivity
      connectivityItem = dfsBuilder.AddCreateStaticItem("Connectivity", intCode, connectivityArray)

      dfsFile = dfsBuilder.GetFile()

      dfsuFile = DfsuFile()
      dfsuFile.DfsuFileBuild(
        dfsFile,
        nodeIdItem,
        xItem,
        yItem,
        zItem,
        codeItem,
        elmtIdItem,
        self.__nodeIds,
        self.__x,
        self.__y,
        self.__z,
        self.__code,
        self.__elementIds,
        elementType,
        self.__connectivity,
        self.__zUnit
      )

      return (dfsuFile)

    @staticmethod
    def Create(fileType):
      """Create a new dfsu builder"""
      return (DfsuBuilder(fileType))
