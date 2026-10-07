from typing import Optional
from mikecore.DfsFile import DfsFile, DfsFileMode, DfsItemData

class Dfs123File(DfsFile):
    def __init__(self):
        super().__init__()
        self.SpatialAxis = None
        self.reshape = False

    def Open(self, filename, mode = DfsFileMode.Read, parameters=None, reshape=False):
        super().Open(filename, mode, parameters)
        self.reshape = reshape
        # TODO: Need to check that this is the same for all items
        if (len(self.ItemInfo) > 0):
            self.SpatialAxis = self.ItemInfo[0].SpatialAxis;

    def Reshape(self, reshape):
        # Set True to reshape item data to multi-dimensional arrays.
        self.reshape = reshape

    def ReadItemTimeStepNext(self, itemData: Optional[DfsItemData] = None, reshape: bool = False) -> Optional[DfsItemData]:
        return super().ReadItemTimeStepNext(itemData, self.reshape or reshape)

class Dfs2File(Dfs123File):
    pass

class Dfs3File(Dfs123File):
    pass
