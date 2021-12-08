import sys;
from datetime import datetime, timedelta;
from mikecore.DfsFile import *;
from mikecore.DfsFileFactory import *;

def DfsShowInfo(dfsFileName, showAxis = False):
    '''Writes dfs info to console '''

    dfs = DfsFileFactory.DfsGenericOpen(dfsFileName)
    txt = sys.stdout

    txt.write('FileName            : %-40s\n' % (dfs.FileInfo.FileName)); 
    txt.write('FileTitle           : %-40s\n' % (dfs.FileInfo.FileTitle)); 
    txt.write('ApplicationTytle    : %-40s\n' % (dfs.FileInfo.ApplicationTitle)); 
    txt.write('ApplicationVersion  : %-40s\n' % (dfs.FileInfo.ApplicationVersion)); 
    txt.write('Projection          : %-40s\n' % (dfs.FileInfo.Projection.WKTString)); 
    txt.write('DataType            : %-40s\n' % (dfs.FileInfo.DataType)); 

    startDateTime = '';
    if (dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarEquidistant or \
        dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarNonEquidistant):
        isCalendarTime = True;
        startDateTime = dfs.FileInfo.TimeAxis.StartDateTime;
    txt.write('Time                : %s, %s, %s\n' % (dfs.FileInfo.TimeAxis.TimeAxisType, dfs.FileInfo.TimeAxis.NumberOfTimeSteps, startDateTime)); 
    
    for customBlock in dfs.FileInfo.CustomBlocks:
        txt.write('Custom Block        : %s, %s, %s\n' % (customBlock.Name, customBlock.Count, customBlock.Values)); 

    item = dfs.ReadStaticItemNext();
    if None != item:
        txt.write('---- Static items  ---- \n'); 
    while None != item:
        txt.write('item %2s: %-40s: %5s: %6s (%11s: %11s) \n' % (item.ItemNumber, item.Name, item.ElementCount, item.DataType.name, item.Quantity.ItemDescription, item.Quantity.UnitDescription)); 
        item = dfs.ReadStaticItemNext();

    txt.write('---- Dynamic items ---- \n'); 
    for item in dfs.ItemInfo:
        txt.write('item %2s: %-40s: %5s: %6s %6s (%11s: %11s) \n' % (item.ItemNumber, item.Name, item.ElementCount, item.DataType.name, item.SpatialAxis.AxisType.name, item.Quantity.ItemDescription, item.Quantity.UnitDescription)); 
        if showAxis:
            if item.SpatialAxis.AxisType is SpaceAxisType.EqD1:
              txt.write('  axis : dx = %s, xCount = %s, x0 = %s (%s)\n' % (item.SpatialAxis.Dx, item.SpatialAxis.XCount, item.SpatialAxis.X0, item.SpatialAxis.AxisUnit.name)); 

    dfs.Close();


def DfsuShowInfo(dfsFileName, showMesh = False):
    '''Writes dfsu info to console '''

    dfs = DfsFileFactory.DfsuFileOpen(dfsFileName)
    txt = sys.stdout
    
    txt.write('FileName            : %-40s\n' % (dfs.FileInfo.FileName)); 
    txt.write('FileTitle           : %-40s\n' % (dfs.FileInfo.FileTitle)); 
    txt.write('ApplicationTytle    : %-40s\n' % (dfs.FileInfo.ApplicationTitle)); 
    txt.write('ApplicationVersion  : %-40s\n' % (dfs.FileInfo.ApplicationVersion)); 
    txt.write('Projection          : %-40s\n' % (dfs.FileInfo.Projection.WKTString)); 
    txt.write('DataType            : %-40s\n' % (dfs.FileInfo.DataType)); 

    startDateTime = '';
    if (dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarEquidistant or \
        dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarNonEquidistant):
        isCalendarTime = True;
        startDateTime = dfs.FileInfo.TimeAxis.StartDateTime;
    txt.write('Time                : %s, %s, %s\n' % (dfs.FileInfo.TimeAxis.TimeAxisType, dfs.FileInfo.TimeAxis.NumberOfTimeSteps, startDateTime)); 
    
    txt.write('DfsuFileType        : %s\n' % (dfs.DfsuFileType)); 
    txt.write('Nodes               : %s\n' % (len(dfs.NodeIds))); 
    txt.write('Elements            : %s\n' % (len(dfs.ElementIds))); 
    txt.write('NodesPerElement     : %s\n' % (len(dfs.ElementTable[0]))); 
    txt.write('NumberOfLayers      : %s\n' % (dfs.NumberOfLayers)); 
    txt.write('NumberOfSigmaLayers : %s\n' % (dfs.NumberOfSigmaLayers)); 
    if (dfs.IsSpectral):
        txt.write('NumberOfFrequencies : %s\n' % (dfs.NumberOfFrequencies)); 
        txt.write('NumberOfDirections  : %s\n' % (dfs.NumberOfDirections)); 

    for customBlock in dfs.FileInfo.CustomBlocks:
        txt.write('Custom Block        : %s, %s, %s\n' % (customBlock.Name, customBlock.Count, customBlock.Values)); 

    txt.write('---- Dynamic items ---- \n'); 
    for item in dfs.ItemInfo:
        txt.write('item %2s: %-40s: %5s: %6s (%11s: %11s) \n' % (item.ItemNumber, item.Name, item.ElementCount, item.DataType.name, item.Quantity.ItemDescription, item.Quantity.UnitDescription)); 

    if showMesh:
        txt.write('---- Nodes ------------ \n'); 
        for i in range(len(dfs.NodeIds)):
            txt.write('node %4s: %20s: %20s: %20s \n' % (i+1, dfs.X[i], dfs.Y[i], dfs.Z[i])); 
        txt.write('---- Elmts ------------ \n'); 
        for i in range(len(dfs.ElementTable)):
            txt.write('elmt %4s: %s \n' % (i+1, dfs.ElementTable[i])); 
        if dfs.NumberOfFrequencies > 0:
            txt.write('---- Freq: %2s ---------\n%s \n' % (dfs.NumberOfFrequencies, dfs.Frequencies)); 
        if dfs.NumberOfDirections > 0:
            txt.write('---- Dirs: %2s ---------\n%s \n' % (dfs.NumberOfDirections, dfs.Directions)); 

    dfs.Close();


