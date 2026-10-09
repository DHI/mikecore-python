from datetime import timedelta
from mikecore.DfsFile import *
from mikecore.DfsFileFactory import *


def Dfs0ToAscii(dfs0FileName, txtFileName):
    """Writes dfs0 data to text file in similar format as other MIKE Zero tools"""

    dfs = DfsFileFactory.DfsGenericOpen(dfs0FileName)
    txt = open(txtFileName, "w")

    txt.write(" ")
    txt.write(dfs.FileInfo.FileTitle)
    txt.write("\n")

    txt.write(" Time")
    for item in dfs.ItemInfo:
        txt.write(f"    {item.Name}")
    txt.write("\n")

    txt.write(" Item")
    for item in dfs.ItemInfo:
        txt.write(
            f" {item.Quantity.Item.value:11} {item.Quantity.Unit.value:11} {item.ValueType.name:11}"
        )
    txt.write("\n")
    txt.write(" Item")
    for item in dfs.ItemInfo:
        txt.write(
            " {:11} {:11} {:11}".format(
                '"' + item.Quantity.ItemDescription + '"',
                '"' + item.Quantity.UnitDescription + '"',
                item.ValueType.name,
            )
        )
    txt.write("\n")

    # Only set for calendar time axes; otherwise times are written as offsets.
    startDateTime = None
    if (
        dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarEquidistant
        or dfs.FileInfo.TimeAxis.TimeAxisType == TimeAxisType.CalendarNonEquidistant
    ):
        startDateTime = dfs.FileInfo.TimeAxis.StartDateTime

    for i in range(dfs.FileInfo.TimeAxis.NumberOfTimeSteps):
        for j in range(len(dfs.ItemInfo)):
            itemData = dfs.ReadItemTimeStepNext()
            if itemData is None:
                raise Exception(
                    f"Could not read item {j + 1} at timestep index {i} from {dfs0FileName}"
                )
            if j == 0:
                if startDateTime is not None:
                    # TODO: Time unit is not always seconds
                    itemTime = startDateTime + timedelta(seconds=itemData.Time)
                    # Depending on the format to write to the file:
                    # txt.write(itemTime.strftime("%Y-%m-%d %H:%M:%S"));         # Seconds accuracy
                    txt.write(
                        itemTime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    )  # Milli-seconds accuracy
                    # txt.write(itemTime.strftime("%Y-%m-%d %H:%M:%S.%f"));      # Micro-seconds accuracy
                else:
                    txt.write(f"{itemData.Time:19.6E}")

            txt.write(f" {itemData.Data[0]:18.11E}")

        txt.write("\n")

    dfs.Close()
    txt.close()
