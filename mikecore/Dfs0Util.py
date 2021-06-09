import os
import numpy as np

from mikecore.DfsFile import DfsSimpleType

class Dfs0Util:
    @staticmethod
    def ReadDfs0DataDouble(dfs0File):
        if os.name == 'nt':
            res = dfs0File.ReadDfs0DataDouble()
            return res.astype(np.float64)

        # not windows... 
        itemCount = len(dfs0File.ItemInfo)
        timestepCount = dfs0File.FileInfo.TimeAxis.NumberOfTimeSteps
        res = np.zeros(shape=(timestepCount, itemCount + 1), dtype=np.float64)

        # Preload a set of item data
        itemDatas = []
        for j in range(itemCount):
            itemDatas.append(dfs0File.CreateEmptyItemData(j + 1))

        dfs0File.Reset()

        # Check if time axis is really a time axis, or if it is a non-time axis
        # timeAxisType = dfs0File.FileInfo.TimeAxis.TimeAxisType
        # timeUnit = dfs0File.FileInfo.TimeAxis.TimeUnit
        # isTimeUnit = timeUnit == eumUnit.eumUsec

        for i in range(timestepCount):

            for j in range(itemCount):

                itemData = itemDatas[j]
                dfs0File.ReadItemTimeStep(itemData, i)
                # First column is time, remaining colums are data
                if j == 0:
                    res[i, 0] = itemData.Time

                res[i, j + 1] = itemData.Data[0]

        return res.astype(np.float64)

    @staticmethod
    def WriteDfs0TimeDataDouble(dfs0File, times, data):

        itemCount = len(dfs0File.ItemInfo)

        if len(times) != data.shape[0]:
            raise ValueError("Number of time steps does not match number of data rows")

        if itemCount != data.shape[1]:
            raise ValueError("Number of items does not match number of data columns")

        isFloatItem = []
        for j in range(itemCount):
            isFloatItem.append(dfs0File.ItemInfo[j].DataType == DfsSimpleType.Float)

        fdata = np.array([0], np.float32)
        ddata = np.array([0], np.float64)

        for i in range(len(times)):
            for j in range(itemCount):
                if isFloatItem[j]:
                    fdata[0] = data[i, j]
                    dfs0File.WriteItemTimeStepNext(times[i], fdata)
                else:
                    ddata[0] = data[i, j]
                    dfs0File.WriteItemTimeStepNext(times[i], ddata)

    @staticmethod
    def WriteDfs0DataDouble(dfs0File, data):

        itemCount = len(dfs0File.ItemInfo)

        if itemCount != data.shape[1]-1:
            raise ValueError("Number of items does not match number of data columns")

        isFloatItem = []
        for j in range(itemCount):
            isFloatItem.append(dfs0File.ItemInfo[j].DataType == DfsSimpleType.Float)

        fdata = np.array([0], np.float32)
        ddata = np.array([0], np.float64)

        for i in range(data.shape[0]):
            time = data[i,0];
            for j in range(itemCount):
                if isFloatItem[j]:
                    fdata[0] = data[i, j+1]
                    dfs0File.WriteItemTimeStepNext(time, fdata)
                else:
                    ddata[0] = data[i, j+1]
                    dfs0File.WriteItemTimeStepNext(time, ddata)
