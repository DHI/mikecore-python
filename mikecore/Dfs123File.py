import copy

from mikecore.DfsFile import DfsFile, DfsFileMode, DfsItemData


class Dfs123File(DfsFile):
    def __init__(self):
        super().__init__()
        self.SpatialAxis = None
        self.reshape = False
        self._spatialAxisUpdated = False

    def Open(self, filename, mode=DfsFileMode.Read, parameters=None, reshape=False):
        super().Open(filename, mode, parameters)
        self.reshape = reshape
        self._spatialAxisUpdated = False
        # TODO: Need to check that this is the same for all items
        if len(self.ItemInfo) > 0:
            self.SpatialAxis = copy.copy(self.ItemInfo[0].SpatialAxis)
            if self.SpatialAxis is not None:
                self.SpatialAxis._OnUpdate = None
                if mode in (DfsFileMode.Edit, DfsFileMode.Append):
                    self.SpatialAxis._OnUpdate = self.__SpatialAxisUpdated

    def __SpatialAxisUpdated(self):
        self._spatialAxisUpdated = True

    def __WriteSpatialAxis(self, staticItems):
        """
        Write a changed SpatialAxis to all dynamic items, and with
        staticItems to the static items with the same type of axis, as the
        C# library does. Writing static items moves the file pointer.
        """
        fileAxis = self.SpatialAxis
        if not self._spatialAxisUpdated or fileAxis is None:
            return
        for itemInfo in self.ItemInfo:
            itemInfo.SpatialAxis._Update(fileAxis)
        if not staticItems:
            return
        self._spatialAxisUpdated = False
        self.Reset()
        staticItemNo = 1
        while (staticItem := self.ReadStaticItem(staticItemNo)) is not None:
            staticItemNo += 1
            axis = staticItem.SpatialAxis
            data = staticItem.Data
            if axis is None or data is None or axis.AxisType != fileAxis.AxisType:
                continue
            axis._Update(fileAxis)
            self.WriteStaticItemData(staticItem, data)

    def Flush(self):
        """
        Flush cached data to the file. A changed SpatialAxis is written to the
        dynamic items here, and to the static items only on Close: writing a
        static item moves the file pointer, so a time step appended after
        Flush would overwrite another. The C# library writes both on Flush.
        """
        if self.filePointer.value is not None:
            self.__WriteSpatialAxis(staticItems=False)
        super().Flush()

    def Close(self):
        try:
            if self.filePointer.value is not None:
                self.__WriteSpatialAxis(staticItems=True)
        finally:
            self._spatialAxisUpdated = False
            if self.SpatialAxis is not None:
                self.SpatialAxis._OnUpdate = None
            super().Close()

    def Reshape(self, reshape):
        # Set True to reshape item data to multi-dimensional arrays.
        self.reshape = reshape

    def ReadItemTimeStepNext(
        self, itemData: DfsItemData | None = None, reshape: bool = False
    ) -> DfsItemData | None:
        res = super().ReadItemTimeStepNext(itemData)
        if res is not None and (self.reshape or reshape):
            res.Data = res.Data.reshape(self.SpatialAxis.Shape, order="F")
        return res


class Dfs2File(Dfs123File):
    pass


class Dfs3File(Dfs123File):
    pass
