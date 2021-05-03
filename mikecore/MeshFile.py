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
    _eumQuantity = None

    # Node variables
    _nodeIds = None # this can be None, then set default id's, starting from 1
    _x = None
    _y = None
    _z = None
    _code = None

    # Element variables
    _elementIds = None # this can be None, then set default id's, starting from 1
    _elementType = None
    _connectivity = []
    
    _hasQuads = None

    #  <summary>
    #  Quantity of the data stored in the mesh file. This is the quantity of the
    #  <see cref="Z"/> variable.
    #  </summary>
    @property
    def EumQuantity(self) -> eumQuantity:
        return self._eumQuantity

    def GetProjectionString(self) -> str:
        """The projection string """
        return self._wktString

    def SetProjectionString(self, value: str):
        """Set the projection string """
        self._wktString = value

    def GetNumberOfNodes(self) -> int:
        """Number of nodes in the mesh."""
        return len(self._nodeIds)

    def GetNumberOfElements(self) -> int:
        """Number of elements in the mesh."""
        return len(self._elementIds)

    def GetNodeIds(self) -> List[int]:
        """Node Id's """
        return self._nodeIds

    def SetNodeIds(self, value: List[int]):
        """Set Node Id's 
        You can modify each value individually directly in the list, 
        or provide a new array of values, which must have the same
        length as the original one.
        
        Be aware that changing this to anything but the default values (1,2,3,...)
        can make some tools stop working.
        """
        if len(self._nodeIds) != len(value):
            raise ValueError("Length of input does not match number of nodes")
        self._nodeIds = value

    def GetNumberOfElements(self) -> int:
        """Number of elements in the mesh."""
        return len(self._elementIds)

   
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
                
                self._eumQuantity = eumQuantity(itemType, itemUnit)
                noNodes = int(groups[2])
                proj = groups[3]                

            # If not successfull, try match the 2011 header line format
            if proj == None:
                match = header2011(line)    
                if match:
                    self._eumQuantity = eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter)
                    groups = match.groups()
                    noNodes = int(groups[0])
                    proj = groups[1]    
            
            if proj == None:
                raise IOError("Can not load mesh file (failed reading mesh file header line): {0}".format(filename))
            
            _wktString = proj.strip()
            self._nodeIds = np.zeros(noNodes, dtype=int)
            self._x = np.zeros(noNodes, dtype=np.float)
            self._y = np.zeros(noNodes, dtype=np.float)
            self._z = np.zeros(noNodes, dtype=np.float)
            self._code = np.zeros(noNodes, dtype=int)

            # Read nodes
            try:
                for i in range(noNodes):
                    line = reader.readline().strip()
                    if line == None:
                        raise IOError("Unexpected end of file") # used as inner exception
                    strings = line.split(separator)  # RemoveEmptyEntries
                    self._nodeIds[i] = int(strings[0])
                    self._x[i] = float(strings[1])#, NumberFormatInfo.InvariantInfo)
                    self._y[i] = float(strings[2])#, NumberFormatInfo.InvariantInfo)
                    self._z[i] = float(strings[3])#, NumberFormatInfo.InvariantInfo)
                    self._code[i] = int(strings[4])            
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

            strings = line.split(separator)
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
            self._elementIds = np.zeros(noNodes, dtype=int)
            self._elementType = np.zeros(noNodes, dtype=int)
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

                    #strings = re.split(r" +",line)
                    strings = line.split(separator)
                    self._elementIds[i] = int(strings[0])
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
                        self._elementType[i] = 21
                    elif len(self._connectivity[i]) == 4:
                        self._elementType[i] = 25
                        self._hasQuads = True
                    else:
                        self._elementType[i] = 0
                        # TODO: Throw an exception?                    
                
            except Exception as inner:
                raise Exception("Can not load mesh file (failed reading elements): {0}. {1}".format(filename, inner))            


    def Write(self, filename:str):
        """Write mesh to file
        """
        pass  # TODO
        # # All double values are written using the "r" format string in order to assure correct
        # # round-tripping (not loosing any decimals when reading again)

        # TextWriter tw = new StreamWriter(filename)

        # # Mesh file header line
        # tw.Write(_eumQuantity.ItemInt)
        # tw.Write(" ")
        # tw.Write(_eumQuantity.UnitInt)
        # tw.Write(" ")
        # tw.Write(_nodeIds.Length)
        # tw.Write(" ")
        # tw.WriteLine(_wktString)

        # # Node information
        # for (int i = 0 i < _nodeIds.Length i++)
        # {
        # tw.Write(_nodeIds[i])
        # tw.Write(" ")
        # tw.Write(_x[i].ToString("r", NumberFormatInfo.InvariantInfo))
        # tw.Write(" ")
        # tw.Write(_y[i].ToString("r", NumberFormatInfo.InvariantInfo))
        # tw.Write(" ")
        # tw.Write(_z[i].ToString("r", NumberFormatInfo.InvariantInfo))
        # tw.Write(" ")
        # tw.WriteLine(_code[i])
        # }

        # int maxNoNodesPerElmt
        # tw.Write(_elementIds.Length)
        # tw.Write(" ")
        # if (!_hasQuads)
        # {
        # maxNoNodesPerElmt = 3
        # tw.Write("3")
        # tw.Write(" ")
        # tw.WriteLine("21")
        # }
        # else
        # {
        # maxNoNodesPerElmt = 4
        # tw.Write("4")
        # tw.Write(" ")
        # tw.WriteLine("25")
        # }

        # # Element information
        # for (int i = 0 i < _elementIds.Length i++)
        # {
        # tw.Write(_elementIds[i])
        # int[] nodes = _connectivity[i]
        # for (int j = 0 j < nodes.Length j++)
        # {
        #     tw.Write(" ")
        #     tw.Write(nodes[j])

        # }
        # # Fill up with zeros
        # for (int j = nodes.Length j < maxNoNodesPerElmt j++)
        # {
        #     tw.Write(" ")
        #     tw.Write(0)
        # }
        # tw.WriteLine()
        # }

        # tw.Close()

    def Create(self, eumQuantity: eumQuantity, wktString: str, nodeIds: List[int], x: List[float], y: List[float], z: List[float], nodeCode: List[int], elmtIds: List[int], elmtTypes: List[int], connectivity): # -> MeshFile:

        res = MeshFile()
        res._eumQuantity = eumQuantity
        res._wktString = wktString
        res._nodeIds = nodeIds
        res._x = x
        res._y = y
        res._z = z
        res._code = nodeCode
        res._elementIds = elmtIds
        res._elementType = elmtTypes
        res._connectivity = connectivity
        for i in range(len(connectivity)):        
            if len(connectivity[i]) == 4:
                res._hasQuads = True
                break

        return res

    @staticmethod
    def ReadMesh(filename: str):# -> MeshFile:
        """Read the mesh from the provided mesh file"""

        if not os.path.exists(filename):
            raise FileNotFoundError("File {0} not found".format(filename))
        file = MeshFile()
        file.Read(filename)
        return file
