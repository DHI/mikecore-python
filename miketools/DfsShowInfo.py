import sys

from mikecore.DfsFile import *
from mikecore.DfsFileFactory import *


def DfsShowInfo(dfsFileName, showAxis=False):
    """Writes dfs info to console"""

    dfs = DfsFileFactory.DfsGenericOpen(dfsFileName)
    txt = sys.stdout

    txt.write(f"FileName            : {dfs.FileInfo.FileName!s:<40}\n")
    txt.write(f"FileTitle           : {dfs.FileInfo.FileTitle!s:<40}\n")
    txt.write(f"ApplicationTytle    : {dfs.FileInfo.ApplicationTitle!s:<40}\n")
    txt.write(f"ApplicationVersion  : {dfs.FileInfo.ApplicationVersion!s:<40}\n")
    txt.write(f"Projection          : {dfs.FileInfo.Projection.WKTString!s:<40}\n")
    txt.write(f"DataType            : {dfs.FileInfo.DataType!s:<40}\n")

    startDateTime = ""
    if (
        dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarEquidistant
        or dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarNonEquidistant
    ):
        isCalendarTime = True
        startDateTime = dfs.FileInfo.TimeAxis.StartDateTime
    txt.write(
        f"Time                : {dfs.FileInfo.TimeAxis.TimeAxisType}, {dfs.FileInfo.TimeAxis.NumberOfTimeSteps}, {startDateTime}\n"
    )

    for customBlock in dfs.FileInfo.CustomBlocks:
        txt.write(
            f"Custom Block        : {customBlock.Name}, {customBlock.Count}, {customBlock.Values}\n"
        )

    item = dfs.ReadStaticItemNext()
    if item is not None:
        txt.write("---- Static items  ---- \n")
    while item is not None:
        txt.write(
            f"item {item.ItemNumber!s:>2}: {item.Name!s:<40}: {item.ElementCount!s:>5}: {item.DataType.name!s:>6} ({item.Quantity.ItemDescription!s:>11}: {item.Quantity.UnitDescription!s:>11}) \n"
        )
        item = dfs.ReadStaticItemNext()

    txt.write("---- Dynamic items ---- \n")
    for item in dfs.ItemInfo:
        txt.write(
            f"item {item.ItemNumber!s:>2}: {item.Name!s:<40}: {item.ElementCount!s:>5}: {item.DataType.name!s:>6} {item.SpatialAxis.AxisType.name!s:>6} ({item.Quantity.ItemDescription!s:>11}: {item.Quantity.UnitDescription!s:>11}) \n"
        )
        if showAxis:
            if item.SpatialAxis.AxisType is SpaceAxisType.EqD1:
                txt.write(
                    f"  axis : dx = {item.SpatialAxis.Dx}, xCount = {item.SpatialAxis.XCount}, x0 = {item.SpatialAxis.X0} ({item.SpatialAxis.AxisUnit.name})\n"
                )

    dfs.Close()


def DfsuShowInfo(dfsFileName, showMesh=False):
    """Writes dfsu info to console"""

    dfs = DfsFileFactory.DfsuFileOpen(dfsFileName)
    txt = sys.stdout

    txt.write(f"FileName            : {dfs.FileInfo.FileName!s:<40}\n")
    txt.write(f"FileTitle           : {dfs.FileInfo.FileTitle!s:<40}\n")
    txt.write(f"ApplicationTytle    : {dfs.FileInfo.ApplicationTitle!s:<40}\n")
    txt.write(f"ApplicationVersion  : {dfs.FileInfo.ApplicationVersion!s:<40}\n")
    txt.write(f"Projection          : {dfs.FileInfo.Projection.WKTString!s:<40}\n")
    txt.write(f"DataType            : {dfs.FileInfo.DataType!s:<40}\n")

    startDateTime = ""
    if (
        dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarEquidistant
        or dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarNonEquidistant
    ):
        isCalendarTime = True
        startDateTime = dfs.FileInfo.TimeAxis.StartDateTime
    txt.write(
        f"Time                : {dfs.FileInfo.TimeAxis.TimeAxisType}, {dfs.FileInfo.TimeAxis.NumberOfTimeSteps}, {startDateTime}\n"
    )

    txt.write(f"DfsuFileType        : {dfs.DfsuFileType}\n")
    txt.write(f"Nodes               : {len(dfs.NodeIds)}\n")
    txt.write(f"Elements            : {len(dfs.ElementIds)}\n")
    txt.write(f"NodesPerElement     : {len(dfs.ElementTable[0])}\n")
    txt.write(f"NumberOfLayers      : {dfs.NumberOfLayers}\n")
    txt.write(f"NumberOfSigmaLayers : {dfs.NumberOfSigmaLayers}\n")
    if dfs.IsSpectral:
        txt.write(f"NumberOfFrequencies : {dfs.NumberOfFrequencies}\n")
        txt.write(f"NumberOfDirections  : {dfs.NumberOfDirections}\n")

    for customBlock in dfs.FileInfo.CustomBlocks:
        txt.write(
            f"Custom Block        : {customBlock.Name}, {customBlock.Count}, {customBlock.Values}\n"
        )

    txt.write("---- Dynamic items ---- \n")
    for item in dfs.ItemInfo:
        txt.write(
            f"item {item.ItemNumber!s:>2}: {item.Name!s:<40}: {item.ElementCount!s:>5}: {item.DataType.name!s:>6} ({item.Quantity.ItemDescription!s:>11}: {item.Quantity.UnitDescription!s:>11}) \n"
        )

    if showMesh:
        txt.write("---- Nodes ------------ \n")
        for i in range(len(dfs.NodeIds)):
            txt.write(
                f"node {i + 1!s:>4}: {dfs.X[i]!s:>20}: {dfs.Y[i]!s:>20}: {dfs.Z[i]!s:>20} \n"
            )
        txt.write("---- Elmts ------------ \n")
        for i in range(len(dfs.ElementTable)):
            txt.write(f"elmt {i + 1!s:>4}: {dfs.ElementTable[i]} \n")
        if dfs.NumberOfFrequencies > 0:
            txt.write(
                f"---- Freq: {dfs.NumberOfFrequencies!s:>2} ---------\n{dfs.Frequencies} \n"
            )
        if dfs.NumberOfDirections > 0:
            txt.write(
                f"---- Dirs: {dfs.NumberOfDirections!s:>2} ---------\n{dfs.Directions} \n"
            )

    dfs.Close()
