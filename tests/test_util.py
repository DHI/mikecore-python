import shutil
import os
import stat
from numpy.testing import assert_allclose, assert_equal


class testUtil:
    @staticmethod
    def copy_file(originalFilename, filename):
        shutil.copyfile(originalFilename, filename)
        # remove read-only flag
        mode = os.stat(filename).st_mode
        ro_mask = 777 ^ (stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
        os.chmod(filename, mode & ro_mask)


class Assert:
    @staticmethod
    def AreEqual(expected, actual, tol: float = 0):
        if tol == 0:
            assert_equal(actual, expected)
        else:
            # tol is relative, with the same value as an absolute floor for expected values near zero
            assert_allclose(actual, expected, rtol=tol, atol=tol)

    @staticmethod
    def IsNotNull(obj):
        if obj is None:
            raise Exception("Object is null")

    @staticmethod
    def IsNull(obj):
        if obj is not None:
            raise Exception("Object is not null")

    @staticmethod
    def IsTrue(obj):
        if not obj:
            raise Exception("Is not True")

    @staticmethod
    def IsFalse(obj):
        if obj:
            raise Exception("Is not False")

    @staticmethod
    def Fail(message):
        raise Exception(message)
