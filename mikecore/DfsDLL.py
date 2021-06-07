import os
import ctypes
from enum import IntEnum

class DfsError(IntEnum):
    F_NO_ERROR            = 0
    F_END_OF_FILE         = 1

    F_FAIL_DATA           = 1000
    F_FAIL_ILLEGEAL_TSTEP = 1001
    F_FAIL_ILLEGEAL_ITEM  = 1002

    F_ERR_MALLOC          = 2000
    F_ERR_READ            = 2001
    F_ERR_WRITE           = 2002
    F_ERR_OPEN            = 2003
    F_ERR_CLOSE           = 2004
    F_ERR_FLUSH           = 2005
    F_ERR_SEEK            = 2006
    F_ERR_ITEMNO          = 2007
    F_ERR_INDEX           = 2008
    F_ERR_DTYPE           = 2009
    F_ERR_DATA            = 2010
    F_ERR_DATE_FORMAT     = 2011
    F_ERR_TIME_FORMAT     = 2012
    F_ERR_SIZE            = 2013
    F_ERR_TAG             = 2014
    F_ERR_READONLY        = 2015
    F_ERR_SKIP            = 2016
    F_ERR_APPTAG          = 2017
    F_ERR_AXIS            = 2018
    F_ERR_CTYPE           = 2019
    F_ERR_EUM             = 2020
    F_ERR_NOT_DTX         = 2021
    F_ERR_PLUGIN          = 2022


class DfsDLL:
    """description of class"""

    # Static variables
    Wrapper = None
    MCCUWrapper = None

    @staticmethod
    def Init(libfilepath=None):

        # ufs lib should be loaded only once
        if DfsDLL.Wrapper is None:

            DfsDLL.libfilepath = None
            if not libfilepath is None:
                DfsDLL.libfilepath = libfilepath

            # TODO: On linux, this looks different!
            if os.name == "nt":
                DfsDLL.Wrapper = ctypes.CDLL(os.path.join(DfsDLL.libfilepath, "ufs.dll"))
            else:
                DfsDLL.Wrapper = ctypes.CDLL(os.path.join(DfsDLL.libfilepath, "libufs.so"))
            DfsDLL.Wrapper.dfsInitSystem()

            DfsDLL.Wrapper.dfsGetAppTitle.argtypes = [ctypes.c_void_p]
            DfsDLL.Wrapper.dfsGetAppTitle.restype = ctypes.c_char_p
            DfsDLL.Wrapper.dfsGetDeleteValFloat.restype = ctypes.c_float
            DfsDLL.Wrapper.dfsGetDeleteValByte.restype = ctypes.c_int8
            DfsDLL.Wrapper.dfsGetDeleteValDouble.restype = ctypes.c_double
            DfsDLL.Wrapper.dfsGetDeleteValInt.restype = ctypes.c_int32
            DfsDLL.Wrapper.dfsGetDeleteValUnsignedInt.restype = ctypes.c_uint32
            DfsDLL.Wrapper.dfsGetFileTitle.argtypes = [ctypes.c_void_p]
            DfsDLL.Wrapper.dfsGetFileTitle.restype = ctypes.c_char_p
            DfsDLL.Wrapper.dfsGetItemValueType.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_int),
            ]
            DfsDLL.Wrapper.dfsGetCustomBlockRef.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]

            DfsDLL.Wrapper.dfsItemD.argtypes = [ctypes.c_void_p, ctypes.c_int]
            DfsDLL.Wrapper.dfsItemD.restype = ctypes.c_void_p
            DfsDLL.Wrapper.dfsItemS.argtypes = [ctypes.c_void_p]
            DfsDLL.Wrapper.dfsItemS.restype = ctypes.c_void_p
            DfsDLL.Wrapper.dfsGetItemInfo.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_int),
            ]
            DfsDLL.Wrapper.dfsGetItemInfo_.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_int),
            ]
            DfsDLL.Wrapper.dfsGetItemElements.argtypes = [ctypes.c_void_p]

            DfsDLL.Wrapper.dfsGetEqTimeAxis.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_int32),
                ctypes.POINTER(ctypes.c_int32),
            ]
            DfsDLL.Wrapper.dfsGetNeqTimeAxis.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_int32),
                ctypes.POINTER(ctypes.c_int32),
            ]
            DfsDLL.Wrapper.dfsGetEqCalendarAxis.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_int32),
                ctypes.POINTER(ctypes.c_int32),
            ]
            DfsDLL.Wrapper.dfsGetNeqCalendarAxis.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_int32),
                ctypes.POINTER(ctypes.c_int32),
            ]

            # Last argument is just a pointer to the memory that can be many different types, though mostly
            DfsDLL.Wrapper.dfsReadItemTimeStep.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_double),
                ctypes.c_void_p,
            ]
            DfsDLL.Wrapper.dfsReadItemTimeStep.restype = ctypes.c_int32
            DfsDLL.Wrapper.dfsWriteItemTimeStep.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_double,
                ctypes.c_void_p,
            ]
            DfsDLL.Wrapper.dfsWriteItemTimeStep.restype = ctypes.c_int32

            DfsDLL.Wrapper.dfsStaticRead.argtypes = [
                ctypes.c_void_p, 
                ctypes.POINTER(ctypes.c_int)
            ]
            DfsDLL.Wrapper.dfsStaticRead.restype = ctypes.c_void_p
            DfsDLL.Wrapper.dfsStaticSetHeader.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]
            DfsDLL.Wrapper.dfsStaticSetHeader.restype = ctypes.c_int32
            DfsDLL.Wrapper.dfsStaticGetData.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]
            DfsDLL.Wrapper.dfsStaticGetData.restype = ctypes.c_int32
            DfsDLL.Wrapper.dfsStaticWrite.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]

            DfsDLL.Wrapper.dfsAddCustomBlock.argtypes = [
                ctypes.c_void_p,
                ctypes.c_int32,
                ctypes.c_char_p,
                ctypes.c_int32,
                ctypes.c_void_p,
            ]

        # MIKE Core C Util should be loaded only once and only on Windows
        if DfsDLL.MCCUWrapper is None and os.name == "nt":
            DfsDLL.MCCUWrapper = ctypes.CDLL(os.path.join(DfsDLL.libfilepath, "MIKECoreCUtil.dll"))

            DfsDLL.MCCUWrapper.ReadDfs0DataDouble.restype = ctypes.c_int32
            DfsDLL.MCCUWrapper.ReadDfs0DataDouble.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]
            DfsDLL.MCCUWrapper.ReadDfs0ItemsDouble.restype = ctypes.c_int32
            DfsDLL.MCCUWrapper.ReadDfs0ItemsDouble.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int32,
            ]
            DfsDLL.MCCUWrapper.WriteDfs0DataDouble.restype = ctypes.c_int32
            DfsDLL.MCCUWrapper.WriteDfs0DataDouble.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int32,
            ]



    @staticmethod
    def dfsErrorString(error : DfsError):
      if error == DfsError.F_NO_ERROR:
        return ("");
      if error == DfsError.F_END_OF_FILE:
        return ("End of file was reached");
      if error == DfsError.F_FAIL_DATA:
        return ("Failed reading/writing/setting data from/to the file. Data is wrong, file is corrupt, not a DFS file or handled incorrectly, or data is invalid");
      if error == DfsError.F_FAIL_ILLEGEAL_TSTEP:
        return ("The time step number is out of range");
      if error == DfsError.F_FAIL_ILLEGEAL_ITEM:
        return ("The item number is out of range");
      if error == DfsError.F_ERR_MALLOC:
        return ("Error allocating memory");
      if error == DfsError.F_ERR_READ:
        return ("Error reading file. Common reasons: File has zero size, file is open in write-only mode, disc is corrupt");
      if error == DfsError.F_ERR_WRITE:
        return ("Error writing data to disc. Common reasons: Disc is full, filename is invalid, not enough available memory (for write buffers)");
      if error == DfsError.F_ERR_OPEN:
        return ("Error opening file. Filename is invalid, or header could not be read (corrupt, or not a DFS file)");
      if error == DfsError.F_ERR_CLOSE:
        return ("Error closing file");
      if error == DfsError.F_ERR_FLUSH:
        return ("Error flushing data to disc. Disc/quota may be full");
      if error == DfsError.F_ERR_SEEK:
        return ("Error seeking in file. File has been truncated or disc is corrupt");
      if error == DfsError.F_ERR_ITEMNO:
        return ("An item number is out of range");
      if error == DfsError.F_ERR_INDEX:
        return ("An index number is out of range");
      if error == DfsError.F_ERR_DTYPE:
        return ("A data type does not match (internal error). File is most likely corrupt");
      if error == DfsError.F_ERR_DATA:
        return ("Error in file data, file is most likely corrupt");
      if error == DfsError.F_ERR_DATE_FORMAT:
        return ("Date format is invalid. Must be YYYY-MM-dd");
      if error == DfsError.F_ERR_TIME_FORMAT:
        return ("Time format is invalid. Must be hh:mm:ss");
      if error == DfsError.F_ERR_SIZE:
        return ("A size does not match (internal error). File is most likely corrupt");
      if error == DfsError.F_ERR_TAG:
        return ("Error reading DHI DFS tag (DHI_). Most likely file is not a DFS file");
      if error == DfsError.F_ERR_READONLY:
        return ("Trying to write to a file in read-only mode");
      if error == DfsError.F_ERR_SKIP:
        return (" Error skipping a logical block (internal error). Most likely file is corrupt");
      if error == DfsError.F_ERR_APPTAG:
        return (" Error reading DHI DFS API tag (DFS_). Most likely file is not a DFS file");
      if error == DfsError.F_ERR_AXIS:
        return ("Wrong axis type number (internal error). Most likely the file is corrupt");
      if error == DfsError.F_ERR_CTYPE:
        return ("Error reading logical block type (internal error). Most likely the file is corrupt");
      if error == DfsError.F_ERR_EUM:
        return ("EUM unit and type does not match");
      if error == DfsError.F_ERR_NOT_DTX:
        return ("File is not a dtx file, though loaded as such");
      if error == DfsError.F_ERR_PLUGIN:
        return ("Plugin extension error");
      return ("Unknown error");

    @staticmethod
    def CheckReturnCode(rc):
        if (rc != 0):
            errorDescr = DfsDLL.dfsErrorString(rc);
            raise Exception("DFS error code " +str(rc)+ " : " + errorDescr );


