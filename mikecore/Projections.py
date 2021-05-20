import os
import ctypes
from typing import Tuple
import numpy as np
from enum import Enum, IntEnum


class ProjectionException(Exception):
  pass

  #/ <summary>
  #/ Abstract (static) class providing one-to-one access to the methods in 
  #/ MzCart.dll, using C# calling conventions and marshalling. 
  #/ </summary>
  #/ <remarks>
  #/ The class changes the following behavior compared to the MzCart.dll:
  #/ - Methods with an error return code throws an exception on error
  #/ - Methods with just one return argument now returns the value
  #/ - Unmanaged arrays (strings) are Marshalled
  #/ </remarks>
class MzCartDLL():

    # Static variables
    Wrapper = None

    _cartCreateCount = 0;
    _cartDestroyCount = 0;
    _projCreateCount = 0;
    _projDestroyCount = 0;
    _converterCreateCount = 0;
    _converterDestroyCount = 0;

    @staticmethod
    def Init(libfilepath: str = None):

        # ufs lib should be loaded only once
        if MzCartDLL.Wrapper is None:

            MzCartDLL.libfilepath = None
            if not libfilepath is None:
                MzCartDLL.libfilepath = libfilepath

            # TODO: On linux, this looks different!
            if os.name == "nt":
                MzCartDLL.Wrapper = ctypes.CDLL(os.path.join(MzCartDLL.libfilepath, "MzCart.dll"))
            else:
                MzCartDLL.Wrapper = ctypes.CDLL(os.path.join(MzCartDLL.libfilepath, "libMzCart.so"))
                libfilepathe = MzCartDLL.libfilepath+"/";
                libfilepatheP = ctypes.c_char_p(libfilepathe.encode("ascii"))
                MzCartDLL.Wrapper.CARTSETUPLINUX(libfilepatheP, libfilepatheP);


            MzCartDLL.Wrapper.C_MZC_GETPROJECTION.restype = ctypes.c_void_p;
            MzCartDLL.Wrapper.C_MZC_GETPROJECTIONSTRING.restype = None;
            MzCartDLL.Wrapper.S_GETGOOGLEMAPPROJECTIONSTRING.restype = None;

            MzCartDLL.Wrapper.C_MZC_CREATE.restype = None;
            MzCartDLL.Wrapper.C_MZC_DESTROY.restype = None;
            MzCartDLL.Wrapper.C_MZC_GETPROJNORTH.restype = ctypes.c_double;
            MzCartDLL.Wrapper.C_MZC_GETTRUENORTH.restype = ctypes.c_double;
            MzCartDLL.Wrapper.C_MZC_GEO2PROJ.restype = None;
            MzCartDLL.Wrapper.C_MZC_PROJ2GEO.restype = None;
            MzCartDLL.Wrapper.C_MZC_GEO2XY.restype = None;
            MzCartDLL.Wrapper.C_MZC_XY2GEO.restype = None;
            MzCartDLL.Wrapper.C_MZC_PROJ2XY.restype = None;
            MzCartDLL.Wrapper.C_MZC_XY2PROJ.restype = None;

            MzCartDLL.Wrapper.C_MZMP_CREATE.restype = None;
            MzCartDLL.Wrapper.C_MZMP_DESTROY.restype = None;
            MzCartDLL.Wrapper.C_MZMP_GETNAME.restype = None;
            MzCartDLL.Wrapper.C_MZMP_GETPROJECTIONSTRING.restype = None;
            MzCartDLL.Wrapper.C_MZMP_GEO2PROJ.restype = None;
            MzCartDLL.Wrapper.C_MZMP_PROJ2GEO.restype = None;
            MzCartDLL.Wrapper.C_MZMP_GETORIGIN.restype = None;
            MzCartDLL.Wrapper.C_MZMP_GETCONVERGENCE.restype = ctypes.c_double;
            MzCartDLL.Wrapper.C_MZMP_GETDEFAULTAREA.restype = None;
            MzCartDLL.Wrapper.C_MZMP_GEO2XYZ.restype = None;
            MzCartDLL.Wrapper.C_MZMP_XYZ2GEO.restype = None;

            MzCartDLL.Wrapper.C_MZDC_CREATE.restype = None;
            MzCartDLL.Wrapper.C_MZDC_DESTROY.restype = None;
            MzCartDLL.Wrapper.C_MZDC_CONVERTXY.restype = None;
            MzCartDLL.Wrapper.C_MZDC_INVCONVERTXY.restype = None;
            MzCartDLL.Wrapper.C_MZDC_CONVERTXYH.restype = None;
            MzCartDLL.Wrapper.C_MZDC_INVCONVERTXYH.restype = None;
            MzCartDLL.Wrapper.C_MZDC_DATUMSHIFT.restype = None;
            MzCartDLL.Wrapper.C_MZDC_BYPASSXYZ.restype = None;
            MzCartDLL.Wrapper.C_MZDC_RESETBYPASSXYZ.restype = None;
            MzCartDLL.Wrapper.C_MZDC_SETDATUMSHIFT.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_void_p, ctypes.c_int32];
            MzCartDLL.Wrapper.C_MZDC_SETDATUMSHIFT.restype = None;
            MzCartDLL.Wrapper.C_MZDC_INVERTORDER.restype = None;

            MzCartDLL.Wrapper.S_LONGITUDETOUTMZONE.restype = None;
            MzCartDLL.Wrapper.S_PROJECTIONSHORTNAME.restype = None;
            MzCartDLL.Wrapper.S_PROJECTIONORIGIN.restype = None;

    ################################/
    #region MzCartography methods
    # ReSharper disable InconsistentNaming

    #/ <summary>
    #/ Create a new cartography class and return the pointer to it.
    #/ <para>
    #/ Remember to call <see cref="MzCartDestroy"/> on it in order to free
    #/ ressources that it has allocated.
    #/ </para>
    #/ </summary>
    #/ <param name="projstring">A string the the WKT format for a spatial reference system</param>
    #/ <param name="lon">Longitude coordinate of the local grid origin</param>
    #/ <param name="lat">Latitude coordinate of the local grid origin</param>
    #/ <param name="ori">Orientation of the cartography class grid, rotation clockwise from geographical north</param>
    @staticmethod
    def MzCartCreate(projstring: str, lon: float, lat: float, ori: float) -> ctypes.c_void_p:
      # TODO: should this require a license?
      rc = ctypes.c_int32();
      mzCartPointer = ctypes.c_void_p();
      MzCartDLL.Wrapper.C_MZC_CREATE(
          ctypes.c_char_p(projstring.encode("ascii")), 
          ctypes.c_double(lon), 
          ctypes.c_double(lat), 
          ctypes.c_double(ori), 
          ctypes.byref(mzCartPointer), 
          ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not create cartography object. Is projection string valid?");
      if (mzCartPointer.value is None):
        raise ProjectionException("Could not create cartography object. Is projection string valid?");
      MzCartDLL._cartCreateCount += 1;
      return (mzCartPointer);

    #/ <summary>
    #/ Destroy the cartography object pointer to by the <paramref name="mzCartPointer"/>.
    #/ <para>
    #/ After this methods has been called, the <paramref name="mzCartPointer"/> will
    #/ be set to <see cref="IntPtr.Zero"/>.
    #/ </para>
    #/ <para>
    #/ The pointer must have been created by using the <see cref="MzCartCreate"/> method.
    #/ </para>
    #/ </summary>
    @staticmethod
    def MzCartDestroy(mzCartPointer: ctypes.c_void_p):
      if (mzCartPointer.value is None):
        return;
      rc = ctypes.c_int32();
      MzCartDLL._cartDestroyCount += 1;
      MzCartDLL.Wrapper.C_MZC_DESTROY(ctypes.byref(mzCartPointer), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not destroy cartography object. Probably invalid pointer argument");

    #/ <summary>
    #/ <para>
    #/ USE WITH CARE!
    #/ </para>
    #/ <para>
    #/ Returns a pointer to the MzMapProjection that the cartography
    #/ object uses.
    #/ </para>
    #/ <para>
    #/ Note that the map projection object is deleted when the cartography object is.
    #/ Hence, you should not call destroy on this pointer, and you should not
    #/ use this pointer after destroy have been called on the cartography pointer.
    #/ </para>
    #/ </summary>
    @staticmethod
    def MzCartGetMapProjection(mzCartPointer: ctypes.c_void_p) -> ctypes.c_void_p:
        return ctypes.c_void_p(MzCartDLL.Wrapper.C_MZC_GETPROJECTION(mzCartPointer));


    #/ <summary>
    #/ Returns the name of the projection of the cartography object 
    #/ pointed to by the <paramref name="mzCartPointer"/>
    #/ </summary>
    @staticmethod
    def MzCartProjectionName(mzCartPointer: ctypes.c_void_p) -> str:
      if (mzCartPointer.value is None):
        raise ValueError("Pointer is null", "mzCartPointer");
      rc = ctypes.c_int32();
      projName = ctypes.c_char_p((" " * 1024).encode("ascii"))
      MzCartDLL.Wrapper.C_MZC_GETPROJECTIONNAME(mzCartPointer, projName, ctypes.c_int32(1024), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        projName = ctypes.c_char_p((" " * (rc.value + 1)).encode("ascii"))
        MzCartDLL.Wrapper.C_MZC_GETPROJECTIONNAME(mzCartPointer, projName, rc.value + 1, ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get projection name from cartography object");
      return (projName.value.decode("ascii"));

    #/ <summary>
    #/ Returns the WKT projection string, or one of the projection abbreviation strings 
    #/ of the cartography object pointed to by the <paramref name="mzCartPointer"/>
    #/ </summary>
    @staticmethod
    def MzCartProjectionString(mzCartPointer: ctypes.c_void_p) -> str:
      if (mzCartPointer.value is None):
        raise ValueError("Pointer is null", "mzCartPointer");
      rc = ctypes.c_int32();
      projName = ctypes.c_char_p((" " * 2048).encode("ascii"));
      MzCartDLL.Wrapper.C_MZC_GETPROJECTIONSTRING(mzCartPointer, projName, ctypes.c_int32(2048), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        projName = ctypes.c_char_p((" " * (rc.value + 1)).encode("ascii"));
        MzCartDLL.Wrapper.C_MZC_GETPROJECTIONSTRING(mzCartPointer, projName, ctypes.c_int32(rc.value+1), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get projection string from cartography object");
      return (projName.value.decode("ascii"));

    #/ <summary>
    #/ Returns the google map projection string
    #/ </summary>
    @staticmethod
    def GoogleMapProjectionString() -> str:
      rc = ctypes.c_int32();
      googleMapProjection = ctypes.c_char_p((" " * 2048).encode("ascii"));
      S_GETGOOGLEMAPPROJECTIONSTRING(googleMapProjection, ctypes.c_int(2048), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        googleMapProjection = ctypes.c_char_p((" " * (rc.value+1)).encode("ascii"));
        S_GETGOOGLEMAPPROJECTIONSTRING(googleMapProjection, ctypes.c_int32(rc.value+1), ctypes.byref(rc));
      if (rc != 0):
        raise ProjectionException("Could not get google map projection string from cartography object");
      return (googleMapProjection.value.decode("ascii"));


    #/ <summary>
    #/ Return the angle between true north and a line parallel to the 
    #/ local grid.
    #/ </summary>
    @staticmethod
    def MzCartProjectionNorth(mzCartPointer: ctypes.c_void_p) -> float:
        return MzCartDLL.Wrapper.C_MZC_GETPROJNORTH(mzCartPointer)

    #/ <summary>
    #/ Returns the angle between true north and a line parallel to the 
    #/ local grid passing through (x,y).
    #/ </summary>
    @staticmethod
    def MzCartTrueNorth(mzCartPointer: ctypes.c_void_p, x: float, y: float) -> float:
        return MzCartDLL.Wrapper.C_MZC_GETTRUENORTH(mzCartPointer, ctypes.c_double(x), ctypes.c_double(y))

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to projection coordinates
    #/ </summary>
    @staticmethod
    def MzCartGeo2Proj(mzCartPointer: ctypes.c_void_p, lon: float, lat: float) -> Tuple[float,float]:
        east = ctypes.c_double() 
        north = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZC_GEO2PROJ(mzCartPointer, 
                                         ctypes.c_double(lon), ctypes.c_double(lat),
                                         ctypes.byref(east), ctypes.byref(north))
        return east.value, north.value;

    #/ <summary>
    #/ Convert coordinates from projection coordinates to geographical coordinates 
    #/ </summary>
    @staticmethod
    def MzCartProj2Geo(mzCartPointer: ctypes.c_void_p, east: float, north: float) -> Tuple[float,float]:
        lon = ctypes.c_double() 
        lat = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZC_PROJ2GEO(mzCartPointer, 
                                         ctypes.c_double(east), ctypes.c_double(north),
                                         ctypes.byref(lon), ctypes.byref(lat))
        return lon.value, lat.value;

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to local grid x-y coordinates
    #/ </summary>
    @staticmethod
    def MzCartGeo2Xy(mzCartPointer: ctypes.c_void_p, lon: float, lat: float) -> Tuple[float,float]:
        x = ctypes.c_double() 
        y = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZC_GEO2XY(mzCartPointer, 
                                         ctypes.c_double(lon), ctypes.c_double(lat),
                                         ctypes.byref(x), ctypes.byref(y))
        return x.value, y.value;

    #/ <summary>
    #/ Convert coordinates from local grid x-y coordinates to geographical coordinates 
    #/ </summary>
    @staticmethod
    def MzCartXy2Geo(mzCartPointer: ctypes.c_void_p, x: float, y: float) -> Tuple[float,float]:
        lon = ctypes.c_double() 
        lat = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZC_XY2GEO(mzCartPointer, 
                                         ctypes.c_double(x), ctypes.c_double(y),
                                         ctypes.byref(lon), ctypes.byref(lat))
        return lon.value, lat.value;

    #/ <summary>
    #/ Convert coordinates from projetion coordinates to local grid x-y coordinates
    #/ </summary>
    @staticmethod
    def MzCartProj2Xy(mzCartPointer: ctypes.c_void_p, east: float, north: float) -> Tuple[float,float]:
        x = ctypes.c_double() 
        y = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZC_PROJ2XY(mzCartPointer, 
                                         ctypes.c_double(east), ctypes.c_double(north),
                                         ctypes.byref(x), ctypes.byref(y))
        return x.value, y.value;

    #/ <summary>
    #/ Convert coordinates from local grid x-y coordinates to projection coordinates 
    #/ </summary>
    @staticmethod
    def MzCartXy2Proj(mzCartPointer: ctypes.c_void_p, x: float, y: float) -> Tuple[float,float]:
        east = ctypes.c_double() 
        north = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZC_XY2PROJ(mzCartPointer, 
                                         ctypes.c_double(x), ctypes.c_double(y),
                                         ctypes.byref(east), ctypes.byref(north))
        return east.value, north.value;

    # endregion


    ################################/
    #region MzMapProjection methods

    #/ <summary>
    #/ Create a new cartography class and return the pointer to it.
    #/ <para>
    #/ Remember to call <see cref="MzCartDestroy"/> on it in order to free
    #/ ressources that it has allocated.
    #/ </para>
    #/ </summary>
    #/ <param name="projstring">A string the the WKT format for a spatial reference system</param>
    @staticmethod
    def MzMapProjCreate(projstring: str) -> ctypes.c_void_p:
      # TODO: should this require a license?
      rc = ctypes.c_int32();
      mzMapProjPointer = ctypes.c_void_p();
      MzCartDLL.Wrapper.C_MZMP_CREATE(ctypes.c_char_p(projstring.encode("ascii")), ctypes.byref(mzMapProjPointer), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not create cartography object. Is projection string valid?");
      if (mzMapProjPointer.value is None):
        raise ProjectionException("Could not create cartography object. Is projection string valid?");
      MzCartDLL._projCreateCount += 1;
      return (mzMapProjPointer);

    #/ <summary>
    #/ Destroy the cartography object pointer to by the <paramref name="mzConverterPointer"/>.
    #/ <para>
    #/ After this methods has been called, the <paramref name="mzConverterPointer"/> will
    #/ be set to <see cref="IntPtr.Zero"/>.
    #/ </para>
    #/ <para>
    #/ The pointer must have been created by using the <see cref="MzCartCreate"/> method.
    #/ </para>
    #/ </summary>
    @staticmethod
    def MzMapProjDestroy(mzConverterPointer: ctypes.c_void_p):
      if (mzConverterPointer.value is None):
        return;
      rc = ctypes.c_int32();
      MzCartDLL._projDestroyCount += 1;
      MzCartDLL.Wrapper.C_MZMP_DESTROY(ctypes.byref(mzConverterPointer), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not destroy cartography object. Probably invalid pointer argument");

    #/ <summary>
    #/ Returns the name of the projection of the cartography object 
    #/ pointed to by the <paramref name="mzMapProjPointer"/>
    #/ </summary>
    @staticmethod
    def MzMapProjName(mzMapProjPointer: ctypes.c_void_p) -> str:
      if (mzMapProjPointer is None):
        raise Exception("Pointer is null", "mzMapProjPointer");
      rc = ctypes.c_int32();
      projName = ctypes.c_char_p((" " * 128).encode("ascii"));
      MzCartDLL.Wrapper.C_MZMP_GETNAME(mzMapProjPointer, projName, ctypes.c_int32(128), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        projName = ctypes.c_char_p((" " * (rc.value + 1)).encode("ascii"));
        MzCartDLL.Wrapper.C_MZMP_GETNAME(mzMapProjPointer, projName, ctypes.c_int32(rc.value+1), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get projection name from cartography object");
      return (projName.value.decode("ascii"));

    #/ <summary>
    #/ Returns the WKT projection string, or one of the projection abbreviation strings 
    #/ of the cartography object pointed to by the <paramref name="mzMapProjPointer"/>
    #/ </summary>
    @staticmethod
    def MzMapProjProjectionString(mzMapProjPointer: ctypes.c_void_p) -> str:
      if (mzMapProjPointer.value is None):
        raise Exception("Pointer is null", "mzMapProjPointer");
      rc = ctypes.c_int32();
      projName = ctypes.c_char_p((" " * 2048).encode("ascii"));
      MzCartDLL.Wrapper.C_MZMP_GETPROJECTIONSTRING(mzMapProjPointer, projName, ctypes.c_int32(2048), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        projName = ctypes.c_char_p((" " * (rc.value+1)).encode("ascii"));
        MzCartDLL.Wrapper.C_MZMP_GETPROJECTIONSTRING(mzMapProjPointer, projName, ctypes.c_int32(rc.value+1), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get projection string from cartography object");
      return (projName.value.decode("ascii"));

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to projection coordinates
    #/ </summary>
    @staticmethod
    def MzMapProjGeo2Proj(mzMapProjPointer: ctypes.c_void_p, lon: float, lat: float) -> Tuple[float,float]:
        east = ctypes.c_double() 
        north = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZMP_GEO2PROJ(mzMapProjPointer, 
                                         ctypes.c_double(lon), ctypes.c_double(lat),
                                         ctypes.byref(east), ctypes.byref(north))
        return east.value, north.value;

    #/ <summary>
    #/ Convert coordinates from projection coordinates to geographical coordinates 
    #/ </summary>
    @staticmethod
    def MzMapProjProj2Geo(mzMapProjPointer: ctypes.c_void_p, east: float, north: float) -> Tuple[float,float]:
        lon = ctypes.c_double() 
        lat = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZMP_PROJ2GEO(mzMapProjPointer, 
                                         ctypes.c_double(east), ctypes.c_double(north),
                                         ctypes.byref(lon), ctypes.byref(lat))
        return (lon.value, lat.value);


    #/ <summary>
    #/ Gets the geographical origin of the map projection
    #/ </summary>
    @staticmethod
    def MzMapProjGetOrigin(mzMapProjPointer: ctypes.c_void_p) -> Tuple[float,float]:
        lon = ctypes.c_double() 
        lat = ctypes.c_double() 
        MzCartDLL.Wrapper.C_MZMP_GETORIGIN(mzMapProjPointer, ctypes.byref(lon), ctypes.byref(lat))
        return (lon.value, lat.value);

    #/ <summary>
    #/ Gets the convergence (angle towards true north) at the given geographical location
    #/ </summary>
    @staticmethod
    def MzMapProjGetConvergence(mzMapProjPointer: ctypes.c_void_p, lon: float, lat: float) -> float:
        return MzCartDLL.Wrapper.C_MZMP_GETCONVERGENCE(mzMapProjPointer, ctypes.c_double(lon), ctypes.c_double(lat))

    #/ <summary>
    #/ Function that returns the default area in map projection coordinates of the projection.
    #/ </summary>
    @staticmethod
    def GetDefaultArea(mzMapProjPointer: ctypes.c_void_p) -> Tuple[float,float,float,float]:
        x0 = ctypes.c_double();
        y0 = ctypes.c_double();
        x1 = ctypes.c_double();
        y1 = ctypes.c_double();
        MzCartDLL.Wrapper.C_MZMP_GETDEFAULTAREA(mzMapProjPointer, 
                                                ctypes.byref(x0), ctypes.byref(y0),
                                                ctypes.byref(x1), ctypes.byref(y1))

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to 3D coordinates
    #/ </summary>
    @staticmethod
    def MzMapProjGeo2Xyz(mzMapProjPointer: ctypes.c_void_p, lon: float, lat: float, height: float) -> Tuple[float,float,float]:
        x = ctypes.c_double();
        y = ctypes.c_double();
        z = ctypes.c_double();
        MzCartDLL.Wrapper.C_MZMP_GEO2XYZ(mzMapProjPointer, 
                                         ctypes.c_double(lon), ctypes.c_double(lat), ctypes.c_double(height),
                                         ctypes.byref(x), ctypes.byref(y), ctypes.byref(z))
        return (x.value, y.value, z.value);

    #/ <summary>
    #/ Convert coordinates from 3D coordinates to geographical coordinates 
    #/ </summary>
    @staticmethod
    def MzMapProjXyz2Geo(mzMapProjPointer: ctypes.c_void_p, x: float, y: float, z: float) -> Tuple[float,float,float]:
        lon = ctypes.c_double();
        lat = ctypes.c_double();
        height = ctypes.c_double();
        MzCartDLL.Wrapper.C_MZMP_XYZ2GEO(mzMapProjPointer, 
                                         ctypes.c_double(x), ctypes.c_double(y), ctypes.c_double(z),
                                         ctypes.byref(lon), ctypes.byref(lat), ctypes.byref(height))
        return (lon.value, lat.value, height.value);

    #endregion


    ################################/
    #region MzDatumConverter methods

    #/ <summary>
    #/ Create a new datum converter class and return the pointer to it.
    #/ <para>
    #/ Remember to call <see cref="MzConverterDestroy"/> on it in order to free
    #/ ressources that it has allocated.
    #/ </para>
    #/ </summary>
    #/ <param name="projstringSource">A projection string in the WKT format for the source map projection</param>
    #/ <param name="projstringTarget">A projection string in the WKT format for the target map projection </param>
    @staticmethod
    def MzConverterCreate(projstringSource: str, projstringTarget: str) -> ctypes.c_void_p:
      rc = ctypes.c_int32();
      mzConverterPointer = ctypes.c_void_p();
      MzCartDLL.Wrapper.C_MZDC_CREATE(
          ctypes.c_char_p(projstringSource.encode("ascii")), 
          ctypes.c_char_p(projstringTarget.encode("ascii")), 
          ctypes.byref(mzConverterPointer), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not create converter object. are projection strings valid?");
      if (mzConverterPointer.value is None):
        raise ProjectionException("Could not create converter object. are projection strings valid?");
      MzCartDLL._converterCreateCount += 1;
      return (mzConverterPointer);

    #/ <summary>
    #/ Destroy the converter object pointer to by the <paramref name="mzConverterPointer"/>.
    #/ <para>
    #/ After this methods has been called, the <paramref name="mzConverterPointer"/> will
    #/ be set to <see cref="IntPtr.Zero"/>.
    #/ </para>
    #/ <para>
    #/ The pointer must have been created by using the <see cref="MzCartCreate"/> method.
    #/ </para>
    #/ </summary>
    @staticmethod
    def MzConverterDestroy(mzConverterPointer: ctypes.c_void_p):
      if (mzConverterPointer.value is None):
        return;
      rc = ctypes.c_int32();
      MzCartDLL._converterDestroyCount += 1;
      MzCartDLL.Wrapper.C_MZDC_DESTROY(ctypes.byref(mzConverterPointer), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not destroy converter object. Probably invalid pointer argument");


    #/ <summary>
    #/ Converts a point (x, y) from the source map projection to the target map projection
    #/ </summary>
    @staticmethod
    def MzConverterConvertXY(mzConverterPointer: ctypes.c_void_p, x: float, y: float) -> Tuple[float,float]:
        resx = ctypes.c_double(x);
        resy = ctypes.c_double(y);
        MzCartDLL.Wrapper.C_MZDC_CONVERTXY(mzConverterPointer, 
                                           ctypes.byref(resx), ctypes.byref(resy))
        return (resx.value, resy.value);
        
    #/ <summary>
    #/ Converts a point (x, y) from the target map projection to the source map projection.
    #/ </summary>
    @staticmethod
    def MzConverterInvConvertXY(mzConverterPointer: ctypes.c_void_p, x: float, y: float) -> Tuple[float,float]:
        resx = ctypes.c_double(x);
        resy = ctypes.c_double(y);
        MzCartDLL.Wrapper.C_MZDC_INVCONVERTXY(mzConverterPointer, 
                                              ctypes.byref(resx), ctypes.byref(resy))
        return (resx.value, resy.value);


    #/ <summary>
    #/ Converts a point (x, y, h) from the source map projection to the target map projection
    #/ </summary>
    @staticmethod
    def MzConverterConvertXYH(mzConverterPointer: ctypes.c_void_p, x: float, y: float, h: float) -> Tuple[float,float,float]:
        resx = ctypes.c_double(x);
        resy = ctypes.c_double(y);
        resh = ctypes.c_double(h);
        MzCartDLL.Wrapper.C_MZDC_CONVERTXYH(mzConverterPointer, 
                                            ctypes.byref(resx), ctypes.byref(resy), ctypes.byref(resh))
        return (resx.value, resy.value, resh.value);

    #/ <summary>
    #/ Converts a point (x, y, h) from the target map projection to the source map projection.
    #/ </summary>
    @staticmethod
    def MzConverterInvConvertXYH(mzConverterPointer: ctypes.c_void_p, x: float, y: float, h: float) -> Tuple[float,float,float]:
        resx = ctypes.c_double(x);
        resy = ctypes.c_double(y);
        resh = ctypes.c_double(h);
        MzCartDLL.Wrapper.C_MZDC_INVCONVERTXYH(mzConverterPointer, 
                                               ctypes.byref(resx), ctypes.byref(resy), ctypes.byref(resh))
        return (resx.value, resy.value, resh.value);


    #/ <summary>
    #/ Converts a point in Euclidean coordinates (x, y, z) relative to the source datum center to 
    #/ Euclidean coordinates relative to the target datum center
    #/ </summary>
    @staticmethod
    def MzConverterDatumShift(mzConverterPointer: ctypes.c_void_p, x: float, y: float, z: float) -> Tuple[float,float,float]:
        resx = ctypes.c_double(x);
        resy = ctypes.c_double(y);
        resz = ctypes.c_double(z);
        MzCartDLL.Wrapper.C_MZDC_DATUMSHIFT(mzConverterPointer, 
                                            ctypes.byref(resx), ctypes.byref(resy), ctypes.byref(resz))
        return (resx.value, resy.value, resz.value);

    #/ <summary>
    #/ Converts a point in Euclidean coordinates (x, y, z) relative to the target datum center to 
    #/ Euclidean coordinates relative to the source datum center
    #/ </summary>
    @staticmethod
    def MzConverterInvDatumShift(mzConverterPointer: ctypes.c_void_p, x: float, y: float, z: float) -> Tuple[float,float,float]:
        resx = ctypes.c_double(x);
        resy = ctypes.c_double(y);
        resz = ctypes.c_double(z);
        MzCartDLL.Wrapper.C_MZDC_INVDATUMSHIFT(mzConverterPointer, 
                                               ctypes.byref(resx), ctypes.byref(resy), ctypes.byref(resz))
        return (resx.value, resy.value, resz.value);

    #/ <summary>
    #/ Sets the type of conversion
    #/ </summary>
    @staticmethod
    def MzConverterSetConversionType(mzConverterPointer: ctypes.c_void_p,  typeOfConversion: int):
        MzCartDLL.Wrapper.C_MZDC_SETCONVERSIONTYPE(mzConverterPointer, ctypes.c_int32(typeOfConversion.value))

    #/ <summary>
    #/ Returns the current value of the bypass flag.
    #/ </summary>
    @staticmethod
    def MzConverterGetBypassXYZ(mzConverterPointer: ctypes.c_void_p) -> bool:
      return MzCartDLL.Wrapper.C_MZDC_GETBYPASSXYZ(mzConverterPointer) != 0;

    #/ <summary>
    #/ Configure the datum converter object to exclude conversion to and from Euclidean space.
    #/ This allows unnecessary datum transformations to be skipped.
    #/ </summary>
    @staticmethod
    def MzConverterBypassXYZ(mzConverterPointer: ctypes.c_void_p):
        MzCartDLL.Wrapper.C_MZDC_BYPASSXYZ(mzConverterPointer);

    #/ <summary>
    #/ Configures the datum converter object to reset the bypass flag to its default value
    #/ </summary>
    @staticmethod
    def MzConverterResetBypassXYZ(mzConverterPointer: ctypes.c_void_p):
        MzCartDLL.Wrapper.C_MZDC_RESETBYPASSXYZ(mzConverterPointer);

    #/ <summary>
    #/ Functions that swaps the source and the target map projection including the datum shift parameters.
    #/ </summary>
    @staticmethod
    def MzConverterInvertOrder(mzConverterPointer: ctypes.c_void_p):
        MzCartDLL.Wrapper.C_MZDC_INVERTORDER(mzConverterPointer);
    
    #endregion

    ################################/
    #region MzMapProjection static methods

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> is a valid projection string
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsValid(projectionString: str) -> bool:
      return (MzCartDLL.Wrapper.S_ISVALID(ctypes.c_char_p(projectionString.encode("ascii"))) != 0);

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection has a datum definition.
    #/ <para>
    #/ If a projection does not have an underlying datum, reprojections including datum
    #/ shifts cannot be performed.
    #/ </para>
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def HasDatum(projectionString: str) -> bool:
      return (MzCartDLL.Wrapper.S_HASDATUM(ctypes.c_char_p(projectionString.encode("ascii"))) != 0);

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> defines a local 
    #/ coordinate system that is not georeferenced.
    #/ <para>
    #/ The projection string for a local coordinate system is the string: "NON-UTM"
    #/ </para>
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsLocal(projectionString: str) -> bool:
      return (MzCartDLL.Wrapper.S_ISLOCAL(ctypes.c_char_p(projectionString.encode("ascii"))) != 0);

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection is "LONG/LAT"
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsLongLat(projectionString: str) -> bool:
      return (MzCartDLL.Wrapper.S_ISLONGLAT(ctypes.c_char_p(projectionString.encode("ascii"))) != 0);

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection is georeferenced,
    #/ meaning that it is based on, or can convert to, geographical coordinates (longitude, latitude).
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsGeoreferenced(projectionString: str) -> bool:
      return (MzCartDLL.Wrapper.S_ISGEOREFERENCED(ctypes.c_char_p(projectionString.encode("ascii"))) != 0);

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection is a geographical projection, i.e. based
    #/ on spherical (lon, lat) coordinates
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsGeographical(projectionString: str) -> bool:
      return (MzCartDLL.Wrapper.S_ISGEOGRAPHICAL(ctypes.c_char_p(projectionString.encode("ascii"))) != 0);

    #/ <summary>
    #/ Get the UTM zone best matching the longitude coordinate
    #/ </summary>
    @staticmethod
    def Longitude2UtmZone(longitude: float) -> str:
      res = ctypes.c_char_p((" " * 128).encode("ascii"));
      rc = ctypes.c_int32();
      MzCartDLL.Wrapper.S_LONGITUDETOUTMZONE(ctypes.c_double(longitude), res, ctypes.c_int32(128), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        res = ctypes.c_char_p((" " * (rc.value+1)).encode("ascii"));
        MzCartDLL.Wrapper.S_LONGITUDETOUTMZONE(ctypes.c_double(longitude), res, ctypes.c_int32(rc.value+1), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get short name out of projection string");
      return (res.value.decode("ascii"));

    #/ <summary>
    #/ Get the short name out of a WKT projetion string. 
    #/ <para>
    #/ The short name is not unique amongst all WKT projections
    #/ </para>
    #/ <para>
    #/ If the <paramref name="projString"/> is not a WKT projection string, 
    #/ the <paramref name="projString"/> itself is returned as the short name.
    #/ </para>
    #/ </summary>
    #/ <param name="projString">A WKT projection string</param>
    @staticmethod
    def ProjectionShortName(projString: str) -> str:
      shortNameBuffer = ctypes.c_char_p((" " * 128).encode("ascii"));
      rc = ctypes.c_int32();
      MzCartDLL.Wrapper.S_PROJECTIONSHORTNAME(ctypes.c_char_p(projString.encode("ascii")), shortNameBuffer, ctypes.c_int32(128), ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        shortNameBuffer = ctypes.c_char_p((" " * (rc.value+1)).encode("ascii"));
        MzCartDLL.Wrapper.S_PROJECTIONSHORTNAME(ctypes.c_char_p(projString.encode("ascii")), shortNameBuffer, ctypes.c_int32(128), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get short name ctypes.byref(of projection string)");
      return (shortNameBuffer.value.decode("ascii"));

    #/ <summary>
    #/ If the projection string is not a valid WKT string, an exception is thrown.
    #/ </summary>
    #/ <param name="projstring">A string the the WKT format for a spatial reference system</param>
    #/ <param name="lon">Longitude coordinate of the projection origin</param>
    #/ <param name="lat">Latitude coordinate of the projection origin</param>
    @staticmethod
    def ProjectionOrigin(projstring: str) -> Tuple[float,float]:
      lon = ctypes.c_double() ;
      lat = ctypes.c_double() ;
      rc = ctypes.c_int32();
      MzCartDLL.Wrapper.S_PROJECTIONORIGIN(ctypes.c_char_p(projstring.encode("ascii")), ctypes.byref(lon), ctypes.byref(lat), ctypes.byref(rc));
      if (rc.value != 0):
        raise ProjectionException("Could not get origin of projection string. Is projection string valid?");
      return (lon.value, lat.value);

    #/ <summary>
    #/ Function that checks if two projecions are identical
    #/ </summary>
    #/ <param name="proj1"></param>
    #/ <param name="proj2"></param>
    #/ <returns></returns>
    @staticmethod
    def AreIdentical(projstring1: str, projstring2: str) -> bool:
      rc = MzCartDLL.Wrapper.S_AREIDENTICAL(
          ctypes.c_char_p(projstring1.encode("ascii")), 
          ctypes.c_char_p(projstring2.encode("ascii")));
      return (rc != 0);

    #/ <summary>
    #/ Function that converts a map projection string in WKT (PRJ) format to PROJ.4 format.
    #/ <para>
    #/ Optional datum shift parameters can be provided, but you can also specify 
    #/ <paramref name="datumShiftParameters"/> as null.
    #/ </para>
    #/ <para>
    #/ Datum shift parameter must be specified in order and unit as defined in the Proj.4 
    #/ projection string.
    #/ </para>
    #/ </summary>
    #/ <param name="wktProjectionString">Full WKT projection string</param>
    #/ <param name="datumShiftParameters">Optional array of datum shift parameters, null if not applicable.</param>
    @staticmethod
    def ConvertWkt2Proj4(wktProjectionString: str, datumShiftParameters: np.ndarray) -> str:
      noOfParams = 0;
      if (datumShiftParameters is not None):
        noOfParams= datumShiftParameters.size;

      if ( not (noOfParams==0 or noOfParams==3 or noOfParams==7) ):
        raise Exception("Invalid number of datum shift parameters specified. Only 0, 3 or 7 is allowed", "datumShiftParameters");

      rc = ctypes.c_int32();
      proj4 = ctypes.c_char_p((" " * 1024).encode("ascii"));

      MzCartDLL.Wrapper.C_MZC_CONVERT2PROJ4(
          ctypes.c_char_p(wktProjectionString.encode("ascii")), 
          datumShiftParameters.ctypes.data, 
          ctypes.c_int32(noOfParams), 
          proj4, 
          ctypes.c_int32(rc.value + 1), 
          ctypes.byref(rc));
      if (rc.value > 0):
        # String was too short (length returned as rc), create one with the required length
        proj4 = ctypes.c_char_p((" " * (rc.value + 1)).encode("ascii"));
        MzCartDLL.Wrapper.C_MZC_CONVERT2PROJ4(
            ctypes.c_char_p(wktProjectionString.encode("ascii")), 
            datumShiftParameters.ctypes.data, 
            ctypes.c_int32(noOfParams), 
            proj4, 
            ctypes.c_int32(rc.value + 1), 
            ctypes.byref(rc));
      if (rc != 0):
        raise ProjectionException("Could not convert Prj string to Proj.4 string");

      return (proj4.value.decode("ascii"));



    #endregion

    # ReSharper restore InconsistentNaming




#/ <summary>
#/ Type of axis
#/ </summary>
# Must be kept synchronized with enum EType in MzProjectionInfo.h
class AxisType(IntEnum):
  #/ <summary> Type of axis is eastbound</summary>
  EastAxis = 0;
  #/ <summary> Type of axis is northbound</summary>
  NorthAxis = 1;
  #/ <summary> Type of axis is westbound</summary>
  WestAxis = 2;
  #/ <summary> Type of axis is southbound</summary>
  SouthAxis = 3;

#/ <summary>
#/ Type of coordinate systems
#/ </summary>
# Must be kept synchronized with enum ECoordSysType in MzMapProjection.h
class CoordSysType(IntEnum):
  #/ <summary> Type of projected coordinate system being undefined</summary>
  TypeUndefined = 0;
  #/ <summary> Type of projected coordinate system being east/north oriented</summary>
  EastNorth = (AxisType.EastAxis << 2) | AxisType.NorthAxis;
  #/ <summary> Type of projected coordinate system being north/east oriented</summary>
  NorthEast = (AxisType.NorthAxis << 2) | AxisType.EastAxis;
  #/ <summary> Type of projected coordinate system being west/north oriented</summary>
  WestNorth = (AxisType.WestAxis << 2) | AxisType.NorthAxis;
  #/ <summary> Type of projected coordinate system being north/west oriented</summary>
  NorthWest = (AxisType.NorthAxis << 2) | AxisType.WestAxis;
  #/ <summary> Type of projected coordinate system being west/south oriented</summary>
  WestSouth = (AxisType.WestAxis << 2) | AxisType.SouthAxis;
  #/ <summary> Type of projected coordinate system being south/west oriented</summary>
  SouthWest = (AxisType.SouthAxis << 2) | AxisType.WestAxis;
  #/ <summary> Type of projected coordinate system being east/south oriented</summary>
  EastSouth = (AxisType.EastAxis << 2) | AxisType.SouthAxis;
  #/ <summary> Type of projected coordinate system being south/east oriented</summary>
  SouthEast = (AxisType.SouthAxis << 2) | AxisType.EastAxis;


  #/ <summary>
  #/ A map projection handles conversion from geographical coordinates (lon, lat)
  #/ to projection coordintes (east, north) and to Euclidean 3D datum coordinates 
  #/ with origin in the center of the earch (center of the ellipsoid).
  #/ <para>
  #/ The <see cref="ProjectionString"/> is a WKT string for a spatial 
  #/ reference system. A number of abbreviated strings also exists, 
  #/ i.e., "UTM-33" for a WGS-84 UTM zone 33 projection.
  #/ </para>
  #/ </summary>
  #/ <example>
  #/ <code>
  #/   # WKT projection string
  #/   string projStr = @"PROJCS[""NZGD_2000_New_Zealand_Transverse_Mercator"",GEOGCS[""GCS_NZGD_2000"",DATUM[""D_NZGD_2000"",SPHEROID[""GRS_1980"",6378137.0,298.257222101]],PRIMEM[""Greenwich"",0.0],UNIT[""Degree"",0.0174532925199433]],PROJECTION[""Transverse_Mercator""],PARAMETER[""False_Easting"",1600000.0],PARAMETER[""False_Northing"",10000000.0],PARAMETER[""Central_Meridian"",173.0],PARAMETER[""Scale_Factor"",0.9996],PARAMETER[""Latitude_Of_Origin"",0.0],UNIT[""Meter"",1.0]]";
  #/   MapProjection mapProj = new MapProjection(projStr);
  #/
  #/   # Convert from projection to geographical coordinates.
  #/   double lon, lat;
  #/   mapProj.Proj2Geo(1752001, 5947201, out lon, out lat);
  #/ </code>
  #/ </example>
class MapProjection:

    def __init__(self, projectionString: str, mzMapProjPointer: ctypes.c_void_p = None, mustFree: bool = False, objectHolder: object = None):
        self.ProjectionString = projectionString;
        self._mzMapProjPointer = mzMapProjPointer;
        #/ <summary>
        #/ Reference to object that actually holds the unmanaged
        #/ data, and that will free unmanaged ressources.
        #/ The reference is kept here to avoid garbage collection
        #/ of the holding object and thereby the release of 
        #/ the MzMapProjection object that this object relies on.
        #/ </summary>
        self._objectHolder = objectHolder;
        self._mustFree = mustFree;

        if (self._mzMapProjPointer is None):
            self._mzMapProjPointer = MzCartDLL.MzMapProjCreate(projectionString);
        if (self.ProjectionString is None):
            self.ProjectionString = MzCartDLL.MzMapProjProjectionString(self._mzMapProjPointer);

        self.Name = MzCartDLL.MzMapProjName(self._mzMapProjPointer);

    #/ <summary>
    #/ Create and initialize a mapprojection with the specifed projection string.
    #/ </summary>
    #/ <param name="projectionString">A string in the WKT format for a spatial reference system, or one of the abbreviations</param>
    #/ <param name="validateProjectionString">Bool specifying if projectionstrings should be validated or not. 
    #/ It is fairly expensive to validate the projection strings, and the validation can be skipped by setting this flag to false. 
    #/ Then the user must beforehand check that the projection is valid by calling <see cref="MapProjection.IsValid"/>. </param>
    @staticmethod
    def Create(projectionString: str, validateProjectionString: bool = True):
      if (projectionString is None or projectionString == ""):
        raise Exception("Projection string cannot be null or empty", "projectionString");
      if (validateProjectionString):
        if (not MapProjection.IsValid(projectionString)):
          raise Exception("Not a valid projection string", "projectionString");
      return MapProjection(projectionString, mustFree=True);

    #/ <summary>
    #/ Creates a map-projection from a pointer to a map-projection object that
    #/ is part of parent object (e.g. MzCartography), and that will
    #/ be released together with the parent object, i.e. the map-projection object
    #/ cannot be released standalone.
    #/ </summary>
    #/ <param name="mzMapProjPointer">Pointer to map projection object</param>
    #/ <param name="mapProjObjectHolder">Pointer to .NET object that represents the parent unmanaged object</param>
    #/ <remarks>
    #/ The mapProjObjectHolder reference is required to assure that the parent .NET object can go 
    #/ out of scope, but only when the map projection also goes out of scope the parent object
    #/ is garbage collected (and only then parent unmanged ressources are released).
    #/ </remarks>
    def CreatePointer(self, mzMapProjPointer: ctypes.c_void_p, mapProjObjectHolder: object):
        return MapProjection(None, mzMapProjPointer, False, mapProjObjectHolder)

    #/ <summary>
    #/ Free unmanaged ressources
    #/ </summary>
    def __del__(self):
      # Release ressources on the unmanaged side when garbage collected
      if (self._mustFree):
        if (self._mzMapProjPointer.value != None):
          MzCartDLL.MzMapProjDestroy(self._mzMapProjPointer);
      _mzMapProjPointer = ctypes.c_void_p();

    ##/ <summary>
    ##/ The short name of a projection. 
    ##/ <para>
    ##/ The short name is not unique amongst all WKT projections
    ##/ </para>
    ##/ <para>
    ##/ If the <see cref="ProjectionString"/> is not a WKT projection string, 
    ##/ the <see cref="ProjectionString"/> itself is returned as the short name.
    ##/ </para>
    ##/ </summary>
    #public string Name { get { return (MzCartDLL.MzMapProjName(self._mzMapProjPointer)); } }

    ##/ <summary>
    ##/ Returns the WKT projection string, or one of the projection abbreviation strings.
    ##/ </summary>
    #public string ProjectionString { get { return (MzCartDLL.MzMapProjProjectionString(self._mzMapProjPointer)); } }

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to projection coordinates
    #/ </summary>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    #/ <param name="east">Easting</param>
    #/ <param name="north">Northing</param>
    def Geo2Proj(self, lon: float, lat: float) -> Tuple[float,float]:
      return MzCartDLL.MzMapProjGeo2Proj(self._mzMapProjPointer, lon, lat);

    #/ <summary>
    #/ Convert coordinates from projection coordinates to geographical coordinates 
    #/ </summary>
    #/ <param name="east">Easting</param>
    #/ <param name="north">Northing</param>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    def Proj2Geo(self, east: float, north: float) -> Tuple[float,float]:
      return MzCartDLL.MzMapProjProj2Geo(self._mzMapProjPointer, east, north);

    #/ <summary>
    #/ Get the geographical origin of the map projection
    #/ </summary>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    def GetOrigin(self) -> Tuple[float,float]:
      return MzCartDLL.MzMapProjGetOrigin(self._mzMapProjPointer);

    #/ <summary>
    #/ Get the convergence (orientation towards true north) at the given geographical location.
    #/ <para>
    #/ The convergence is the angle measured clockwise from true north to the north-south
    #/ gridline passing through the specified coordinate.
    #/ </para>
    #/ </summary>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    def GetConvergence(self, lon: float, lat: float) -> float:
      return (MzCartDLL.MzMapProjGetConvergence(self._mzMapProjPointer, lon, lat));

    #/ <summary>
    #/ Function that returns the default area in map projection coordinates of the projection.
    #/ <para>
    #/ The default area is the area where the projection is ment to be used and where
    #/ it is accurate. It is not recommended to use the map projection outside its
    #/ default area.
    #/ </para>
    #/ </summary>
    #/ <param name="x0">the x-coordinate of the lower lefthand corner</param>
    #/ <param name="y0">the y-coordinate of the lower lefthand corner</param>
    #/ <param name="x1">the x-coordinate of the upper righthand corner</param>
    #/ <param name="y1">the y-coordinate of the upper righthand corner</param>
    def GetDefaultArea(self) -> Tuple[float,float,float,float]:
      return MzCartDLL.GetDefaultArea(self._mzMapProjPointer);

    #/ <summary>
    #/ Convert coordinates from geographical coordinates and height to 3D Euclidean coordinates.
    #/ <para>
    #/ The 3D coordinate system origin is at the earth center (ellipsoid center)
    #/ </para>
    #/ </summary>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    #/ <param name="height">Height over ellipsoid</param>
    #/ <param name="x">Eucledian x coordinate</param>
    #/ <param name="y">Eucledian y coordinate</param>
    #/ <param name="z">Eucledian z coordinate</param>
    def Geo2Xyz(self, lon: float, lat: float, height: float) -> Tuple[float,float,float]:
      return MzCartDLL.MzMapProjGeo2Xyz(self._mzMapProjPointer, lon, lat, height);

    #/ <summary>
    #/ Convert coordinates from Euclidean 3D coordinates to geographical coordinates and height.
    #/ <para>
    #/ The 3D coordinate system origin is at the earth center (ellipsoid center)
    #/ </para>
    #/ </summary>
    #/ <param name="x">Eucledian x coordinate</param>
    #/ <param name="y">Eucledian y coordinate</param>
    #/ <param name="z">Eucledian z coordinate</param>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    #/ <param name="height">Height over ellipsoid</param>
    def Xyz2Geo(self, x: float, y: float, z: float) -> Tuple[float,float,float]:
      return MzCartDLL.MzMapProjXyz2Geo(self._mzMapProjPointer, x, y, z);

    #/ <summary>
    #/ Convert a rotation from map projection north
    #/ into a rotation from true north. 
    #/ <para>
    #/ It adds the convergence value to the projection north rotation value
    #/ </para>
    #/ <para>
    #/ The convertion depends on the geographical location.
    #/ </para>
    #/ </summary>
    #/ <param name="east">Easting coordinate</param>
    #/ <param name="north">Northing coordinate</param>
    #/ <param name="rotation">Rotation clock-wise from map projection north</param>
    #/ <returns>Rotation clock-wise from true north</returns>
    def Proj2GeoRotation(self, east: float, north: float, rotation: float) -> float:
      lon, lat = self.Proj2Geo(east, north);
      convergence = self.GetConvergence(lon, lat);
      return rotation + convergence;

    #/ <summary>
    #/ Convert a rotation from true north
    #/ into a rotation from map projection north
    #/ <para>
    #/ It subtracts the convergence value from the true north rotation value
    #/ </para>
    #/ <para>
    #/ The convertion depends on the geographical location.
    #/ </para>
    #/ </summary>
    #/ <param name="lon">Easting coordinate</param>
    #/ <param name="lat">Northing coordinate</param>
    #/ <param name="rotation">Rotation clock-wise from true north</param>
    #/ <returns>Rotation clock-wise from map projection north</returns>
    def Geo2ProjRotation(self, lon: float, lat: float, rotation: float) -> float:
      convergence = self.GetConvergence(lon, lat);
      return rotation - convergence;

    ################################/
    #region static methods

    #private static readonly Dictionary<string, bool> _validProjectionStrings = new Dictionary<string, bool>(StringComparer.Ordinal);

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> is a valid projection string
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsValid(projectionString: str) -> bool:
      return MzCartDLL.IsValid(projectionString);
#      # The C += 1 IsValid method is fairly expensive, so buffer values for future use.
#      lock (_validProjectionStrings)
#        bool isValid;
#        if (not _validProjectionStrings.TryGetValue(projectionString, ctypes.byref(isValid))):
#           isValid = MzCartDLL.IsValid(projectionString);
#          _validProjectionStrings.Add(projectionString, isValid);
#        }          
#        return isValid;

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection has a datum definition.
    #/ <para>
    #/ If a projection does not have an underlying datum, reprojections including datum
    #/ shifts cannot be performed.
    #/ </para>
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def HasDatum(projectionString: str) -> bool:
      return (MzCartDLL.HasDatum(projectionString));

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> defines a local 
    #/ coordinate system that is not georeferenced.
    #/ <para>
    #/ The projection string for a local coordinate system is the string: "NON-UTM"
    #/ </para>
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsLocal(projectionString: str) -> bool:
      return (MzCartDLL.IsLocal(projectionString));

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection is "LONG/LAT"
    #/ <para>
    #/ "LONG/LAT" is a geographical coordinate system without an underlying datum (ellipsoid) 
    #/ definition.
    #/ </para>
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsLongLat(projectionString: str) -> bool:
      return (MzCartDLL.IsLongLat(projectionString));

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection is georeferenced,
    #/ meaning that it is based on, or can convert to, geographical coordinates (longitude, latitude).
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsGeoreferenced(projectionString: str) -> bool:
      return (MzCartDLL.IsGeoreferenced(projectionString));

    #/ <summary>
    #/ Returns true if the <paramref name="projectionString"/> projection is a geographical projection, i.e. based
    #/ on spherical (lon, lat) coordinates
    #/ </summary>
    #/ <param name="projectionString">Name of map projection, WKT string or a projection abbreviation</param>
    @staticmethod
    def IsGeographical(projectionString: str) -> bool:
      return (MzCartDLL.IsGeographical(projectionString));


    #/ <summary>
    #/ Get the projection string for the UTM zone best matching the longitude coordinate
    #/ </summary>
    #/ <param name="lon">Name of map projection, WKT string</param>
    #/ <returns>UTM zone WKT string</returns>
    @staticmethod
    def Longitude2UtmZone(lon: float) -> str:
      return (MzCartDLL.Longitude2UtmZone(lon));

    #/ <summary>
    #/ Get the short name out of a WKT projetion string. 
    #/ <para>
    #/ The short name is not unique amongst all WKT projections
    #/ </para>
    #/ <para>
    #/ If the <paramref name="projString"/> is not a WKT projection string, 
    #/ the <paramref name="projString"/> itself is returned as the short name.
    #/ </para>
    #/ </summary>
    #/ <param name="projString">A WKT projection string</param>
    @staticmethod
    def ProjectionShortName(projString: str) -> str:
      return (MzCartDLL.ProjectionShortName(projString));

    #/ <summary>
    #/ Returns the geographical origin of the projection defined by the
    #/ <paramref name="projstring"/>
    #/ <para>
    #/ If the projection string is not a valid WKT string, an exception is thrown.
    #/ </para>
    #/ </summary>
    #/ <param name="projstring">A string the the WKT format for a spatial reference system</param>
    #/ <param name="lon">Longitude coordinate of the projection origin</param>
    #/ <param name="lat">Latitude coordinate of the projection origin</param>
    #/ <param name="validateProjectionString">Bool specifying if projectionstrings should be validated or not. 
    #/ It is fairly expensive to validate the projection strings, and the validation can be skipped by setting this flag to false. 
    #/ Then the user must beforehand check that the projection is valid by calling <see cref="MapProjection.IsValid"/>. </param>
    @staticmethod
    def ProjectionOrigin(projstring: str, validateProjectionString: bool = True) -> Tuple[float,float]:
      if (validateProjectionString and not MzCartDLL.IsValid(projstring)):
        raise Exception("Projection string is not a valid WKT projection string", "projstring");
      return MzCartDLL.ProjectionOrigin(projstring);

    #/ <summary>
    #/ Returns the Google Map projection string
    #/ </summary>
    @staticmethod
    def GoogleMapProjectionString() -> str:
        return MzCartDLL.GoogleMapProjectionString();

    @staticmethod
    def LocalCoordinatesProjectionString() -> str:
        return "NON-UTM";


    #/ <summary>
    #/ Function that checks if two projecions are identical. 
    #/ <para>
    #/ Two map projections are identical, if they have the same set of parameters. 
    #/ if just one of the parameters are different, then the map projections are NOT identical.
    #/ </para>
    #/ </summary>
    #/ <example>
    #/ As an example, "UTM-32" is identical to  "WGS_1984_UTM_Zone_32N", because they 
    #/ have the same set of parameters and the ellipsoids are equivalent, but the projections don't have the same name. 
    #/ Another example of identical map projections is "NAD_1983_StatePlane_Alaska_1_FIPS_5001" and 
    #/ "NAD_1983_StatePlane_Alaska_1_FIPS_5001_Feet". Some parameters are defined in different units,
    #/ but they are converted to a common unit, before they are compared. 
    #/ </example>
    #/ <param name="projstring1">Specifies the full WKT map projection string to the first projection</param>
    #/ <param name="projstring2">Specifies the full WKT map projection string to the second projection</param>
    #/ <returns></returns>
    @staticmethod
    def AreIdentical(projstring1: str, projstring2: str) -> bool:
      return MzCartDLL.AreIdentical(projstring1, projstring2);

    #/ <summary>
    #/ Function that returns the coordinate system type.
    #/ <para>
    #/ Use this function check the type of coordinate system e.g. east/north or some other combination.
    #/ A typical application of this function is to exclude coordinate systems, that are not standard
    #/ east/north-oriented.
    #/ </para>
    #/ </summary>
    #/ <param name="projstring">Specifies the full WKT map projection string to the projection</param>
    #/ <returns></returns>
    @staticmethod
    def GetCoordSysType(projstring: str) -> CoordSysType:
        rc = MzCartDLL.Wrapper.S_GETCOORDSYSTYPE(ctypes.c_char_p(projstring.encode("ascii")));
        return (CoordSysType(rc));
    #endregion


  #/ <summary>
  #/ A cartography object handles a map projection and a local grid 
  #/ that can be translated and rotated relative to the projected
  #/ coordinate system.
  #/ <para>
  #/ There are 3 levels of coordinates:
  #/ Geographical coordinates (longitude, latitude) in degrees, 
  #/ projection coordinates (easting, northing), and
  #/ local/model/user grid coordinates (x,y).
  #/ </para>
  #/ <para>
  #/ The <see cref="ProjectionString"/> defines the mapping from geographical 
  #/ coordinates to projection coordinates.
  #/ </para>
  #/ <para>
  #/ The <see cref="LatOrigin"/>, <see cref="LonOrigin"/> and 
  #/ <see cref="Orientation"/> defines the origin and the 
  #/ orientation of the local grid coordinates. It defines how 
  #/ the local grid coordinate system is translated and rotated.
  #/ This kind of local grid coordinate system is used for e.g. a 2D grid in a dfs2 file.
  #/ </para>
  #/ <para>
  #/ See <see cref="Orientation"/> for the definition of the orientation.
  #/ The local grid are rotated around its origin.
  #/ </para>
  #/ <para>
  #/ If <see cref="LonOrigin"/> is zero, and <see cref="LatOrigin"/> and <see cref="MapProjection.ProjectionOrigin"/>
  #/ matches the origin of the projection coordinate system (from <see cref="MapProjection"/>), 
  #/ then projection coordinates equals local grid coordinates. 
  #/ Example: UTM-31 has projection origin at (lon,lat) = (3,0). 
  #/ </para>
  #/ </summary>
  #/ <example>
  #/ <code>
  #/   # The abbreviation for the long WKT projection string
  #/   utm33String = "UTM-33"; 
  #/ 
  #/   # Create a Cartography object with a local grid origin at lon-lat (17,55)
  #/   # rotated -45 degrees from true north.
  #/   Cartography cart = new Cartography(utm33String, 17, 55, -45);
  #/   double east, north, x, y;
  #/ 
  #/   # Convert from geographical to map projection coordinates
  #/   cart.Geo2Proj(17, 55, out east, out north);
  #/ 
  #/   # Convert from geographical to local grid coordinates
  #/   cart.Geo2Xy(17, 55, out x, out y);
  #/ </code>
  #/ </example>
  #/ 
class Cartography:
    def __init__(self, 
                 projectionString: str,
                 lonOrigin: float = None,
                 latOrigin: float = None,
                 orientation: float = 0.0,
                 eastOrigin: float = None,
                 northOrigin: float = None,
                 orientationProj: float = 0.0,
                 validateProjectionString: bool = True,
                 ):

        self._mzCartPointer = ctypes.c_void_p(0);

        if (validateProjectionString):
          if (not MapProjection.IsValid(projectionString)):
            raise Exception("Not a valid projection string", "projectionString");

        if (lonOrigin is None):
            lonOrigin, latOrigin = MapProjection.ProjectionOrigin(projectionString, False);
        self.LonOrigin        = lonOrigin;
        self.LatOrigin        = latOrigin;
        self.Orientation      = orientation;

        self._mzCartPointer = MzCartDLL.MzCartCreate(projectionString, self.LonOrigin, self.LatOrigin, self.Orientation);

        # Override - to expand abbreviations
        self.ProjectionString = MzCartDLL.MzCartProjectionString(self._mzCartPointer)
        self.ProjectionName = MzCartDLL.MzCartProjectionName(self._mzCartPointer);

        if (eastOrigin is None):
            self.__InitProjOrigin();
        else:
            self.EastOrigin       = eastOrigin;
            self.NorthOrigin      = northOrigin;
            self.OrientationProj  = orientationProj;

        self._myProjection = None;


    def __InitProjOrigin(self):
      if (MapProjection.IsGeographical(self.ProjectionString)):
        self.EastOrigin = self.LonOrigin;
        self.NorthOrigin = self.LatOrigin;
        self.OrientationProj = self.Orientation;
      else:
        eastOrigin, northOrigin = self.Geo2Proj(self.LonOrigin, self.LatOrigin);
        self.EastOrigin  = eastOrigin;
        self.NorthOrigin = northOrigin;
        self.OrientationProj = MzCartDLL.MzCartProjectionNorth(self._mzCartPointer);

    #/ <summary>
    #/ Release ressources on the unmanaged side when garbage collected.
    #/ </summary>
    def __del__(self):
      self.Dispose();

    #/ <summary>
    #/ Release ressources on the unmanaged side.
    #/ </summary>
    #/ <remarks>
    #/ The Dispose method must be private; The user should not be able 
    #/ to call this method directly, since there can be a MapProjection 
    #/ object out there that needs the unmanaged MzCartography class for 
    #/ its work.
    #/ </remarks>
    def Dispose(self):
      # Release ressources on the unmanaged side
      if (self._mzCartPointer.value != None):
        MzCartDLL.MzCartDestroy(self._mzCartPointer);
        # Prevent subsequent finalization of this object. This is not needed 
        # because managed and unmanaged resources have been explicitly released
        #GC.SuppressFinalize(this);
      self._mzCartPointer = ctypes.c_void_p();

    #/ <summary>
    #/ Get the map projection that this cartography object uses.
    #/ </summary>
    def Projection(self):
        if (self._myProjection == None):
          self._myProjection = MapProjection(None, MzCartDLL.MzCartGetMapProjection(self._mzCartPointer), objectHolder=self);
        return (self._myProjection);

    #/ <summary>
    #/ Returns the angle between true north and a line parallel to the 
    #/ local grid y axis passing through (x,y).
    #/ <para>
    #/ The angle is in degrees, measured positive clockwise from true north.
    #/ </para>
    #/ </summary>
    #/ <param name="x">Local grid x coordinate</param>
    #/ <param name="y">Local grid y coordinate</param>
    def GetTrueNorth(self, x: float, y: float) -> float:
      return (MzCartDLL.MzCartTrueNorth(self._mzCartPointer, x, y));

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to projection coordinates
    #/ </summary>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    #/ <param name="east">Easting</param>
    #/ <param name="north">Northing</param>
    def Geo2Proj(self, lon: float, lat: float) -> Tuple[float,float]:
      return MzCartDLL.MzCartGeo2Proj(self._mzCartPointer, lon, lat);

    #/ <summary>
    #/ Convert coordinates from projection coordinates to geographical coordinates 
    #/ </summary>
    #/ <param name="east">Easting</param>
    #/ <param name="north">Northing</param>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    def Proj2Geo(self, east: float, north: float) -> Tuple[float,float]:
      return MzCartDLL.MzCartProj2Geo(self._mzCartPointer, east, north);

    #/ <summary>
    #/ Convert coordinates from geographical coordinates to local grid x-y coordinates
    #/ </summary>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    #/ <param name="x">Local grid x coordinate</param>
    #/ <param name="y">Local grid y coordinate</param>
    def Geo2Xy(self, lon: float, lat: float) -> Tuple[float,float]:
      return MzCartDLL.MzCartGeo2Xy(self._mzCartPointer, lon, lat);

    #/ <summary>
    #/ Convert coordinates from local grid x-y coordinates to geographical coordinates 
    #/ </summary>
    #/ <param name="x">Local grid x coordinate</param>
    #/ <param name="y">Local grid y coordinate</param>
    #/ <param name="lon">Longitude</param>
    #/ <param name="lat">Latitude</param>
    def Xy2Geo(self, x: float, y: float) -> Tuple[float,float]:
      return MzCartDLL.MzCartXy2Geo(self._mzCartPointer, x, y);

    #/ <summary>
    #/ Convert coordinates from projetion coordinates to local grid x-y coordinates
    #/ </summary>
    #/ <param name="east">Easting</param>
    #/ <param name="north">Northing</param>
    #/ <param name="x">Local grid x coordinate</param>
    #/ <param name="y">Local grid y coordinate</param>
    def Proj2Xy(self, east: float, north: float) -> Tuple[float,float]:
      return MzCartDLL.MzCartProj2Xy(self._mzCartPointer, east, north);

    #/ <summary>
    #/ Convert coordinates from local grid x-y coordinates to projection coordinates 
    #/ </summary>
    #/ <param name="x">Local grid x coordinate</param>
    #/ <param name="y">Local grid y coordinate</param>
    #/ <param name="east">Easting</param>
    #/ <param name="north">Northing</param>
    def Xy2Proj(self, x: float, y: float) -> Tuple[float,float]:
      return MzCartDLL.MzCartXy2Proj(self._mzCartPointer, x, y);

    #region Static factory methods
    

    #/ <summary>
    #/ Create and initialize a cartography object using the
    #/ specified projection string, setting the origin of the user
    #/ defined local grid coordinates to the 
    #/ <paramref name="lonOrigin"/>, <paramref name="latOrigin"/>, rotated
    #/ <paramref name="orientation"/>.
    #/ </summary>
    #/ <param name="projectionString">A string in the WKT format for a spatial reference system, or one of the abbreviations</param>
    #/ <param name="lonOrigin">Longitude coordinate of the local grid origin</param>
    #/ <param name="latOrigin">Latitude coordinate of the local grid origin</param>
    #/ <param name="orientation">Orientation of the cartography class grid, rotation in degreesn clockwise from geographical north</param>
    #/ <param name="validateProjectionString">Bool specifying if projectionstrings should be validated or not. 
    #/ It is fairly expensive to validate the projection strings, and the validation can be skipped by setting this flag to false. 
    #/ Then the user must beforehand check that the projection is valid by calling <see cref="MapProjection.IsValid"/>. </param>
    @staticmethod
    def CreateGeoOrigin(projectionString: str, lonOrigin: float, latOrigin: float, orientation: float = 0, validateProjectionString: bool = True):
      if (projectionString is None or projectionString == ""):
        raise ValueError("Projection string can not be null or empty")
      if (validateProjectionString):
        if (not MapProjection.IsValid(projectionString)):
          raise ValueError("Not a valid projection string")
      cart = Cartography(projectionString, lonOrigin, latOrigin, orientation, validateProjectionString=False);
      return cart;

    #/ <summary>
    #/ Create and initialize a cartography object using the
    #/ specified projection string, setting the origin of the user
    #/ defined local grid coordinates to the projected coordinates
    #/ <paramref name="east"/>, <paramref name="north"/>, rotated
    #/ <paramref name="orientationProj"/> towards projection north.
    #/ </summary>
    #/ <param name="projectionString">A string in the WKT format for a spatial reference system, or one of the abbreviations</param>
    #/ <param name="east">Origin easting/x coordinate value of the local grid origin</param>
    #/ <param name="north">Origin northing/y coordinate value</param>
    #/ <param name="orientationProj">Orientation of the local grid, rotation in degreesn clockwise from projection north</param>
    #/ <param name="validateProjectionString">Bool specifying if projectionstrings should be validated or not. 
    #/ It is fairly expensive to validate the projection strings, and the validation can be skipped by setting this flag to false. 
    #/ Then the user must beforehand check that the projection is valid by calling <see cref="MapProjection.IsValid"/>. </param>
    @staticmethod
    def CreateProjOrigin(projectionString: str, east: float, north: float, orientationProj: float, validateProjectionString: bool = True):
      if (projectionString is None or projectionString == ""):
        raise ValueError("Projection string cannot be null or empty")
      if (validateProjectionString):
        if (not MapProjection.IsValid(projectionString)):
          raise ValueError("Not a valid projection string")
      proj = MapProjection.Create(projectionString, validateProjectionString);
      lonOrigin, latOrigin = proj.Proj2Geo(east, north);
      orientationGeo = proj.Proj2GeoRotation(east, north, orientationProj);
      return Cartography(projectionString, lonOrigin, latOrigin, orientationGeo, east, north, orientationProj, validateProjectionString=False);


#/ <summary>
#/ Side of conversion in reprojection
#/ </summary>
class ReprojectorSide(IntEnum):
  #/ <summary> Source side </summary>
  Source = 0;
  #/ <summary> Target side </summary>
  Target = 1;

#/ <summary>
#/ Type of conversion
#/ </summary>
# Must be kept synchronized with enum ETypeOfConversion in MzDatumConverter.h
class ReprojectorConversionType(IntEnum):
  #/ <summary> Convert from source projection coordinates to target projection coordinates</summary>
  Proj2Proj = 0;
  #/ <summary> Convert from source projection coordinates to target geographic coordinates</summary>
  Proj2Geo = 1;
  #/ <summary> Convert from source geographic coordinates to target projection coordinates</summary>
  Geo2Proj = 2;
  #/ <summary> Convert from source geographic coordinates to target geographic coordinates</summary>
  Geo2Geo = 3;

# Must be kept synchronized with enum ETypeOfDatumShift in MzDatumConverter.h
class ReprojectorDatumShiftType(IntEnum):
  #/ <summary> No datum shift is to be applied </summary>
  NoDatumShift = 0;
  #/ <summary> Using 3 parameter datum shift </summary>
  Param3 = 1;
  #/ <summary> Using 7 parameter datum shift </summary>
  Param7 = 2;
    


  #/ <summary>
  #/ The Reprojector class handles conversion from a source map projection to a target map projection. 
  #/ The conversion can be performed with or without height. The conversion automatically handles datum 
  #/ (ellipsoid) conversions, and can also perform datum shifts.
  #/ <para>
  #/ The <see cref="TypeOfConversion"/> defines type of coordinates used in conversion.
  #/ </para>
  #/ <para>
  #/ The reprojection conversion from source map projection to target map projection coordinates works as follows:
  #/ <list type="bullet">
  #/ <item>Source projection coordinates (east, north) are converted to source geographic coordinates (lon, lat)</item>
  #/ <item>Source geographic coordinates (lon, lat, height) are converted to source Eucledian datum coordinates (x,y,z)</item>
  #/ <item>Datum shift is applied, if specified, to target Eucledian datum coordinates (x,y,z)</item>
  #/ <item>Target Eucledian datum coordinates (x,y,z) are converted to target geographic coordinates (lon, lat, height)</item>
  #/ <item>Target geographic coordinates (lon, lat) are converted to target projection coordinates (east, north)</item>
  #/ </list>
  #/ When datum shift parameters are not specified, and the datums (ellipsoids) of the source and the target
  #/ are identical, the three middel steps are skipped. The three middle steps can also be bypassed
  #/ by setting explicitly the <see cref="BypassDatumConversions"/> property to false. That will give incorrect
  #/ results, however especially some graphical tools does this for performance reasons: 
  #/ Visually the results will look ok as long 
  #/ as all data are defined in projections sharing the same datum (ellipsoid), and all visualization take place in 
  #/ target projection - if data are defined in projections using different datums (ellipsoids), errors will occur.   
  #/ </para>
  #/ <para>
  #/ The datum shift works in a two step process:
  #/ <list type="bullet">
  #/ <item>Source datum shift conversion is applied, if specified</item>
  #/ <item>Target datum shift inverse conversion is applied, if specified</item>
  #/ </list>
  #/ </para>
  #/ <para>
  #/ It is possible to specify datum shift parameters for as well the source as the target
  #/ map projection. 
  #/ </para>
  #/ <para>
  #/ If datum shift parameters directly from source to target is known, this must be set as
  #/ the source datum shift parameters. 
  #/ </para>
  #/ <para>
  #/ If datum shift parameters directly from target to source is known, this must be set as 
  #/ the target datum shift parameters.  
  #/ </para>
  #/ <para>
  #/ If datum shift parameters is known from both source and target to
  #/ a common datum, both set of parameters must be specified. Then a reprojection will first
  #/ convert from source datum to common datum, and then from common datum to target datum by an
  #/ inverse datum shift operation.
  #/ </para>
  #/ </summary>
  #/ <example>
  #/ <code>
  #/   # Projection strings are truncated due to their lenghts.
  #/   string utm20NNad1927 = @"PROJCS[""NAD_1927_UTM_Zone_20N"", ... 
  #/   string utm20NWgs84 = @"PROJCS[""WGS_1984_UTM_Zone_20N"", ... 
  #/ 
  #/   # Create reprojector.
  #/   Reprojector reprojector = new Reprojector(utm20NNad1927, utm20NWgs84);
  #/ 
  #/   # Conversion from projection-to-projection coordinates, no height
  #/   x = 35000; y = 6000000;
  #/   reprojector.Convert(ref x, ref y);
  #/ 
  #/   # Converting from projection-to-geographical coordiantes, including height
  #/   reprojector.TypeOfConversion = Reprojector.ConversionType.Proj2Geo;
  #/   x = 35000; y = 6000000; h = 100;
  #/   reprojector.Convert(ref x, ref y, ref h);
  #/ </code>
  #/ </example>
class Reprojector:


    #/ <summary>
    #/ Create a new reprojector object, converting from source to target as specified in the
    #/ arguments.
    #/ </summary>
    #/ <param name="projectionStringSource">String for source map projection, in the WKT format for a spatial reference system, or one of the abbreviations</param>
    #/ <param name="projectionStringTarget">String for target map projection, in the WKT format for a spatial reference system, or one of the abbreviations</param>
    #/ <param name="validateProjectionStrings">Bool specifying if projectionstrings should be validated or not. 
    #/ It is fairly expensive to validate the projection strings, and the validation can be skipped by setting this flag to false. 
    #/ Then the user must beforehand check that the projection is valid by calling <see cref="MapProjection.IsValid"/>. </param>
    def __init__(self, projectionStringSource: str, projectionStringTarget: str, validateProjectionStrings: bool = True):
      if (projectionStringSource is None or projectionStringSource == ""):
        raise Exception("Projection string cannot be null or empty", "projectionStringSource");
      if (projectionStringTarget is None or projectionStringTarget == ""):
        raise Exception("Projection string cannot be null or empty", "projectionStringTarget");
      if (validateProjectionStrings):
        if (not MapProjection.IsValid(projectionStringSource)):
          raise Exception("Not a valid projection string", "projectionStringSource");
        if (not MapProjection.IsValid(projectionStringTarget)):
          raise Exception("Not a valid projection string", "projectionStringTarget");
      self.ProjectionStringSource = projectionStringSource;
      self.ProjectionStringTarget = projectionStringTarget;
      self._mzConverterPointer = MzCartDLL.MzConverterCreate(projectionStringSource, projectionStringTarget);
      self._typeOfConversion = ReprojectorConversionType.Proj2Proj;


    #/ <summary>
    #/ Release ressources on the unmanaged side when garbage collected.
    #/ </summary>
    def __del__(self):
      self.Dispose();

    #/ <summary>
    #/ Release ressources on the unmanaged side.
    #/ </summary>
    #/ <remarks>
    #/ The Dispose method must be private; The user should not be able 
    #/ to call this method directly.
    #/ </remarks>
    def Dispose(self):
      # Release ressources on the unmanaged side
      if (not self._mzConverterPointer is None):
        MzCartDLL.MzConverterDestroy(self._mzConverterPointer);
        # Prevent subsequent finalization of this object. This is not needed 
        # because managed and unmanaged resources have been explicitly released
        #GC.SuppressFinalize(this);
      self._mzConverterPointer = ctypes.c_void_p();

    def __getConversionType(self):
        return self._typeOfConversion
    def __setConversionType(self, value):
        self._typeOfConversion = value; 
        MzCartDLL.MzConverterSetConversionType(self._mzConverterPointer, self._typeOfConversion);
    #/ <summary>
    #/ Type of conversion. Default is <see cref="ConversionType.Proj2Proj"/>.
    #/ </summary>
    TypeOfConversion = property(__getConversionType, __setConversionType);

    #/ <summary>
    #/ Invert the order of the conversion, by swapping the source and the target map 
    #/ projection, including any datum shift parameters.
    #/ <para>
    #/ Also the <see cref="TypeOfConversion"/> will be inverted, 
    #/ i.e. a type of <see cref="ConversionType.Proj2Geo"/> will be changed to 
    #/ <see cref="ConversionType.Geo2Proj"/> and vice versa.
    #/ </para>
    #/ </summary>
    def InvertOrder(self):
      MzCartDLL.MzConverterInvertOrder(self._mzConverterPointer);
      # Invert projection strings
      tmp = self.ProjectionStringSource
      _projectionStringSource = self.ProjectionStringTarget
      _projectionStringTarget = tmp
      # Also invert conversion type for the "non-symmetric" cases, as CMzDatumConverter class does
      if (self._typeOfConversion == ReprojectorConversionType.Proj2Geo):
        self._typeOfConversion = ReprojectorConversionType.Geo2Proj;
      elif (self._typeOfConversion == ReprojectorConversionType.Geo2Proj):
        self._typeOfConversion = ReprojectorConversionType.Proj2Geo;

    def __getDoDatumConversions(self):
        # The method in MZCart is GetBypassXYZ(), and the method to bypass is BypassXYZ().
        # It is not possible to have an BypassXYZ get-property and method at the same time,
        # so this is instead called DoDatumConversion with the inverted bolean value,
        # and then the BypassXYZ method is kept.
        return not MzCartDLL.MzConverterGetBypassXYZ(self._mzConverterPointer);

    #/ <summary>
    #/ Flag informing whether datum conversions are enabled or disabled.
    #/ <para>
    #/ Datum conversions are by default enabled, 
    #/ and disabled only if the datums (ellipsoids) of the source and 
    #/ target are the same, AND no datum shifts has been specified.
    #/ </para>
    #/ <para>
    #/ Datum conversions can be explicitly bypassed by calling <see cref="BypassDatumConversions"/>.
    #/ </para>
    #/ The flag can be reset to its default value by calling <see cref="ResetDoDatumConversions"/>.
    #/ <para>
    #/ Call to any of the SetDatumShiftParameters or the <see cref="SetNoDatumShift"/>
    #/ methods will also revert this flag to its default value.
    #/ </para>
    #/ </summary>
    DoDatumConversions = property(__getDoDatumConversions)

    #/ <summary>
    #/ Explicitly bypass datum conversions, setting the <see cref="DoDatumConversions"/> to false.
    #/ </summary>
    def BypassDatumConversions(self):
      MzCartDLL.MzConverterBypassXYZ(self._mzConverterPointer);

    #/ <summary>
    #/ Reset the <see cref="DoDatumConversions"/> flag to its default value.
    #/ </summary>
    def ResetDoDatumConversions(self):
      MzCartDLL.MzConverterResetBypassXYZ(self._mzConverterPointer);

    #/ <summary>
    #/ Disable datum shift calculations for either the source or the target.
    #/ <para>
    #/ This call will reset the <see cref="BypassDatumConversions"/> flag
    #/ </para>
    #/ </summary>
    #/ <param name="side">Side to apply to, source or target</param>
    def SetNoDatumShift(self, side: ReprojectorSide):
      self.SetDatumShift(ReprojectorDatumShiftType.NoDatumShift, None, side == ReprojectorSide.Source);

    #/ <summary>
    #/ Sets the 3-parameter datum shift parameters of either the source or the target map projection.
    #/ <para>
    #/ This call will reset the <see cref="BypassDatumConversions"/> flag
    #/ </para>
    #/ </summary>
    #/ <param name="side">Side to apply to, source or target</param>
    #/ <param name="dx">dx in meters</param>
    #/ <param name="dy">dy in meters</param>
    #/ <param name="dz">dz in meters</param>
    def SetDatumShift3Parameters(self, side: ReprojectorSide, dx: float, dy: float, dz: float):
      datumParams = np.array([dx, dy, dz], dtype=np.float64);
      self.SetDatumShift(ReprojectorDatumShiftType.Param3, datumParams, side == ReprojectorSide.Source);

    #/ <summary>
    #/ Sets the 7-parameter datum shift parameters of either the source or the target map projection.
    #/ </summary>
    #/ <param name="side">Side to apply to, source or target</param>
    #/ <param name="dx">dx in meters</param>
    #/ <param name="dy">dy in meters</param>
    #/ <param name="dz">dz in meters</param>
    #/ <param name="rx">Rx in radians. Be aware: Often rotation parameters are given in arcsec</param>
    #/ <param name="ry">Ry in radians. Be aware: Often rotation parameters are given in arcsec</param>
    #/ <param name="rz">Rz in radians. Be aware: Often rotation parameters are given in arcsec</param>
    #/ <param name="sc">Scale difference, dimensionless. Be aware: Often the scale difference is given in ppm</param>
    def SetDatumShift7Parameters(self, side: ReprojectorSide, dx: float, dy: float, dz: float, rx: float, ry: float, rz: float, sc: float):
      datumParams = np.array([dx, dy, dz, rx, ry, rz, sc], dtype=np.float64);
      self.SetDatumShift(ReprojectorDatumShiftType.Param7, datumParams, side == ReprojectorSide.Source);

    #/ <summary>
    #/ Functions that sets the datum shift parameters of either the source or the target map projection.
    #/ </summary>
    def SetDatumShift(self, typeOfDatumShift: ReprojectorDatumShiftType, datumParams: np.ndarray, source: bool):
      if   typeOfDatumShift is ReprojectorDatumShiftType.NoDatumShift:
          datumParamsdata = ctypes.c_void_p(0)
          pass;
      elif typeOfDatumShift is ReprojectorDatumShiftType.Param3:
          if (datumParams is None):
            raise TypeError("datumParams is None")
          if (datumParams.size < 3):
            raise Exception("Length of datum shift parameters must be at least three");
          datumParamsdata = datumParams.ctypes.data
      elif typeOfDatumShift is ReprojectorDatumShiftType.Param7:
          if (datumParams is None):
            raise TypeError("datumParams is None")
          if (datumParams.size < 7):
            raise Exception("Length of datum shift parameters must be at least seven");
          datumParamsdata = datumParams.ctypes.data
      else:
          raise IndexError("typeOfDatumShift")
      MzCartDLL.Wrapper.C_MZDC_SETDATUMSHIFT(self._mzConverterPointer, ctypes.c_int32(typeOfDatumShift), datumParamsdata, ctypes.c_int32(1 if source else 0));


    #/ <summary>
    #/ Converts a point (x, y) from the source map projection to the target map projection.
    #/ </summary>
    def ConvertXY(self, x: float, y: float) -> Tuple[float,float]:
      return MzCartDLL.MzConverterConvertXY(self._mzConverterPointer, x, y);

    #/ <summary>
    #/ Inverse conversion, converts a point (x, y) from the target map projection to the source map projection.
    #/ </summary>
    def InvConvertXY(self, x: float, y: float) -> Tuple[float,float]:
      return MzCartDLL.MzConverterInvConvertXY(self._mzConverterPointer, x, y);

    #/ <summary>
    #/ Converts a point (x, y, h) from the source map projection to the target map projection.
    #/ </summary>
    def ConvertXYH(self, x: float, y: float, h: float) -> Tuple[float,float,float]:
      return MzCartDLL.MzConverterConvertXYH(self._mzConverterPointer, x, y, h);

    #/ <summary>
    #/ Inverse conversion, converts a point (x, y, h) from the target map projection to the source map projection.
    #/ </summary>
    def InvConvertXYH(self, x: float, y: float, h: float) -> Tuple[float,float,float]:
      return MzCartDLL.MzConverterInvConvertXYH(self._mzConverterPointer, x, y, h);

    #/ <summary>
    #/ Converts a point in Euclidean coordinates (x, y, z) relative to the source datum center to 
    #/ Euclidean coordinates relative to the target datum center. 
    #/ <para>
    #/ This is done in a two step process. First the coordinates are converted from the source 
    #/ datum center to an arbitrary geocentric Euclidean space, and from there it's converted
    #/ to the target datum center.
    #/ </para>
    #/ </summary>
    #/ <param name="x">Euclidean x coordinate</param>
    #/ <param name="y">Euclidean y coordinate</param>
    #/ <param name="z">Euclidean z coordinate</param>
    def DatumShift(self, x: float, y: float, z: float) -> Tuple[float,float,float]:
      return MzCartDLL.MzConverterDatumShift(self._mzConverterPointer, x, y, z);

    #/ <summary>
    #/ Inverse conversion, converts a point in Euclidean coordinates (x, y, z) relative to the 
    #/ target datum center to Euclidean coordinates relative to the source datum center. 
    #/ <para>
    #/ This is done in a two step process. First the coordinates are converted from the target 
    #/ datum center to an arbitrary geocentric Euclidean space, and from there it's converted
    #/ to the source datum center.
    #/ </para>
    #/ </summary>
    #/ <param name="x">Euclidean x coordinate</param>
    #/ <param name="y">Euclidean y coordinate</param>
    #/ <param name="z">Euclidean z coordinate</param>
    def InvDatumShift(self, x: float, y: float, z: float) -> Tuple[float,float,float]:
      return MzCartDLL.MzConverterInvDatumShift(self._mzConverterPointer, x, y, z);
