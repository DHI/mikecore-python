from collections.abc import Sequence

import numpy as np
from mikecore.DfsuFile import DfsuFile
from mikecore.eum import eumQuantity, eumItem, eumUnit
from mikecore.MeshFile import MeshFile
from mikecore.DfsBuilder import DfsBuilder
from mikecore.DfsFile import DfsProjection


class MeshBuilder:
    def __init__(self):
        self.__projectionString: str | None = None
        self.__eumQuantity: eumQuantity | None = None

        self.__nodeIds: np.ndarray | None = None
        # x, y, z and code, always set together
        self.__nodes: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = (
            None
        )

        self.__elementIds: Sequence[int] | np.ndarray | None = None
        self.__connectivity: Sequence | np.ndarray | None = None

    def SetProjection(self, projection):
        """Set the geographical projection"""
        if isinstance(projection, str):
            self.__projectionString = projection
        elif isinstance(projection, DfsProjection):
            self.__projectionString = projection.WKTString
        else:
            raise TypeError("projection must be str or DfsProjection")

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

        if (
            numberOfNodes != len(y)
            or numberOfNodes != len(z)
            or numberOfNodes != len(code)
        ):
            raise Exception(
                f"All arguments must have same length. Lengths are: x={x.size}, y={y.size}, z={z.size}, code={code.size}"
            )

        if self.__nodeIds is not None and numberOfNodes != len(self.__nodeIds):
            raise Exception(
                "Arguments does not have same length as the number of node ids. These must match"
            )

        self.__nodes = (x, y, z, code)

    def SetElements(self, connectivity):
        if connectivity is None:
            raise TypeError("connectivity")
        if len(connectivity) == 0:
            raise ValueError(
                "Element table has no rows. There must be at least one row"
            )

        ## Check number of elements
        for i in range(len(connectivity)):
            elmnt = connectivity[i]
            if (3 > len(elmnt)) or (len(elmnt) > 4):
                raise ValueError(
                    f"All elements must have 3 or 4 nodes. Element number {i + 1} has {len(elmnt)} nodes"
                )

        self.__connectivity = connectivity

    def SetElementIds(self, elementIds):
        """Set the element id's. Optional. If not set, default values are used (1,2,3,...)"""
        if (self.__connectivity is not None) and (
            len(self.__connectivity) != len(elementIds)
        ):
            raise ValueError("Number of element id's does not match number of elements")
        self.__elementIds = elementIds

    def Validate(self, dieOnError: bool = False) -> list[str]:
        """Validate will return a string of issues from the mesh builder.
        When this returns an empty list, the mesh has been properly build.
        """
        errors = []
        if self.__projectionString is None:
            errors.append("Projection has not been set")
        if self.__nodes is None:
            errors.append("Nodes have not been set")
        if self.__connectivity is None:
            errors.append("Elements have not been set")

        # Check that all nodenumbers are within the range of number of nodes.
        if (self.__nodes is not None) and (self.__connectivity is not None):
            numberOfNodes = len(self.__nodes[0])
            for elmt in self.__connectivity:
                elmt = np.array(elmt)
                if np.any(elmt <= 0) or np.any(elmt > numberOfNodes):
                    errors.append(
                        "At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]"
                    )
                    break

        if dieOnError and (len(errors) > 0):
            msgs = DfsBuilder.ErrorMessage(errors)
            raise Exception(msgs)

        return errors

    def CreateMesh(self) -> MeshFile:
        """Create and return a new MeshFile object"""
        errors = self.Validate()
        projectionString = self.__projectionString
        nodes = self.__nodes
        connectivity = self.__connectivity
        # Validate reports each of these as an error when it is None
        if errors or projectionString is None or nodes is None or connectivity is None:
            raise Exception(DfsBuilder.ErrorMessage(errors))
        x, y, z, code = nodes

        # Creating default eumQuantity in meters
        if self.__eumQuantity is None:
            self.__eumQuantity = eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter)

        # Creating default node id's, if empty
        if self.__nodeIds is None:
            self.__nodeIds = np.arange(len(x)) + 1

        # Creating default element id's, if empty
        if self.__elementIds is None:
            self.__elementIds = np.arange(len(connectivity)) + 1

        # Creating additional element information
        elementType = np.zeros(len(connectivity), dtype=np.int32)
        nodesPerElmt = np.zeros(len(connectivity), dtype=np.int32)
        nodeElmtCount = 0  # total number of nodes listed in the connectivity table
        for i in range(len(elementType)):
            elmtTypeNumber = 0
            elmt = connectivity[i]
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

        res = MeshFile.Create(
            self.__eumQuantity,
            projectionString,
            self.__nodeIds,
            x,
            y,
            z,
            code,
            self.__elementIds,
            elementType,
            connectivity,
        )

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

        res = MeshFile.Create(
            bathyQuantity,
            dfsuFile.Projection.WKTString,
            dfsuFile.NodeIds,
            dfsuFile.X,
            dfsuFile.Y,
            dfsuFile.Z.astype(dtype=np.float32),
            dfsuFile.Code,
            dfsuFile.ElementIds,
            dfsuFile.ElementType,
            dfsuFile.ElementTable,
        )
        return res
