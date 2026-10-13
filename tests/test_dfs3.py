import unittest
from mikecore.DfsFileFactory import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *
from tests.examples_dfs2 import *
from tests.examples_misc import *
from tests.test_util import *


class Dfs3Tests(unittest.TestCase):
    """
    Class for testing functionality related to dfs2 files.
    """

    def test_EncodeKeys(self):

        # Name of the file to open
        filename = "testdata/OresundHD.dfs3"
        # Open the file as a dfs3 file
        dfs3File = DfsFileFactory.Dfs3FileOpen(filename)
        dfs3File.Reshape(True)

        (xKey, yKey, zKey) = dfs3File.FileInfo.GetEncodeKey()
        # Check the first 10 encoding key values
        xsExpected = np.array([62, 62, 62, 66, 60, 62, 66, 66, 60, 62], dtype=np.int32)
        ysExpected = np.array([64, 64, 64, 87, 55, 64, 86, 87, 55, 64], dtype=np.int32)
        zsExpected = np.array([3, 4, 5, 5, 6, 6, 6, 6, 7, 7], dtype=np.int32)
        Assert.AreEqual(xsExpected, xKey[:10])
        Assert.AreEqual(ysExpected, yKey[:10])
        Assert.AreEqual(zsExpected, zKey[:10])

        dfs3File.Close()

    def test_CopyDfs3(self):
        """Test that we can read and write a complete dfs3 file"""
        filename = "testdata/OresundHD.dfs3"
        filenameCopy = "testdata/testtmp/test_copy_OresundHD.dfs3"

        ExamplesMisc.CopyDfsFile(filename, filenameCopy)

    def test_ModifyItemInfoTest(self):
        originalFilename = "testdata/OresundHD.dfs3"
        filename = "testdata/testtmp/test_modifyItemInfo_OresundHD.dfs3"

        testUtil.copy_file(originalFilename, filename)

        # Check existing data
        file = DfsFileFactory.Dfs3FileOpen(filename)
        assert_equal("U velocity [m/s]", file.ItemInfo[0].Name)
        assert_equal(eumItem.eumIFlowVelocity, file.ItemInfo[0].Quantity.Item)
        assert_equal(eumUnit.eumUmeterPerSec, file.ItemInfo[0].Quantity.Unit)
        assert_equal("V velocity [m/s]", file.ItemInfo[1].Name)
        file.Close()

        file = DfsFileFactory.Dfs3FileOpenEdit(filename)
        file.ItemInfo[0].Name = "U"
        file.ItemInfo[0].Quantity = eumQuantity(
            eumItem.eumIuVelocity, eumUnit.eumUfeetPerSec
        )
        file.Close()

        # Check the new file, the name is padded to the old length
        file = DfsFileFactory.Dfs3FileOpen(filename)
        assert_equal("U               ", file.ItemInfo[0].Name)
        assert_equal(eumItem.eumIuVelocity, file.ItemInfo[0].Quantity.Item)
        assert_equal(eumUnit.eumUfeetPerSec, file.ItemInfo[0].Quantity.Unit)
        assert_equal("V velocity [m/s]", file.ItemInfo[1].Name)
        file.Close()

    def test_ModifyAxisTest(self):
        originalFilename = "testdata/OresundHD.dfs3"
        filename = "testdata/testtmp/test_modifyAxis_OresundHD.dfs3"

        testUtil.copy_file(originalFilename, filename)

        def axisValues(axis):
            return (axis.X0, axis.Dx, axis.Y0, axis.Dy, axis.Z0, axis.Dz)

        def readStaticItems(file):
            staticItems = []
            while (staticItem := file.ReadStaticItemNext()) is not None:
                staticItems.append(staticItem)
            return staticItems

        # Check existing data
        file = DfsFileFactory.Dfs3FileOpen(filename)
        assert_equal((0, 900, 0, 900, 0, 1), axisValues(file.SpatialAxis))
        assert_equal(4, len(file.ItemInfo))
        for itemInfo in file.ItemInfo:
            assert_equal((0, 900, 0, 900, 0, 1), axisValues(itemInfo.SpatialAxis))
        sourceStaticItems = readStaticItems(file)
        assert_equal(2, len(sourceStaticItems))
        for staticItem in sourceStaticItems:
            assert_equal((0, 900, 0, 900, 0, 1), axisValues(staticItem.SpatialAxis))
        file.Close()

        file = DfsFileFactory.Dfs3FileOpenEdit(filename)
        axis = file.SpatialAxis
        assert axis is not None
        axis.X0 = 55
        axis.Dx = 905
        axis.Y0 = -55
        axis.Dy = 915
        axis.Z0 = 5
        axis.Dz = 2
        file.Close()

        # Check all dynamic and static items
        file = DfsFileFactory.Dfs3FileOpen(filename)
        assert_equal((55, 905, -55, 915, 5, 2), axisValues(file.SpatialAxis))
        for itemInfo in file.ItemInfo:
            assert_equal((55, 905, -55, 915, 5, 2), axisValues(itemInfo.SpatialAxis))
        staticItems = readStaticItems(file)
        assert_equal(2, len(staticItems))
        for staticItem, sourceStaticItem in zip(
            staticItems, sourceStaticItems, strict=True
        ):
            assert_equal((55, 905, -55, 915, 5, 2), axisValues(staticItem.SpatialAxis))
            # Writing the axis keeps the static item data of the encoded file
            assert_equal(sourceStaticItem.Data, staticItem.Data)
        file.Close()
