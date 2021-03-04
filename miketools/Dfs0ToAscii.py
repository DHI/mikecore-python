from datetime import datetime, timedelta;
from mikecore.DfsFile import *;
from mikecore.DfsFileFactory import *;

def Dfs0ToAscii(dfs0FileName, txtFileName):
    '''Writes dfs0 data to text file in similar format as other MIKE Zero tools  '''

    dfs = DfsFileFactory.DfsGenericOpen(dfs0FileName)
    txt = open                         (txtFileName,"w")
    
    txt.write(" "); 
    txt.write(dfs.FileInfo.FileTitle); 
    txt.write("\n"); 

    txt.write(" Time"); 
    for item in dfs.ItemInfo:
        txt.write('    {}'.format(item.Name)); 
    txt.write("\n"); 

    txt.write(" Item"); 
    for item in dfs.ItemInfo:
        txt.write(' {:11} {:11} {:11}'.format(item.Quantity.Item.value, item.Quantity.Unit.value, item.ValueType.name)); 
    txt.write("\n"); 
    txt.write(" Item"); 
    for item in dfs.ItemInfo:
        txt.write(' {:11} {:11} {:11}'.format('"'+item.Quantity.ItemDescription+'"', '"'+item.Quantity.UnitDescription+'"', item.ValueType.name)); 
    txt.write("\n"); 

    isCalendarTime = False;
    if (dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarEquidistant or \
        dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarNonEquidistant):
        isCalendarTime = True;
        startDateTime = dfs.FileInfo.TimeAxis.StartDateTime;

    for i in range (dfs.FileInfo.TimeAxis.NumberOfTimeSteps):
        for j in range(len(dfs.ItemInfo)):
            itemData = dfs.ReadItemTimeStepNext();
            if (j == 0):
                if (isCalendarTime):
                    # TODO: Time unit is not always seconds
                    itemTime = startDateTime + timedelta(seconds=itemData.Time)
                    # Depending on the format to write to the file:
                    #txt.write(itemTime.strftime("%Y-%m-%d %H:%M:%S"));         # Seconds accuracy
                    txt.write(itemTime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]); # Milli-seconds accuracy
                    #txt.write(itemTime.strftime("%Y-%m-%d %H:%M:%S.%f"));      # Micro-seconds accuracy
                else:
                    txt.write('{:19.6E}'.format(itemData.Time));

            txt.write(' {:18.11E}'.format(itemData.Data[0])); 

        txt.write("\n"); 

    dfs.Close();
    txt.close();


