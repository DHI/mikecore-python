import unittest
from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.DfsFile import *
from numpy.testing import *
from tests.test_util import *

class Test_dfs_custom_block(unittest.TestCase):

    def test_dfs2(self):
        dfsFile = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfs2")

        assert_equal(1, len(dfsFile.FileInfo.CustomBlocks))

        customBlock = dfsFile.FileInfo.CustomBlocks[0];
        assert_equal("M21_Misc", customBlock.Name);
        assert_equal(DfsSimpleType.Float, customBlock.SimpleType);
        assert_equal(7, len(customBlock.Values));
        assert_equal(327, customBlock.Values[0])    # Orientation - matching that in the projection info
        assert_allclose(0.2, customBlock.Values[1]) # Drying depth
        assert_equal(-900, customBlock.Values[2])   # -900 = contains geographic information (projection)
        assert_equal(10, customBlock.Values[3]);    # Land value
        assert_equal(0, customBlock.Values[4]);
        assert_equal(0, customBlock.Values[5]);
        assert_equal(0, customBlock.Values[6]);

        dfsFile.Close()

    def test_dfsu(self):
        dfsFile = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

        assert_equal(1, len(dfsFile.FileInfo.CustomBlocks))

        customBlock = dfsFile.FileInfo.CustomBlocks[0];
        assert_equal(DfsSimpleType.Int, customBlock.SimpleType);
        assert_equal("MIKE_FM", customBlock.Name);
        assert_equal(5, len(customBlock.Values));
        assert_equal(2057, customBlock.Values[0]);
        assert_equal(3636, customBlock.Values[1]);
        assert_equal(2, customBlock.Values[2]);
        assert_equal(0, customBlock.Values[3]);
        assert_equal(0, customBlock.Values[4]);


        dfsFile.Close()

    def test_UpdateCustomBlockDataTest(self):

        originalFilename = "testdata/OresundHD.dfs2";
        filename = "testdata/testtmp/test_copy_OresundHD_cb.dfs2";

        testUtil.copy_file(originalFilename, filename)

        # Check initial value
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        fileInfo = dfsFile.FileInfo;
        customBlock = fileInfo.CustomBlocks[0];
        assert_equal(10, customBlock.Values[3]);
        dfsFile.Close();

        # Modify value
        dfsFile = DfsFileFactory.DfsGenericOpenEdit(filename);
        fileInfo = dfsFile.FileInfo;
        customBlock = fileInfo.CustomBlocks[0];
        customBlock.Values[3] = 25;
        dfsFile.Close();

        # Check new value
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        fileInfo = dfsFile.FileInfo;
        customBlock = fileInfo.CustomBlocks[0];
        assert_equal(25, customBlock.Values[3]);
        dfsFile.Close();
