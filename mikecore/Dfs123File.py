from mikecore.DfsFile import DfsFile, DfsFileMode, DfsItemData


class Dfs123File(DfsFile):
    def __init__(self):
        super().__init__()
        self.SpatialAxis = None
        self.reshape = False

    def Open(self, filename, mode=DfsFileMode.Read, parameters=None, reshape=False):
        super().Open(filename, mode, parameters)
        self.reshape = reshape
        # TODO: Need to check that this is the same for all items
        if len(self.ItemInfo) > 0:
            self.SpatialAxis = self.ItemInfo[0].SpatialAxis

    def Reshape(self, reshape):
        # Set True to reshape item data to multi-dimensional arrays.
        self.reshape = reshape

    def ReadItemTimeStepNext(
        self, itemData: DfsItemData | None = None, reshape: bool = False
    ) -> DfsItemData | None:
        return self.__Reshaped(super().ReadItemTimeStepNext(itemData), reshape)

    def ReadItemTimeStep(
        self,
        itemNumber: int | DfsItemData,
        timestepIndex: int,
        reshape: bool = False,
    ) -> DfsItemData | None:
        return self.__Reshaped(
            super().ReadItemTimeStep(itemNumber, timestepIndex), reshape
        )

    def __Reshaped(self, res: DfsItemData | None, reshape: bool) -> DfsItemData | None:
        # Reshaping an array that already has the axis shape leaves it unchanged
        if res is not None and (self.reshape or reshape):
            res.Data = res.Data.reshape(self.SpatialAxis.Shape, order="F")
        return res


class Dfs2File(Dfs123File):
    pass


class Dfs3File(Dfs123File):
    pass
