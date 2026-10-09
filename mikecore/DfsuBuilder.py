from collections.abc import Sequence

import numpy as np
from mikecore.DfsFile import DfsProjection, DfsTemporalAxis
from mikecore.MeshFile import MeshFile
from mikecore.MeshBuilder import MeshNodes
from mikecore.DfsFactory import DfsFactory
from mikecore.DfsBuilder import DfsBuilder
from mikecore.DfsuFile import (
    DfsuFile,
    DfsuFileType,
    DfsSimpleType,
    DataValueType,
    DfsuUtil,
)
from mikecore.eum import eumUnit, eumQuantity, eumItem


# / <summary>
# / Builder for creating a dfsu file.
# / <para>
# / The following must be set before calling <see cref="CreateFile"/>:
# / <see cref="SetProjection"/>,
# / <see cref="SetTimeInfo"/>,
# / <see cref="SetNodes(double[],double[],float[],int[])"/>,
# / <see cref="SetElements"/>.
# / </para>
# / <para>
# / For files with a vertical dimension, the <see cref="SetNumberOfSigmaLayers"/> must also be set.
# / </para>
# / <para>
# / Other setters are optional, and if not set, default values are written to the file.
# / </para>
# / <para>
# / Using the <see cref="SetFromMeshFile"/> will set the projection, nodes
# / and elements from the mesh file.
# / </para>
# / <para>
# / Be aware; setting the node and element id's to anything but the default
# / values can cause some tools to fail.
# / </para>
# / </summary>
class DfsuBuilder:
    def __init__(self, dfsuFileType):
        self.__isSetTimeInfo = False
        self.__isSetNumberOfSigmaLayers = False

        self.__dfsuFileType = dfsuFileType
        self.__numberOfSigmaLayers = -1

        # Projection variables
        self.__dfsProjection: DfsProjection | None = None

        # Time variables
        self.__timeAxis: DfsTemporalAxis | None = None
        self.__startDateTime = None
        self.__timeStepInSeconds = -1
        self.__numberOfTimeSteps = -1

        # Node variables
        # this can be null, then set default id's, starting from 1
        self.__nodeIds: np.ndarray | None = None
        self.__nodes: MeshNodes | None = None
        self.__zUnit = eumUnit.eumUmeter
        self.__zQuantity: eumQuantity | None = None

        # Element variables
        self.__connectivity: Sequence | np.ndarray | None = None
        # this can be null, then set default id's, starting from 1
        self.__elementIds: np.ndarray | None = None

        # Dynamic item information
        self.__dynamicItemData = []

        # spectral
        self.__frequencies: Sequence[float] | np.ndarray | None = None
        self.__directions: Sequence[float] | np.ndarray | None = None

        self.__dfsuFileType = dfsuFileType
        if dfsuFileType == DfsuFileType.Dfsu2D:
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

    def SetProjection(self, projection: DfsProjection):
        """Set the geographical projection"""
        if isinstance(projection, DfsProjection):
            self.__dfsProjection = projection
        else:
            raise TypeError("projection must be DfsProjection")

    # / <summary>
    # / Set the number of sigma layers in a file with a vertical dimension
    # / </summary>
    # / <remarks>
    # / If called with a <see cref="DfsuFileType"/> that does not have any
    # / vertical dimension, an <see cref="InvalidOperationException"/> is thrown.
    # / </remarks>
    def SetNumberOfSigmaLayers(self, numberOfSigmaLayers: int):
        if self.__dfsuFileType == DfsuFileType.Dfsu2D:
            raise Exception("Can not set number of sigma layers on a 2D dfsu file")
        elif (
            self.__dfsuFileType
            == DfsuFileType.DfsuVerticalColumn  # strictly speaking not required, but anyway...
            or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma
            or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ
            or self.__dfsuFileType == DfsuFileType.Dfsu3DSigma
            or self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ
        ):
            self.__numberOfSigmaLayers = numberOfSigmaLayers
            self.__isSetNumberOfSigmaLayers = True
        else:
            raise Exception("dfsuFileType")

    def SetFrequencies(self, frequencies):
        self.__frequencies = frequencies

    def SetDirections(self, directions):
        self.__directions = directions

    # / <summary>
    # / Set a non-standard temporal axis for the dfsu file. WARNING: The dfsu file will not be valid in all contexts.
    # / <para>
    # / The standard dfsu file requires an <see cref="IDfsEqCalendarAxis"/> temporal axis.
    # / You can use the <see cref="SetTimeInfo"/> method to define a valid <see cref="IDfsEqCalendarAxis"/>
    # / axis for the dfsu file.
    # / </para>
    # / <para>
    # / If you define another temporal axis than the <see cref="IDfsEqCalendarAxis"/> for a dfsu file,
    # / be sure to test that the file works as intended in your context.
    # / </para>
    # / </summary>
    def SetTemporalAxis(self, timeAxis: DfsTemporalAxis):
        self.__timeAxis = timeAxis
        self.__isSetTimeInfo = True

    def SetTimeInfo(self, startDateTime, timeStepInSeconds):
        """Set time info, specifying an equidistant calendar axis, which is the default (always valid) temporal axis of a dfsu file."""
        self.__startDateTime = startDateTime
        self.__timeStepInSeconds = timeStepInSeconds
        self.__isSetTimeInfo = True

    # / <summary>
    # / Sets the number of time steps in the file.
    # / <para>
    # / This is only required in streaming context, where it is not possible
    # / to update the dfs header when everything is written to the file.
    # / In a non-streaming context this should not be used.
    # / </para>
    # / <para>
    # / This is a stage 1 method.
    # / </para>
    # / </summary>
    def SetNumberOfTimeSteps(self, numberOfTimeSteps: int):
        self.__numberOfTimeSteps = numberOfTimeSteps

    def SetNodes(self, x, y, z, code):
        """Set node coordinates and code. Depending on the projection string,
        node coordinates are in meters or degrees
        """
        try:
            x = np.array(x, dtype=np.float64)
        except Exception as err:
            raise TypeError("x must be array of float") from err
        try:
            y = np.array(y, dtype=np.float64)
        except Exception as err:
            raise TypeError("y must be array of float") from err
        try:
            z = np.array(z, dtype=np.float32)
        except Exception as err:
            raise TypeError("z must be array of float") from err
        try:
            code = np.array(code, dtype=np.int32)
        except Exception as err:
            raise TypeError("code must be array of int") from err

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

        self.__nodes = MeshNodes(x, y, z, code)

    # / <inheritdoc/>
    def SetZUnit(self, zUnit: eumUnit):
        # TODO: Fix!
        if (
            zUnit != eumUnit.eumUmeter
            and zUnit != eumUnit.eumUfeet
            and zUnit != eumUnit.eumUUnitUndefined
        ):
            raise Exception("Currently only meter and feet unit is supported")
        self.__zUnit = zUnit
        # if (EUMWrapper.eumUnitsEqv(eumUnit.eumUmeter, zUnit)):
        #  self.__zUnit = zUnit
        # else:
        #  raise Exception("Unit of z coordinate is not a length unit")

    def SetNodeIds(self, nodeIds):
        """Set the node id's. Optional. If not set, default values are used (1,2,3,...)"""
        if nodeIds is None:
            self.__nodeIds = None
            return
        if self.__nodes is not None and self.__nodes.x.size != nodeIds.size:
            raise Exception(
                "Number of node id's does not match number of nodes", "nodeIds"
            )
        self.__nodeIds = nodeIds

    def SetElements(self, connectivity):
        """Set element connectivity: For each element is specified which nodes
        the element consist of. The node is specified by its index into the list of nodes.
        """
        if connectivity is None:
            raise Exception("connectivity")
        if len(connectivity) == 0:
            raise Exception("Element table has no rows. There must be at least one row")

        if self.__elementIds is not None and self.__elementIds.size != len(
            connectivity
        ):
            raise Exception(
                "Number of elements is not the same as number of element ids. They must match"
            )

        # Validate that element numbers are ok.
        if self.__dfsuFileType == DfsuFileType.Dfsu2D:
            # Check number of elements
            for i in range(len(connectivity)):
                elmnt = connectivity[i]
                if 3 > len(elmnt) or len(elmnt) > 4:
                    raise Exception(
                        f"All elements must have 3 or 4 nodes. Element number {i + 1} has {len(elmnt)} nodes"
                    )
        elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigma:
            # Check number of elements
            for i in range(len(connectivity)):
                elmnt = connectivity[i]
                if len(elmnt) != 6 and len(elmnt) != 8:
                    raise Exception(
                        f"All elements must have 6 or 8 nodes. Element number {i + 1} has {len(elmnt)} nodes"
                    )

        self.__connectivity = connectivity

    def SetElementIds(self, elementIds):
        """Set the element id's. Optional. If not set, default values are used (1,2,3,...)"""
        if (self.__connectivity is not None) and (
            len(self.__connectivity) != elementIds.size
        ):
            raise Exception(
                "Number of element id's does not match number of elements", "elementIds"
            )

    def SetFromMeshFile(self, meshFile: MeshFile):
        """Set projection, nodes and elements from mesh file.
        This is equivalent to calling SetProjection, SetNodes, SetElements
        """
        wktString = meshFile.ProjectionString
        x, y, z, code = meshFile.X, meshFile.Y, meshFile.Z, meshFile.Code
        quantity = meshFile.EumQuantity
        if (
            wktString is None
            or x is None
            or y is None
            or z is None
            or code is None
            or quantity is None
        ):
            raise ValueError("Mesh file has no projection, nodes or quantity")
        self.__dfsProjection = DfsProjection.Create(wktString)

        self.__nodeIds = meshFile.NodeIds
        self.__nodes = MeshNodes(x, y, z.astype(dtype=np.float32), code)
        self.__zUnit = quantity.Unit

        self.__elementIds = meshFile.ElementIds
        self.__connectivity = meshFile.ElementTable

    def AddDynamicItem(self, itemName: str, quantity):
        """Add a dynamic item."""
        self.__dynamicItemData.append((itemName, quantity))

    def Validate(self, dieOnError: bool = False):
        """Validate will return a string of issues from the item builder.
        When this returns an empty list, the item has been properly build.
        """
        errors = []

        if self.__dfsProjection is None:
            errors.append("Projection has not been set")
        if not self.__isSetTimeInfo:
            errors.append("Time information has not been set")
        if self.__nodes is None:
            errors.append("Nodes have not been set")
        if self.__connectivity is None:
            errors.append("Elements have not been set")
        if not self.__isSetNumberOfSigmaLayers and self.__dfsuFileType in (
            DfsuFileType.Dfsu3DSigma,
            DfsuFileType.Dfsu3DSigmaZ,
            DfsuFileType.DfsuVerticalColumn,
            DfsuFileType.DfsuVerticalProfileSigma,
            DfsuFileType.DfsuVerticalProfileSigmaZ,
        ):
            errors.append("Number of sigma layers has not been set")

        if self.__nodes is None or self.__connectivity is None:
            # The remaining checks need nodes and elements.
            if dieOnError:
                raise Exception(DfsBuilder.ErrorMessage(errors))
            return errors
        numberOfNodes = self.__nodes.x.size
        connectivity = self.__connectivity

        # Check that all nodenumbers are within the range of
        # number of nodes.
        check = True
        for elmt in connectivity:
            for nodeNumber in elmt:
                if 0 >= nodeNumber or nodeNumber > numberOfNodes:
                    check = False
                    break
            if not check:
                break
        if not check:
            errors.append(
                "At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]"
            )

        # For vertical files, checking that elements are correctly on top of each other,
        # and calculate the maxNumberOfLayers
        # TODO: Need to check that node coordinates are also on top of each other?
        # TODO: Need to check that the 2D elements are defined counter-clockwise
        if self.__dfsuFileType == DfsuFileType.Dfsu2D:
            pass
        elif self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn:
            topLayerElements = DfsuUtil.FindTopLayerElements(connectivity)
            if len(topLayerElements) != 1:
                errors.append(
                    "Elements does not seem to be on top of each other. Element table is invalid"
                )
        elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma:
            topLayerElements = DfsuUtil.FindTopLayerElements(connectivity)
            maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(topLayerElements)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if (
                maxNumberOfLayers != self.__numberOfSigmaLayers
                or minNumberOfLayers != self.__numberOfSigmaLayers
            ):
                errors.append(
                    "The number of layers does not everywhere equal the number of sigma layers. Element table is invalid"
                )
        elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ:
            topLayerElements = DfsuUtil.FindTopLayerElements(connectivity)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if minNumberOfLayers < self.__numberOfSigmaLayers:
                errors.append(
                    "The minimum number of layers is smaller than the number of sigma layers. Element table is invalid"
                )
        elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigma:
            topLayerElements = DfsuUtil.FindTopLayerElements(connectivity)
            maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(topLayerElements)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if (
                maxNumberOfLayers != self.__numberOfSigmaLayers
                or minNumberOfLayers != self.__numberOfSigmaLayers
            ):
                errors.append(
                    "The number of layers does not everywhere equal the number of sigma layers. Element table is invalid"
                )
        elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ:
            topLayerElements = DfsuUtil.FindTopLayerElements(connectivity)
            minNumberOfLayers = DfsuUtil.FindMinNumberOfLayers(topLayerElements)
            if minNumberOfLayers < self.__numberOfSigmaLayers:
                errors.append(
                    "The minimum number of layers is smaller than the number of sigma layers. Element table is invalid"
                )
        elif self.__dfsuFileType in (
            DfsuFileType.DfsuSpectral0D,
            DfsuFileType.DfsuSpectral1D,
            DfsuFileType.DfsuSpectral2D,
        ):
            # TODO do we need to check frequency or directions?
            pass
        else:
            raise Exception(f"Dfsu file type {self.__dfsuFileType} not supported")

        if dieOnError and len(errors) > 0:
            msgs = DfsBuilder.ErrorMessage(errors)
            raise Exception(msgs)

        return errors

    def __NodesAndElements(self):
        """The nodes and the element connectivity, which must have been set."""
        if self.__nodes is None or self.__connectivity is None:
            raise Exception("Nodes and elements must be set")
        return self.__nodes, self.__connectivity

    def SetupConnectivityArrays(self):
        nodes, connectivity = self.__NodesAndElements()
        # Creating default node id's, if empty, node ids 1,2,3,...
        if self.__nodeIds is None:
            self.__nodeIds = np.arange(nodes.x.size, dtype=np.int32) + 1
        # Creating default element id's, if empty, element ids 1,2,3,...
        if self.__elementIds is None:
            self.__elementIds = np.arange(len(connectivity), dtype=np.int32) + 1

        # Creating additional element information
        elementType = np.zeros(len(connectivity), dtype=np.int32)
        nodesPerElmt = np.zeros(len(connectivity), dtype=np.int32)
        nodeElmtCount = 0  # total number of nodes listed in the connectivity table
        for i in range(elementType.size):
            elmt = connectivity[i]
            elmtsize = len(elmt)
            if elmtsize == 2:  # vertical column
                elmtTypeNumber = 11
            elif elmtsize == 3:  # triangle
                elmtTypeNumber = 21
            elif elmtsize == 4:  # quadrilateral
                elmtTypeNumber = 25
            elif elmtsize == 6:  # prisme (base element is a triangle)
                elmtTypeNumber = 32
            elif elmtsize == 8:  # Hexahedron (base element is a quadrilateral)
                elmtTypeNumber = 33
            else:
                # this should have been caught in the validate phase, but just in case:
                raise Exception("Element with invalid number of nodes encountered")
            elementType[i] = elmtTypeNumber
            nodesPerElmt[i] = len(elmt)
            nodeElmtCount += len(elmt)

        connectivityArray = np.zeros(nodeElmtCount, dtype=np.int32)
        k = 0
        for i in range(elementType.size):
            elmt = connectivity[i]
            for j in range(len(elmt)):
                connectivityArray[k] = elmt[j]
                k += 1

        return elementType, nodesPerElmt, connectivityArray

    def SetupBuilder(self):
        nodes, connectivity = self.__NodesAndElements()
        # Unset frequencies or directions are written as a count of 0
        numberOfFrequencies = (
            0 if self.__frequencies is None else len(self.__frequencies)
        )
        numberOfDirections = 0 if self.__directions is None else len(self.__directions)
        self.__zQuantity = eumQuantity(eumItem.eumIItemGeometry3D, self.__zUnit)

        factory = DfsFactory()
        dfsBuilder = DfsBuilder.Create(
            self.FileTitle, self.ApplicationTitle, self.ApplicationVersion
        )

        if self.__dfsuFileType == DfsuFileType.DfsuSpectral1D:
            dfsBuilder.SetDataType(2002)
        elif self.__dfsuFileType == DfsuFileType.DfsuSpectral2D:
            dfsBuilder.SetDataType(2003)
        else:
            dfsBuilder.SetDataType(2001)

        dfsBuilder.SetGeographicalProjection(self.__dfsProjection)
        if self.__timeAxis is not None:
            dfsBuilder.SetTemporalAxis(self.__timeAxis)
        else:
            dfsBuilder.SetTemporalAxis(
                factory.CreateTemporalEqCalendarAxis(
                    eumUnit.eumUsec, self.__startDateTime, 0, self.__timeStepInSeconds
                )
            )
        dfsBuilder.DeleteValueFloat = np.float32(1e-35)

        # Set up custom block
        if self.__dfsuFileType == DfsuFileType.Dfsu2D:
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array([nodes.x.size, len(connectivity), 2, 0, 0], np.int32),
            )
        elif self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn:
            maxNumberOfLayers = len(connectivity)
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        1,
                        maxNumberOfLayers,
                        self.__numberOfSigmaLayers,
                    ],
                    np.int32,
                ),
            )
        elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma:
            maxNumberOfLayers = self.__numberOfSigmaLayers
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        2,
                        maxNumberOfLayers,
                        self.__numberOfSigmaLayers,
                    ],
                    np.int32,
                ),
            )
        elif self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ:
            maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(
                DfsuUtil.FindTopLayerElements(connectivity)
            )
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        2,
                        maxNumberOfLayers,
                        self.__numberOfSigmaLayers,
                    ],
                    np.int32,
                ),
            )
        elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigma:
            maxNumberOfLayers = self.__numberOfSigmaLayers
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        3,
                        maxNumberOfLayers,
                        self.__numberOfSigmaLayers,
                    ],
                    np.int32,
                ),
            )
        elif self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ:
            maxNumberOfLayers = DfsuUtil.FindMaxNumberOfLayers(
                DfsuUtil.FindTopLayerElements(connectivity)
            )
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        3,
                        maxNumberOfLayers,
                        self.__numberOfSigmaLayers,
                    ],
                    np.int32,
                ),
            )
        elif self.__dfsuFileType == DfsuFileType.DfsuSpectral1D:
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        1,
                        0,
                        numberOfFrequencies,
                        numberOfDirections,
                    ],
                    np.int32,
                ),
            )
        elif self.__dfsuFileType == DfsuFileType.DfsuSpectral2D:
            dfsBuilder.AddCreateCustomBlock(
                "MIKE_FM",
                np.array(
                    [
                        nodes.x.size,
                        len(connectivity),
                        2,
                        0,
                        numberOfFrequencies,
                        numberOfDirections,
                    ],
                    np.int32,
                ),
            )
        else:
            raise Exception()

        # For the files with a vertical dimension, the first dynamic item is the Z-coordinate
        if (
            self.__dfsuFileType == DfsuFileType.DfsuVerticalColumn
            or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigma
            or self.__dfsuFileType == DfsuFileType.DfsuVerticalProfileSigmaZ
            or self.__dfsuFileType == DfsuFileType.Dfsu3DSigma
            or self.__dfsuFileType == DfsuFileType.Dfsu3DSigmaZ
        ):
            dfsItem = dfsBuilder.CreateDynamicItemBuilder()
            dfsItem.Set("Z coordinate", self.__zQuantity, DfsSimpleType.Float)
            dfsItem.SetValueType(DataValueType.Instantaneous)
            # Disabled to make the dfsu files exactly match those from the engine. Not necessary,
            # but enables binary compares
            # if (false):
            #  dfsItem.SetAxis(factory.CreateAxisDummy(len(connectivity)))
            # else
            # Set axis to have meter unit (not necessary, just to make file exactly equal)
            dfsItem.SetAxis(
                factory.CreateAxisEqD1(eumUnit.eumUmeter, nodes.x.size, 0, 1)
            )
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
            # if (false):
            #  dfsItem.SetAxis(factory.CreateAxisDummy(len(connectivity)))
            # else
            # Set axis to have meter unit (not necessary, just to make file exactly equal)

            if self.__dfsuFileType in (
                DfsuFileType.DfsuSpectral1D,
                DfsuFileType.DfsuSpectral2D,
            ):
                if self.__dfsuFileType == DfsuFileType.DfsuSpectral1D:
                    size = nodes.x.size
                else:
                    size = len(connectivity)

                if self.__frequencies is not None:
                    size *= numberOfFrequencies
                if self.__directions is not None:
                    size *= numberOfDirections

                dfsItem.SetAxis(factory.CreateAxisEqD1(eumUnit.eumUmeter, size, 0, 1))
            else:
                dfsItem.SetAxis(
                    factory.CreateAxisEqD1(eumUnit.eumUmeter, len(connectivity), 0, 1)
                )
            # Set to default ufs delete values (not used anyway, just to make file exactly equal)
            dfsItem.SetReferenceCoordinates(-1e-35, -1e-35, -1e-35)
            dfsItem.SetOrientation(-1e-35, -1e-35, -1e-35)
            dfsBuilder.AddDynamicItem(dfsItem.GetDynamicItemInfo())
        return dfsBuilder

    def CreateFile(self, filename: str):
        """Create and return a dfsu file"""

        self.Validate(dieOnError=True)
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

        nodes, connectivity = self.__NodesAndElements()
        intCode = eumQuantity(eumItem.eumIIntegerCode, eumUnit.eumUintCode)
        xyQuantity = eumQuantity(eumItem.eumIGeographicalCoordinate, eumUnit.eumUmeter)

        # TODO: reenable:
        # if (MapProjection.IsValid(self.__dfsProjection.WKTString)):
        #    if (MapProjection.IsGeographical(self.__dfsProjection.WKTString)):
        #        xyQuantity = eumQuantity(eumItem.eumILatLong, eumUnit.eumUdegree)

        # Node id
        nodeIdItem = dfsBuilder.AddCreateStaticItem("Node id", intCode, self.__nodeIds)

        # X-coord
        xItem = dfsBuilder.AddCreateStaticItem("X-coord", xyQuantity, nodes.x)

        # Y-coord
        yItem = dfsBuilder.AddCreateStaticItem("Y-coord", xyQuantity, nodes.y)

        # Z-coord
        zItem = dfsBuilder.AddCreateStaticItem("Z-coord", self.__zQuantity, nodes.z)

        # Code
        codeItem = dfsBuilder.AddCreateStaticItem("Code", intCode, nodes.code)

        # Element id
        elmtIdItem = dfsBuilder.AddCreateStaticItem(
            "Element id", intCode, self.__elementIds
        )

        # Element type
        elmtTypeItem = dfsBuilder.AddCreateStaticItem(
            "Element type", intCode, elementType
        )

        # No of nodes (per element)
        nodesPerElmtItem = dfsBuilder.AddCreateStaticItem(
            "No of nodes", intCode, nodesPerElmt
        )

        # Connectivity
        connectivityItem = dfsBuilder.AddCreateStaticItem(
            "Connectivity", intCode, connectivityArray
        )

        # Spectral
        frequencyItem = (
            dfsBuilder.AddCreateStaticItem(
                "Frequency",
                eumQuantity(eumItem.eumIFrequency, eumUnit.eumUhertz),
                self.__frequencies,
            )
            if self.__frequencies is not None
            else None
        )

        # TODO unit
        directionItem = (
            dfsBuilder.AddCreateStaticItem(
                "Direction",
                eumQuantity(eumItem.eumIDirection, eumUnit.eumUradian),
                self.__directions,
            )
            if self.__directions is not None
            else None
        )

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
            nodes.x,
            nodes.y,
            nodes.z,
            nodes.code,
            self.__elementIds,
            elementType,
            connectivity,
            self.__zUnit,
            frequencyItem,
            directionItem,
        )

        return dfsuFile

    @staticmethod
    def Create(fileType):
        """Create a new dfsu builder"""
        return DfsuBuilder(fileType)
