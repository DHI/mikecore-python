import unittest
from datetime import datetime
from mikecore.DfsFileFactory import *
from mikecore.DfsBuilder import *
from mikecore.DfsFactory import *
from mikecore.DfsFile import *
from mikecore.eum import *
from numpy.testing import *
from tests.examples_dfs2 import *
from tests.examples_misc import *
from tests.test_util import *


class Dfs3Tests(unittest.TestCase):
    '''
    Class for testing functionality related to dfs2 files.
    '''

    def test_EncodeKeys(self):

        # Name of the file to open
        filename = "testdata/OresundHD.dfs3";
        # Open the file as a dfs3 file
        dfs3File = DfsFileFactory.Dfs3FileOpen(filename);
        dfs3File.Reshape(True);
        
        (xKey,yKey,zKey) = dfs3File.FileInfo.GetEncodeKey()
        # Check the first 10 encoding key values
        xsExpected = np.array([ 62, 62, 62, 66, 60, 62, 66, 66, 60, 62 ], dtype=np.int32);
        ysExpected = np.array([ 64, 64, 64, 87, 55, 64, 86, 87, 55, 64 ], dtype=np.int32);
        zsExpected = np.array([  3,  4,  5,  5,  6,  6,  6,  6,  7,  7 ], dtype=np.int32);
        Assert.AreEqual(xsExpected, xKey[:10]);
        Assert.AreEqual(ysExpected, yKey[:10]);
        Assert.AreEqual(zsExpected, zKey[:10]);

        dfs3File.Close();

    def test_CopyDfs3(self):
        ''' Test that we can read and write a complete dfs3 file '''
        filename = "testdata/OresundHD.dfs3";
        filenameCopy = "testdata/testtmp/test_copy_OresundHD.dfs3";

        ExamplesMisc.CopyDfsFile(filename,filenameCopy)
        