import datetime
import numpy as np
from mikecore.eum import *
from mikecore.DfsFile import *

def CheckForNull(obj):
  if (obj == None):
    raise Exception("File is not a valid dfsu file. It can not be opened");

class DfsuFileType(IntEnum):

    # 2D area series
    Dfsu2D = 1,

    # 1D vertical column
    DfsuVerticalColumn = 2,

    # 2D vertical slice through a Dfsu3DSigma
    DfsuVerticalProfileSigma = 3,

    # 2D vertical slice through a Dfsu3DSigmaZ
    DfsuVerticalProfileSigmaZ = 4,

    # 3D file with sigma coordinates, i.e., a constant number of layers.
    Dfsu3DSigma = 5,

    # 3D file with sigma and Z coordinates, i.e. a varying number of layers.
    Dfsu3DSigmaZ = 6,

class DfsuFile(object):
    """
    Class for exposing data from a dfsu file. 

    Use the DfsFileFactory to open an existing dfsu file.

    Use the DfsuBuilder to create a new dfsu file.

    You can read, write and append item-timesteps to the file. 

    The geometry can be altered, by moving the nodes, but the element connectivity can not be changed.
    """

    def __init__(self, dfsFile = None):
        # underlying dfs file
        self.dfsFile = dfsFile;
        self.DfsuFileType = DfsuFileType.Dfsu2D;
        self.NumberOfLayers = -1;
        self.NumberOfSigmaLayers = -1;

        # Static item
        self.__nodeIdItem = None;
        self.__xItem = None;
        self.__yItem = None;
        self.__zItem = None;
        self.__codeItem = None;

        self.__elmtIdItem = None;

        # Node variables
        self.NodeIds = None;
        self.X = None;
        self.Y = None;
        self.Z = None;
        self.Code = None;

        self.ZUnit = eumUnit.eumUmeter;

        # Element variables
        self.ElementIds = None; # this can be null, then set default id's, starting from 1
        self.ElementType = None;
        self.ElementTable = [];

        if (not dfsFile is None):
            self.__Init(dfsFile)

    def __Init(self, dfsFile, build = False):
      """
      Wrap a dfs file in the DfsuFile object.
      It will throw an exception if file is not a dfsu file.
      """

      self.dfsFile = dfsFile;
      self.FileInfo  = self.dfsFile.FileInfo

      # Build geometry

      # Read "MIKE_FM" custom block
      if (len(self.dfsFile.FileInfo.CustomBlocks) != 1 
          or not self.dfsFile.FileInfo.CustomBlocks[0].Name ==  "MIKE_FM"):
          raise Exception("Error while reading dfsu file (custom block 'MIKE_FM' missing)");

      customBlock = self.dfsFile.FileInfo.CustomBlocks[0];
      if (customBlock is None or customBlock.Count < 4 or customBlock.SimpleType != DfsSimpleType.Int):
          raise Exception("Error while reading dfsu file (custom block not valid)");

      #int numberOfNodes = customBlock[0];
      numberOfElmts = customBlock[1];

      dimensions = customBlock[2];
      self.NumberOfLayers = customBlock[3];
      if (customBlock.Count == 5):
        self.NumberOfSigmaLayers = customBlock[4];
      else:
        self.NumberOfSigmaLayers = self.NumberOfLayers;

      # Figuring out dfsu file type from custom block MIKE_FM
      if (dimensions == 1):
        self.DfsuFileType = DfsuFileType.DfsuVerticalColumn;
      elif (dimensions == 2):
        if (self.NumberOfLayers == 0):
          self.DfsuFileType = DfsuFileType.Dfsu2D;
        elif (self.NumberOfLayers == self.NumberOfSigmaLayers):
          self.DfsuFileType = DfsuFileType.DfsuVerticalProfileSigma;
        else:
          self.DfsuFileType = DfsuFileType.DfsuVerticalProfileSigmaZ;
 
      elif (dimensions == 3):

        if (self.NumberOfLayers == self.NumberOfSigmaLayers):
          self.DfsuFileType = DfsuFileType.Dfsu3DSigma;
        else:
          self.DfsuFileType = DfsuFileType.Dfsu3DSigmaZ;


      # Do not read static items when building, they are already set
      if (not build):
          # "Node id"       , int
          # "X-coord"       , double/float
          # "Y-coord"       , double/float
          # "Z-coord"       , float (prepared for reading doubles)
          # "Code"          , int
          # "Element id"    , int
          # "Element type"  , int
          # "No of nodes"   , int
          # "Connectivity"  , int

          self.__nodeIdItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(self.__nodeIdItem);
          self.NodeIds = self.__nodeIdItem.Data

          # X can be in doubles or in floats. Floats are converted to doubles
          self.__xItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(self.__xItem);
          if (self.__xItem.DataType == DfsSimpleType.Double):
            self.X = self.__xItem.Data
          else: # self.__xItem.DataType == DfsSimpleType.Float 
            floats = self.__xItem.Data;
            self.X = np.array(floats, np.double);


          # Y can be in doubles or in floats. Floats are converted to doubles
          self.__yItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(self.__yItem);
          if (self.__yItem.DataType == DfsSimpleType.Double):
            self.Y = self.__yItem.Data
          else: # self.__yItem.DataType == DfsSimpleType.Double
            floats = self.__yItem.Data;
            self.Y = np.array(floats, np.double);

          # Z is stored as float. Doubles are also read, but converted to floats ("future" support of doubles)
          self.__zItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(self.__zItem);
          if (self.__zItem.DataType == DfsSimpleType.Float):
            self.Z = self.__zItem.Data
          else: # self.__zItem.DataType == DfsSimpleType.Double
            doubles = self.__zItem.Data;
            self.Z = np.array(doubles, np.float32);

          self.ZUnit = self.__zItem.Quantity.Unit;

          self.__codeItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(self.__codeItem);
          self.Code = self.__codeItem.Data

          self.__elmtIdItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(self.__elmtIdItem);
          self.ElementIds = self.__elmtIdItem.Data

          elmtTypeItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(elmtTypeItem);
          self.ElementType = elmtTypeItem.Data

          nodesPerElmtItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(nodesPerElmtItem);
          nodesPerElement = nodesPerElmtItem.Data

          connectivityItem = self.dfsFile.ReadStaticItemNext(); CheckForNull(connectivityItem);
          connectivityArray = connectivityItem.Data

          # TODO Validate data

          self.ElementTable = np.empty(numberOfElmts,dtype=object);
          k = 0;
          for i in range(numberOfElmts):
            nodesInElement = nodesPerElement[i];
            self.ElementTable[i] = np.empty(nodesInElement,dtype=np.int32);
            for j in range(nodesInElement):
              self.ElementTable[i][j] = connectivityArray[k];
              k += 1

      self.NumberOfNodes = self.NodeIds.size; 
      self.ItemInfo = self.dfsFile.ItemInfo

      self.NumberOfElements = self.ElementIds.size
      #self.NumberOfNodes = self.X.size

      if (not build):
         # In append mode, move the file pointer to end of file
         # It was moved elsewhere when reading static data...
         if (self.dfsFile.FileMode == DfsFileMode.Append):
            self.dfsFile.FindTimeStep(self.NumberOfTimeSteps);


    def Dispose(self):
      """
      Close file and release ressources on the unmanaged side.
      """

      self.dfsFile.Dispose();

    def ReadItemTimeStepNext(self):
      return (self.dfsFile.ReadItemTimeStepNext());

    def ReadItemTimeStep(self, itemNumber, timestepIndex):
      return (self.dfsFile.ReadItemTimeStep(itemNumber, timestepIndex));

#    def ReadItemTimeStep(itemData, timestepIndex)
#      return (self.dfsFile.ReadItemTimeStep(itemData, timestepIndex));

    def WriteItemTimeStep(self, itemNumber, timestepIndex, time, data):
      self.dfsFile.WriteItemTimeStep(itemNumber, timestepIndex, time, data);

    def WriteItemTimeStepNext(self, time, data):
      self.dfsFile.WriteItemTimeStepNext(time, data);


    def FindItem(self, itemNumber, timestepIndex):
      self.dfsFile.FindItem(itemNumber, timestepIndex);

    def FindTimeStep(self, timestepIndex):
      self.dfsFile.FindTimeStep(timestepIndex);

    def Reset(self):
      self.dfsFile.Reset();

    def Flush(self):
       self.dfsFile.Flush(self);

    def FlushTimeStep(self):
       self.dfsFile.FlushTimeStep();

    def Close(self):
       self.dfsFile.Close();

    @staticmethod
    def Open(fileName):
      dfs = DfsFile();
      dfs.Open(fileName, DfsFileMode.Read);
      return (DfsuFile(dfs));

    @staticmethod
    def OpenEdit(fileName):
      dfs = DfsFile();
      dfs.Open(fileName, DfsFileMode.Edit);
      return (DfsuFile(dfs));

    @staticmethod
    def OpenAppend(fileName):
      dfs = DfsFile();
      dfs.Open(fileName, DfsFileMode.Append);
      return (DfsuFile(dfs));

      """
      Internal factory method, used by the DfsuBuilder
      """
    def DfsuFileBuild(
      self,
      dfsFile,
      nodeIdItem,
      xItem,
      yItem,
      zItem,
      codeItem,
      elmtIdItem,
      nodeIds,
      x,
      y,
      z,
      code,
      elementIds,
      elementType,
      connectivity,
      zUnit
      ):

      self.dfsFile = dfsFile;
      self.__nodeIdItem = nodeIdItem;
      self.__xItem = xItem;
      self.__yItem = yItem;
      self.__zItem = zItem;
      self.__codeItem = codeItem;
      self.__elmtIdItem = elmtIdItem;
      self.NodeIds = nodeIds;
      self.X = x;
      self.Y = y;
      self.Z = z;
      self.Code = code;
      self.ElementIds = elementIds;
      self.ElementType = elementType;
      self.ElementTable = connectivity;
      self.ZUnit = zUnit;
      self.__Init(dfsFile, build = True)


    def __GetFileName(self):
        return self.FileInfo.FileName
    def __SetFileName(self, value: str):
        self.FileInfo.FileName = value
    FileName = property(__GetFileName, __SetFileName)

    def __GetFileTitle(self):
        return self.FileInfo.FileTitle
    def __SetFileTitle(self, value: str):
        self.FileInfo.FileTitle = value
    FileTitle = property(__GetFileTitle, __SetFileTitle)

    def __GetApplicationTitle(self):
        return self.FileInfo.ApplicationTitle
    def __SetApplicationTitle(self, value):
        self.FileInfo.ApplicationTitle = value
    ApplicationTitle = property(__GetApplicationTitle, __SetApplicationTitle)

    def __GetApplicationVersion(self):
        return self.FileInfo.ApplicationVersion
    def __SetApplicationVersion(self, value):
        self.FileInfo.ApplicationVersion = value
    ApplicationVersion = property(__GetApplicationVersion, __SetApplicationVersion)

    def __GetProjection(self) -> DfsProjection:
        return self.FileInfo.Projection
    def __SetProjection(self, value: DfsProjection):
        self.FileInfo.Projection = value
    Projection = property(__GetProjection, __SetProjection)

    def __GetTimeAxis(self):
        return self.FileInfo.TimeAxis
#    def __SetTimeAxis(self, value):
#        self.FileInfo.TimeAxis = value
    TimeAxis = property(__GetTimeAxis)

    def __GetStartDateTime(self):
        return self.FileInfo.TimeAxis.StartDateTime
    def __SetStartDateTime(self, value):
        self.FileInfo.TimeAxis.StartDateTime = value
    StartDateTime = property(__GetStartDateTime, __SetStartDateTime)

    def __GetTimeStepInSeconds(self):
        return self.dfsFile.FileInfo.TimeAxis.TimeStepInSeconds() if self.dfsFile.FileInfo.TimeAxis.IsEquidistant() else -1
#    def __SetTimeStepInSeconds(self, value):
#        self.FileInfo.TimeStepInSeconds = value
#    TimeStepInSeconds = property(__GetTimeStepInSeconds, __SetTimeStepInSeconds)
    TimeStepInSeconds = property(__GetTimeStepInSeconds)

    def __GetNumberOfTimeSteps(self):
        return self.FileInfo.TimeAxis.NumberOfTimeSteps
    
    @property
    def NumberOfTimeSteps(self):
      return self.__GetNumberOfTimeSteps()

    def __GetDeleteValueFloat(self):
        return self.FileInfo.DeleteValueFloat
    def __SetDeleteValueFloat(self, value):
        self.FileInfo.DeleteValueFloat = value
    DeleteValueFloat = property(__GetDeleteValueFloat, __SetDeleteValueFloat)



    @staticmethod
    def CreateEmptyItemDatas(dfsFile: DfsFile):
      """
      Create an <see cref="IDfsItemData{T}"/> of the provided type for each of the
      dynamic items in the file.
      <para>
      The result can be used by <see cref="IDfsFileIO.ReadItemTimeStep(DHI.Generic.MikeZero.DFS.IDfsItemData,int)"/>
      </para>
      <para>
      If not all items are of type {T}, an exception will be thrown.
      </para>
      """
      res = np.zeros(len(dfsFile.ItemInfo), dtype=object);
      for i in range(len(dfsFile.ItemInfo)):
        res[i] = dfsFile.ItemInfo[i].CreateEmptyItemData();
      return res;

    def CalculateElementCenterCoordinates(self):
      """"
      For each element, calculates the element center coordinate
      as the average of all node coordinates of the nodes in 
      each element.
      """
      xArr = np.zeros(self.NumberOfElements, dtype=np.float64);
      yArr = np.zeros(self.NumberOfElements, dtype=np.float64);
      zArr = np.zeros(self.NumberOfElements, dtype=np.float64);

      for i in range(self.NumberOfElements):
        nodesInElmt = self.ElementTable[i].size;
        iNodesInElmt = 1.0/nodesInElmt;
        x = 0;
        y = 0;
        z = 0;
        for j in range(nodesInElmt):
          nodeIndex = self.ElementTable[i][j];
          x += self.X[nodeIndex -1] * iNodesInElmt;
          y += self.Y[nodeIndex -1] * iNodesInElmt;
          z += self.Z[nodeIndex -1] * iNodesInElmt;
        xArr[i] = x;
        yArr[i] = y;
        zArr[i] = z;
      return xArr, yArr, zArr

    def GetDateTimes(self):
      """"
      Return an array of DateTimes which are the times for each timestep
      """
      res = np.zeros(self.NumberOfTimeSteps, dtype=datetime.datetime);
      start = self.StartDateTime;
      timestepInSecs = self.TimeStepInSeconds;
      for i in range(self.NumberOfTimeSteps):
        res[i] = start + datetime.timedelta(seconds=i*timestepInSecs);
      return (res);

    def FindTopLayerElements(self):
      if (self.DfsuFileType == DfsuFileType.Dfsu2D):
        raise Exception("Can not extract top layer elements of a 2D dfsu file");

      return DfsuUtil.FindTopLayerElements(self.ElementTable)

    """"
    Utility and extension methods for <see cref="DfsuFile"/>
    """
class DfsuUtil:

    @staticmethod
    def FindTopLayerElements(elementTable):
      """
      Find element indices (zero based) of the elements being the upper-most element
      in its column.

      Each column is identified by matching node id numbers. For 3D elements the
      last half of the node numbers of the bottom element must match the first half
      of the node numbers in the top element. For 2D vertical elements the order of 
      the node numbers in the bottom element (last half number of nodes) are reversed 
      compared to those in the top element (first half number of nodes).

      To find the number of elements in each column, assuming the result
      is stored in res:

      For the first column it is res[0]+1.

      For the i'th column, it is res[i]-res[i-1].

      :returns: A list of element indices of top layer elements
      """

      topLayerElments = [];

      # Find top layer elements by matching the number numers of the last half of elmt i 
      # with the first half of element i+1.
      # Elements always start from the bottom, and the element of one columne are following
      # each other in the element table.
      for i in range(len(elementTable)-1):
        elmt1 = elementTable[i];
        elmt2 = elementTable[i+1];

        if (elmt1.size != elmt2.size):
          # elements with different number of nodes can not be on top of each other, 
          # so elmt2 must be another column, and elmt1 must be a top element
          topLayerElments.append(i);
          continue;
        
        if (elmt1.size%2 != 0):
          raise Exception("In a layered mesh, each element must have an even number of elements (element index "+i+")");

        # Number of nodes in a 2D element
        elmt2DSize = int(elmt1.size/2);

        for j in range(elmt2DSize):
          if (elmt2DSize > 2):
            if (elmt1[j + elmt2DSize] != elmt2[j]):
              # At least one node number did not match
              # so elmt2 must be another column, and elmt1 must be a top element
              topLayerElments.append(i);
              break;
          else:
            # for 2D vertical profiles the nodes in the element on the
            # top is in reverse order of those in the bottom.
            if (elmt1[j + elmt2DSize] != elmt2[(elmt2DSize-1)-j]):
              # At least one node number did not match
              # so elmt2 must be another column, and elmt1 must be a top element
              topLayerElments.append(i);
              break;

      # The last element will always be a top layer element
      topLayerElments.append(len(elementTable)-1);

      return (np.array(topLayerElments, dtype=np.int32));


    @staticmethod
    def FindTopLayerElementsXY(elementTable, x, y):
      """
      Find element indices (zero based) of the elements being the upper-most element
      in its column.

      This method uses the element center (x,y) coordinate, and identifies
      each column by having the same element center (x,y) coordinate.

      To find the number of elements in each column, assuming the result
      is stored in res:

      For the first column it is res[0]+1.

      For the i'th column, it is res[i]-res[i-1].

      :returns: A list of element indices of top layer elements
      """

      topLayerElments = [];

      # Find top layer elements by matching the element center (x,y)-coordinates
      # of a column
      for i in range(len(elementTable) - 1):
        elmt1 = elementTable[i];
        elmt2 = elementTable[i + 1];

        x1 = 0;
        y1 = 0;
        x2 = 0;
        y2 = 0;

        # Calculate element center coordinate
        for j in range(elmt1.size):
          x1 += x[elmt1[j] - 1];
          y1 += y[elmt1[j] - 1];
        x1 /= elmt1.size;
        y1 /= elmt1.size;

        for j in range(elmt2.size):
          x2 += x[elmt2[j] - 1];
          y2 += y[elmt2[j] - 1];
        x2 /= elmt2.size;
        y2 /= elmt2.size;

        dx = x2 - x1;
        dy = y2 - y1;
        # Distance (squared) between element center (x,y) coordinates
        dist2 = dx*dx + dy*dy;

        # Find a reference length, being the longest (x,y) 
        # distance between two consecutive nodes in the element table. 
        # For 3D files this will usually be some kind of diagonal.
        maxNodeDist2 = 0;
        for j in range(elmt1.size):
          x1 = x[elmt1[(j) % elmt1.size] - 1];
          y1 = y[elmt1[(j) % elmt1.size] - 1];
          x2 = x[elmt1[(j + 1) % elmt1.size] - 1];
          y2 = y[elmt1[(j + 1) % elmt1.size] - 1];
          dx = x2 - x1;
          dy = y2 - y1;
          nodeDist2 = dx * dx + dy * dy;
          if (nodeDist2 > maxNodeDist2):
            maxNodeDist2 = nodeDist2;

        # Check if element center coordinates differ more than a tolerance
        # times the reference lenght - the maximum node distance.
        if (dist2 > 1e-4 * maxNodeDist2):
          # Element center coordinates are too far from each other, elmt1
          # is a top layer element.
          topLayerElments.append(i);
      
      # The last element will always be a top layer element
      topLayerElments.append(len(elementTable) - 1);

      return (np.array(topLayerElments, dtype=np.int32));

    @staticmethod
    def FindMaxNumberOfLayers(topLayerElements):
      """
      Find the maximum number of layers, based on the indices of
      all top layer elements.

      Assuming that the topLayerElements comes ordered.
      """
      # the first column has top-element-index + 1 layers
      maxLayers = topLayerElements[0]+1;
      for i in range(1, topLayerElements.size):
        layers = topLayerElements[i] - topLayerElements[i - 1];
        if (layers > maxLayers):
          maxLayers = layers;
      return (maxLayers);

    @staticmethod
    def FindMinNumberOfLayers(topLayerElements):
      """
      Find the minimum number of layers, based on the indices of
      all top layer elements.

      Assuming that the <paramref name="topLayerElements"/> comes
      ordered.
      """
      # the first column has top-element-index + 1 layers
      minLayers = topLayerElements[0] + 1;
      for i in range(1, topLayerElements.size):
        layers = topLayerElements[i] - topLayerElements[i - 1];
        if (layers < minLayers):
          minLayers = layers;
      return (minLayers);

