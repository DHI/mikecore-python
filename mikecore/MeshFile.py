import os.path
#from enum import Enum
#import datetime
#import ctypes
import numpy as np
from mikecore.eum import *
#from mikecore.DfsDLL import DfsDLL
from typing import Union, List
import re

#  <summary>
#  Class for handling mesh files (reading, writing, editing)
#  </summary>
class MeshFile:

    # projection as wkt-string
    _wktString = None

    # quantity of data in the mesh file
    EumQuantity = None

    # Node variables
    NodeIds = None # this can be None, then set default id's, starting from 1
    X = None
    Y = None
    Z = None
    Code = None

    # Element variables
    ElementIds = None # this can be None, then set default id's, starting from 1
    ElementType = None
    _connectivity = []
    
    _hasQuads = None

    #  <summary>
    #  Quantity of the data stored in the mesh file. This is the quantity of the
    #  <see cref="Z"/> variable.
    #  </summary>
    # @property
    # def EumQuantity(self) -> eumQuantity:
    #     return self._eumQuantity

    # def GetProjectionString(self) -> str:
    #     """The projection string """
    #     return self._wktString

    # def SetProjectionString(self, value: str):
    #     """Set the projection string """
    #     self._wktString = value

    def GetNumberOfNodes(self) -> int:
        """Number of nodes in the mesh."""
        return len(self.NodeIds)

    def GetNumberOfElements(self) -> int:
        """Number of elements in the mesh."""
        return len(self.ElementIds)

    # def GetNodeIds(self) -> List[int]:
    #     """Node Id's """
    #     return self.NodeIds

    # def SetNodeIds(self, value: List[int]):
    #     """Set Node Id's 
    #     You can modify each value individually directly in the list, 
    #     or provide a new array of values, which must have the same
    #     length as the original one.
        
    #     Be aware that changing this to anything but the default values (1,2,3,...)
    #     can make some tools stop working.
    #     """
    #     if len(self.NodeIds) != len(value):
    #         raise ValueError("Length of input does not match number of nodes")
    #     self.NodeIds = value

    def GetNumberOfElements(self) -> int:
        """Number of elements in the mesh."""
        return len(self.ElementIds)

   
    #  <summary>
    #  Node X coordinates.
    #  <para>
    #  You can modify each coordinate individually directly in the list, 
    #  or provide a new array of coordinates, which must have the same
    #  length as the original one.
    #  </para>
    #  </summary>
    # public double[] X
    # {
    #     get { return _x }
    #     set
    #     {
    #     if (_x.Length != value.Length)
    #         raise ArgumentException("Length of input does not match number of nodes")
    #     _x = value
    #     }
    # }

    # #  <summary>
    # #  Node Y coordinates.
    # #  <para>
    # #  You can modify each coordinate individually directly in the list, 
    # #  or provide a new array of coordinates, which must have the same
    # #  length as the original one.
    # #  </para>
    # #  </summary>
    # public double[] Y
    # {
    #     get { return _y }
    #     set
    #     {
    #     if (_y.Length != value.Length)
    #         raise ArgumentException("Length of input does not match number of nodes")
    #     _y = value
    #     }
    # }

    # #  <summary>
    # #  Node Z coordinates.
    # #  <para>
    # #  You can modify each coordinate individually directly in the list, 
    # #  or provide a new array of coordinates, which must have the same
    # #  length as the original one.
    # #  </para>
    # #  </summary>
    # public double[] Z
    # {
    #     get { return _z }
    #     set
    #     {
    #     if (_z.Length != value.Length)
    #         raise ArgumentException("Length of input does not match number of nodes")
    #     _z = value
    #     }
    # }

    # #  <summary>
    # #  Node boundary code.
    # #  <para>
    # #  You can modify each value individually directly in the list, 
    # #  or provide a new array of values, which must have the same
    # #  length as the original one.
    # #  </para>
    # #  </summary>
    # public int[] Code
    # {
    #     get { return _code }
    #     set
    #     {
    #     if (_code.Length != value.Length)
    #         raise ArgumentException("Length of input does not match number of nodes")
    #     _code = value
    #     }
    # }

    # #  <summary>
    # #  Element Id's
    # #  <para>
    # #  You can modify each value individually directly in the list, 
    # #  or provide a new array of values, which must have the same
    # #  length as the original one.
    # #  </para>
    # #  <para>
    # #  Be aware that changing this to anything but the default values (1,2,3,...)
    # #  can make some tools stop working.
    # #  </para>
    # #  </summary>
    # public int[] ElementIds
    # {
    #     get { return _elementIds }
    #     set
    #     {
    #     if (_elementIds.Length != value.Length)
    #         raise ArgumentException("Length of input does not match number of elements")
    #     _elementIds = value
    #     }
    # }


    #  <summary>
    #  Array of element types. See documentation for each type.
    #  </summary>
    # TODO: Make into a enum
    
    #  def ElementType(self) -> List[int]:
    #     return self._elementType

    #  <summary>
    #  The <see cref="ElementTable"/> defines for each element which 
    #  nodes that defines the element. 
    #  <para>
    #  The numbers in the <see cref="ElementTable"/> are node numbers, not indices!
    #  Each value in the table must be between 1 and number-of-nodes.
    #  </para>
    #  <para>
    #  You can modify each value individually directly in the list, 
    #  or provide a new array of values, which must have the same
    #  length as the original one.
    #  </para>
    #  </summary>
    def GetElementTable(self) -> List:
        return self._connectivity

    # public int[][] ElementTable
    # {
    #     get { return _connectivity }
    #     set
    #     {
    #     if (_connectivity.Length != value.Length)
    #         raise ArgumentException("Length of input does not match number of elements")
    #     _connectivity = value
    #     }
    # }

    def Read(self, filename:str):
        """Read .mesh file and load all data.

        If an element specifies a node number of zero, that node number is ignored, and
        does not become a part of the mesh data structure. That is the case for e.g.
        mixed triangular/quadrilateral meshes, where all elements specify 4 nodes, 
        and triangular elements specifies the last node as zero.
        """
        with open(filename ,'r') as reader:
            separator = ' '#[' ', '\t']
            
            # read header line
            line = reader.readline().lstrip()
            if line is None:
                raise IOError("Can not load mesh file. File is empty")

            noNodes = 0
            proj = None

            header2012 = lambda s: re.match(r"(\d+)\s+(\d+)\s+(\d+)\s+(.+)", s)            
            header2011 = lambda s: re.match(r"(\d+)\s+(.+)", s)

            # First try match the 2012 header line format
            match = header2012(line)
            if match:
                groups = match.groups()
                itemType = eumItem(int(groups[0]))
                itemUnit = eumUnit(int(groups[1]))
                #(eumItem)Int32.Parse(groups[1]g)
                #itemUnit = (eumUnit)Int32.Parse(groups[2])
                
                self.EumQuantity = eumQuantity(itemType, itemUnit)
                noNodes = int(groups[2])
                proj = groups[3]                

            # If not successfull, try match the 2011 header line format
            if proj == None:
                match = header2011(line)    
                if match:
                    self.EumQuantity = eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter)
                    groups = match.groups()
                    noNodes = int(groups[0])
                    proj = groups[1]    
            
            if proj == None:
                raise IOError("Can not load mesh file (failed reading mesh file header line): {0}".format(filename))
            
            _wktString = proj.strip()
            self.NodeIds = np.zeros(noNodes, dtype=int)
            self.X = np.zeros(noNodes, dtype=np.float)
            self.Y = np.zeros(noNodes, dtype=np.float)
            self.Z = np.zeros(noNodes, dtype=np.float)
            self.Code = np.zeros(noNodes, dtype=int)

            # Read nodes
            try:
                for i in range(noNodes):
                    line = reader.readline().strip()
                    if line == None:
                        raise IOError("Unexpected end of file") # used as inner exception
                    strings = re.split(r"\s+",line)
                    self.NodeIds[i] = int(strings[0])
                    self.X[i] = float(strings[1])#, NumberFormatInfo.InvariantInfo)
                    self.Y[i] = float(strings[2])#, NumberFormatInfo.InvariantInfo)
                    self.Z[i] = float(strings[3])#, NumberFormatInfo.InvariantInfo)
                    self.Code[i] = int(strings[4])            
            except Exception as inner:
                # DfsException
                raise Exception("Can not load mesh file (failed reading nodes): {0}. {1}".format(filename, inner))
            
            # Reading element header line
            noElements = None
            maxNoNodesPerElement = None
            elmtCode = None
            
            line = reader.readline().strip()
            if line is None:
                raise IOError("Can not load mesh file (unexpected end of file)")

            strings = re.split(r"\s+",line)
            if (len(strings) != 3):
                raise IOError("Can not load mesh file (failed reading element header line): {0}".format(filename))
            try:            
                noElements = int(strings[0])
                maxNoNodesPerElement = int(strings[1])
                elmtCode = int(strings[2])            
            except Exception as ex:            
                raise Exception("Can not load mesh file (failed reading element header line): {0}. {1}".format(filename, ex))
            
            # Element code must be 21 or 25 (21 for triangular meshes, 25 for mixed meshes)
            if (elmtCode != 21) or (elmtCode != 25):
                pass # TODO?? Do we care?
            
            # Allocate memory for elements
            self.ElementIds = np.zeros(noElements, dtype=int)
            self.ElementType = np.zeros(noElements, dtype=int)
            self._connectivity = [] #new int[noElements][]

            # Temporary (reused) list of nodes in one element
            nodesInElement = np.zeros(maxNoNodesPerElement, dtype=int)
            #List<int> nodesInElement = new List<int>(maxNoNodesPerElement)

            # Read all elements
            try:
                for i in range(noElements):

                    nodesInElement[:] = 0

                    line = reader.readline().strip()
                    if line is None:
                        raise IOError("Unexpected end of file") # used as inner exception

                    strings = re.split(r"\s+",line)                    
                    self.ElementIds[i] = int(strings[0])
                    noNodesInElmt = len(strings) - 1
                    for j in range(noNodesInElmt):
                        nodeNumber = int(strings[j + 1])
                        if (nodeNumber < 0) or (nodeNumber > noNodes): # used as inner exception:
                            raise IOError("Node number in element table is negative or larger than number of nodes")
                        # It is only a node in the element if the node number is positive
                        if nodeNumber > 0:
                            nodesInElement[j] = nodeNumber
                    
                    self._connectivity.append(nodesInElement[:noNodesInElmt])

                    # Get element type from number of nodes
                    if len(self._connectivity[i]) == 3:
                        self.ElementType[i] = 21
                    elif len(self._connectivity[i]) == 4:
                        self.ElementType[i] = 25
                        self._hasQuads = True
                    else:
                        self.ElementType[i] = 0
                        # TODO: Throw an exception?                    
                
            except Exception as inner:
                raise Exception("Can not load mesh file (failed reading elements): {0}. {1}".format(filename, inner))            


    def Write(self, filename:str):
        """Write mesh to file
        """
        # # All double values are written using the "r" format string in order to assure correct
        # # round-tripping (not loosing any decimals when reading again)

        with open(filename, 'w') as writer:
            # header line
            line = str(self.EumQuantity.ItemInt) + " "
            line += str(self.EumQuantity.UnitInt) + " " 
            line += str(self.NodeIds) + " " 
            line += self._wktString
            writer.write(line)

            # Node information
            for i in range(len(self.NodeIds)):
                line = str(self.NodeIds[i]) + " "
                line += str(self.X[i]) + " "
                line += str(self.Y[i]) + " "
                line += str(self.Z[i]) + " "
                line += str(self.Code[i]) 
                writer.write(line)
        
            # Element "header"
            line = str(len(self.ElementIds)) + " "
            if not self._hasQuads:
                maxNodesPerElmt, elmtType = 3, 21
            else:
                maxNodesPerElmt, elmtType = 4, 25
            line += str(maxNodesPerElmt) + " " + str(elmtType)
            writer.write(line)

            # Element information
            for i in range(len(self.ElementIds)):
                line = str(self.ElementIds[i])
                nodes = self._connectivity[i]
                for j in range(len(nodes)):
                    line = " " + str(nodes[j])
                for j in range(len(nodes), maxNodesPerElmt):
                    # fill with zeros
                    line = " " + "0"
                writer.write(line)

    def Create(self, eumQuantity: eumQuantity, wktString: str, nodeIds: List[int], x: List[float], y: List[float], z: List[float], nodeCode: List[int], elmtIds: List[int], elmtTypes: List[int], connectivity) -> "MeshFile":

        res = MeshFile()
        res.EumQuantity = eumQuantity
        res._wktString = wktString
        res.NodeIds = nodeIds
        res.X = x
        res.Y = y
        res.Z = z
        res.Code = nodeCode
        res.ElementIds = elmtIds
        res.ElementType = elmtTypes
        res._connectivity = connectivity
        for i in range(len(connectivity)):        
            if len(connectivity[i]) == 4:
                res._hasQuads = True
                break

        return res

    @staticmethod
    def ReadMesh(filename: str) -> "MeshFile":
        """Read the mesh from the provided mesh file"""

        if not os.path.exists(filename):
            raise FileNotFoundError("File {0} not found".format(filename))
        file = MeshFile()
        file.Read(filename)
        return file