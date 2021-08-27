from datetime import datetime
from mikecore.DfsFileFactory import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *


class ExamplesMisc:
    '''
    Misc examples
    '''

    @staticmethod
    def CopyDfsFile(sourceFilename, filename):
      '''Example of how to copy a Dfs file.'''

      source = DfsFileFactory.DfsGenericOpen(sourceFilename);
      fileInfo = source.FileInfo;

      builder = DfsBuilder.Create(fileInfo.FileTitle, fileInfo.ApplicationTitle, fileInfo.ApplicationVersion);

      # Set up the header
      builder.SetDataType(fileInfo.DataType);
      builder.SetGeographicalProjection(fileInfo.Projection);
      builder.SetTemporalAxis(fileInfo.TimeAxis);
      builder.SetItemStatisticsType(fileInfo.StatsType);
      builder.DeleteValueByte = fileInfo.DeleteValueByte;
      builder.DeleteValueDouble = fileInfo.DeleteValueDouble;
      builder.DeleteValueFloat = fileInfo.DeleteValueFloat;
      builder.DeleteValueInt = fileInfo.DeleteValueInt;
      builder.DeleteValueUnsignedInt = fileInfo.DeleteValueUnsignedInt;

      # Transfer compression keys - if any.
      if (fileInfo.IsFileCompressed):
        (xkey, ykey, zkey) = fileInfo.GetEncodeKey();
        builder.SetEncodingKey(xkey, ykey, zkey);

      # Copy custom blocks - if any
      for customBlock in fileInfo.CustomBlocks:
        builder.AddCustomBlock(customBlock);

      # Copy dynamic items
      for itemInfo in source.ItemInfo:
        builder.AddDynamicItem(itemInfo);

      # Create file
      builder.CreateFile(filename);

      # Copy static items
      sourceStaticItem = source.ReadStaticItemNext();
      while None != sourceStaticItem:
        builder.AddStaticItem(sourceStaticItem);
        sourceStaticItem = source.ReadStaticItemNext();

      # Get the file
      file = builder.GetFile();

      # Copy dynamic item data
      sourceData = source.ReadItemTimeStepNext();
      while None != sourceData:
        file.WriteItemTimeStepNext(sourceData.Time, sourceData.Data);
        sourceData = source.ReadItemTimeStepNext();

      source.Close();
      file.Close();
