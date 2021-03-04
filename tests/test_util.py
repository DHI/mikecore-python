import shutil
import os
import stat
import unittest
from numpy.testing import *

class testUtil:

    @staticmethod
    def copy_file(originalFilename, filename):
        shutil.copyfile(originalFilename, filename);
        # remove read-only flag
        mode = os.stat(filename).st_mode
        ro_mask = 777 ^ (stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
        os.chmod(filename, mode & ro_mask) 

class Assert:
    @staticmethod
    def AreEqual(expected, actual, tol = 0):
        if (tol == 0):
            assert_equal(actual, expected)
        else:
            assert_allclose(actual, expected, tol)
    def IsNotNull(obj):
        if (obj is None):
            raise Exception("Object is null")
    def IsNull(obj):
        if (not obj is None):
            raise Exception("Object is not null")
    def IsTrue(obj):
        if (not obj):
            raise Exception("Is not True")
    def IsFalse(obj):
        if (obj):
            raise Exception("Is not False")
