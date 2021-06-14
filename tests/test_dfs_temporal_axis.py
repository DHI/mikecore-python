import unittest
from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.DfsFile import *
from numpy.testing import *
from shutil import copyfile
from tests.test_util import *

class Test_dfs_temporal_axis(unittest.TestCase):

    def test_ModifyEqCalTest(self):
        sourcefilename = "testdata/TemporalEqCal.dfs0";
        filename = "testdata/testtmp/test_temporal_modifyEqCal.dfs0";

        testUtil.copy_file(sourcefilename, filename)

        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        timeAxis = dfsFile.FileInfo.TimeAxis;

        assert_equal(0, timeAxis.FirstTimeStepIndex);
        assert_equal(4, timeAxis.StartTimeOffset);
        assert_equal(eumUnit.eumUsec, timeAxis.TimeUnit);
        assert_equal(datetime.datetime(2010, 1, 4, 12, 34, 00), timeAxis.StartDateTime);
        assert_equal(10, timeAxis.TimeStep);

        dfsFile.Close();


        # Update temporal axis
        dfsFile = DfsFileFactory.DfsGenericOpenEdit(filename);
        timeAxis = dfsFile.FileInfo.TimeAxis;

        timeAxis.FirstTimeStepIndex = 3;
        timeAxis.StartTimeOffset = 6;
        timeAxis.StartDateTime = datetime.datetime(2009, 2, 2, 21, 43, 00);
        timeAxis.TimeUnit = eumUnit.eumUminute;
        timeAxis.TimeStep = 1;

        dfsFile.Close();


        # Load file from disc again, and check time axis
        dfsFile = DfsFileFactory.DfsGenericOpen(filename);
        timeAxis = dfsFile.FileInfo.TimeAxis;

        assert_equal(3, timeAxis.FirstTimeStepIndex);
        assert_equal(6, timeAxis.StartTimeOffset);
        assert_equal(eumUnit.eumUminute, timeAxis.TimeUnit);
        assert_equal(datetime.datetime(2009, 2, 2, 21, 43, 00), timeAxis.StartDateTime); 
        assert_equal(1, timeAxis.TimeStep);
          
        dfsFile.Close();
