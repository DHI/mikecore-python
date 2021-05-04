import numpy as np
from typing import List
from mikecore.DfsuFile import DfsuFile
from mikecore.eum import eumQuantity, eumItem, eumUnit
from mikecore.MeshFile import MeshFile
from mikecore.DfsBuilder import DfsBuilder
from mikecore.DfsFile import DfsProjection

class MeshBuilder:

    def __init__(self):
        self.__projectionString = None
        self.__eumQuantity = None
        
        self.__isSetProjection = False
        self.__isSetNodes = False
        self.__isSetConnectivity = False

        self.__nodeIds = None
        self.__x = None
        self.__y = None
        self.__z = None
        self.__code = None

        self.__elementIds = None
        self.__connectivity = None

    def SetProjection(self, projection):
        """Set the geographical projection"""
        if isinstance(projection, str):
            self.__projectionString = projection
        elif isinstance(projection, DfsProjection):
            self.__projectionString = projection.WKTString
        else:
            raise TypeError("projection must be str or DfsProjection")
        self.__isSetProjection = True    

    def SetEumQuantity(self, eumQuantity):    
        self.__eumQuantity = eumQuantity
    
    def SetNodes(self, x, y, z, code):
      """Set node coordinates and code. Depending on the projection string, 
         node coordinates are in meters or degrees
      """
      try:
        x = np.array(x, dtype=np.float64)
      except:
        raise TypeError("x must be array of float")
      try:
        y = np.array(y, dtype=np.float64)
      except:
        raise TypeError("y must be array of float")
      try:
        z = np.array(z, dtype=np.float32)
      except:
        raise TypeError("z must be array of float")
      try:
        code = np.array(code, dtype=np.int32)
      except:
        raise TypeError("code must be array of int")

      numberOfNodes = len(x)

      if (numberOfNodes != len(y) or numberOfNodes != len(z) or numberOfNodes != len(code)):
          raise Exception("All arguments must have same length. Lengths are: x={x}, y={y}, z={z}, code={code}".format(x=x.size, y=y.size, z=z.size, code=code.size))

      if (self.__nodeIds != None and numberOfNodes != len(self.__nodeIds)):
        raise Exception("Arguments does not have same length as the number of node ids. These must match")

      self.__x = x
      self.__y = y
      self.__z = z
      self.__code = code
      self.__isSetNodes = True

    def SetElements(self, connectivity):
        if connectivity == None:
            raise TypeError("connectivity")
        if len(connectivity) == 0:
            raise ValueError("Element table has no rows. There must be at least one row")

        ## Check number of elements
        for i in range(len(connectivity)):
            elmnt = connectivity[i]
            if (3 > len(elmnt)) or (len(elmnt) > 4):
                raise ValueError("All elements must have 3 or 4 nodes. Element number {0} has {1} nodes".format(i + 1, len(elmnt)))
        
        self.__connectivity = connectivity
        self.__isSetConnectivity = True

    def SetElementIds(self, elementIds):
        """Set the element id's. Optional. If not set, default values are used (1,2,3,...)"""
        if (not self.__connectivity is None) and (len(self.__connectivity) != len(elementIds)):
            raise ValueError("Number of element id's does not match number of elements")
        self.__elementIds = elementIds

    def Validate(self, dieOnError: bool=False) -> List[str]:
        """Validate will return a string of issues from the mesh builder.
        When this returns an empty list, the mesh has been properly build.
        """
        errors = []
        if not self.__isSetProjection:
            errors.append("Projection has not been set")
        if not self.__isSetNodes:
            errors.append("Nodes have not been set")
        if not self.__isSetConnectivity:
            errors.append("Elements have not been set")

        # Check that all nodenumbers are within the range of number of nodes.        
        if (self.__isSetNodes) and (self.__isSetConnectivity):      
            for elmt in self.__connectivity:
                elmt = np.array(elmt)
                if np.any(elmt<=0) or np.any(elmt>len(self.__x)):
                    errors.append("At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]")
                    break
            
        if dieOnError and (len(errors) > 0):
            msgs = DfsBuilder.ErrorMessage(errors)
            raise Exception(msgs)

        return errors

    def CreateMesh(self) -> MeshFile:
        """Create and return a new MeshFile object"""
        self.Validate(dieOnError=True)

        # Creating default eumQuantity in meters
        if self.__eumQuantity == None: 
            self.__eumQuantity = eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter);

        # Creating default node id's, if empty
        if self.__nodeIds == None:
            self.__nodeIds = np.arange(len(self.__x)) + 1            
        
        # Creating default element id's, if empty
        if self.__elementIds == None:            
            self.__elementIds = np.arange(len(self.__connectivity)) + 1
            
        # Creating additional element information
        elementType = np.zeros(len(self.__connectivity), dtype=np.int32)
        nodesPerElmt = np.zeros(len(self.__connectivity), dtype=np.int32)
        nodeElmtCount = 0  # total number of nodes listed in the connectivity table
        for i in range(len(elementType)):
            elmtTypeNumber = 0
            elmt = self.__connectivity[i]
            if len(elmt) == 3:
                elmtTypeNumber = 21
            elif len(elmt) == 4:
                elmtTypeNumber = 25
            elif len(elmt) == 6:
                elmtTypeNumber = 32
            elif len(elmt) == 8:
                elmtTypeNumber = 33
            else:
                raise Exception("Element with invalid number of nodes encountered")

            elementType[i] = elmtTypeNumber
            nodesPerElmt[i] = len(elmt)
            nodeElmtCount += len(elmt)

        # NotUsed
        # connectivityArray = np.zeros(nodeElmtCount, dtype=np.int32)
        # k = 0
        # for i in range(len(elementType)):
        #     elmt = self.__connectivity[i]
        #     for j in range(len(elmt)):
        #         connectivityArray[k] = elmt[j]
        #         k += 1
 
        res = MeshFile.Create(self.__eumQuantity, 
                              self.__projectionString, 
                              self.__nodeIds, 
                              self.__x, 
                              self.__y,
                              self.__z, 
                              self.__code, 
                              self.__elementIds, 
                              elementType, 
                              self.__connectivity)

        return res

    @staticmethod
    def Create(dfsuFile: DfsuFile) -> MeshFile:
        """Create a mesh file from the provided dfsu file.
        The dfsu file must be a 2D dfsu file.
        """
        if dfsuFile.ZUnit != eumUnit.eumUUnitUndefined:
            bathyQuantity = eumQuantity(eumItem.eumIBathymetry, dfsuFile.ZUnit)
        else:
            bathyQuantity = eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter)
      
        res = MeshFile.Create(bathyQuantity, 
                              dfsuFile.Projection.WKTString, 
                              dfsuFile.NodeIds, 
                              dfsuFile.X, 
                              dfsuFile.Y, 
                              dfsuFile.Z.astype(dtype=np.float32),
                              dfsuFile.Code, 
                              dfsuFile.ElementIds, 
                              dfsuFile.ElementType, 
                              dfsuFile.ElementTable)                                    
        return res
    