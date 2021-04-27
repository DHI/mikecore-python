import unittest
from tests.test_util import *
from mikecore.Projections import *


class MapProjectionsTest(unittest.TestCase):
    def test_MapProjectionStaticMethods(self):
      Assert.IsTrue(MapProjection.IsValid(ProjectionStrings.Osgb));
      Assert.IsTrue(MapProjection.IsValid(ProjectionStrings.Osgb));
      Assert.IsTrue(MapProjection.IsValid("UTM-33"));
      Assert.IsTrue(MapProjection.IsValid(ProjectionStrings.Utm33Dhi));
      Assert.IsTrue(MapProjection.IsValid(ProjectionStrings.Utm33N));
      Assert.IsTrue(MapProjection.IsValid(ProjectionStrings.GeoGCSWgs84));

      Assert.IsFalse(MapProjection.HasDatum(ProjectionStrings.NonUtm));
      Assert.IsFalse(MapProjection.HasDatum(ProjectionStrings.LongLat));
      Assert.IsTrue(MapProjection.HasDatum(ProjectionStrings.Osgb));
      Assert.IsTrue(MapProjection.HasDatum("UTM-33"));

      Assert.IsTrue(MapProjection.IsLocal(ProjectionStrings.NonUtm));
      Assert.IsFalse(MapProjection.IsLocal(ProjectionStrings.Osgb));

      Assert.IsFalse(MapProjection.IsLongLat(ProjectionStrings.NonUtm));
      Assert.IsTrue(MapProjection.IsLongLat(ProjectionStrings.LongLat));
      Assert.IsFalse(MapProjection.IsLongLat(ProjectionStrings.Osgb));

      Assert.IsFalse(MapProjection.IsGeoreferenced(ProjectionStrings.NonUtm));
      Assert.IsTrue(MapProjection.IsGeoreferenced(ProjectionStrings.Osgb));

      Assert.IsFalse(MapProjection.IsGeographical(ProjectionStrings.Utm33N));
      Assert.IsTrue(MapProjection.IsGeographical(ProjectionStrings.GeoGCSWgs84));
      Assert.IsTrue(MapProjection.IsGeographical(ProjectionStrings.GeoGcsArc1950));

      Assert.AreEqual("UTM-33", MapProjection.Longitude2UtmZone(14.5));
      Assert.AreEqual("UTM-30", MapProjection.Longitude2UtmZone(-1));
      Assert.AreEqual("UTM-1", MapProjection.Longitude2UtmZone(-177));
      Assert.AreEqual("UTM-60", MapProjection.Longitude2UtmZone(178));

      shortName = MapProjection.ProjectionShortName(ProjectionStrings.Utm33N);
      Assert.AreEqual("WGS_1984_UTM_Zone_33N", shortName);
      shortName = MapProjection.ProjectionShortName(ProjectionStrings.Utm33Dhi);
      Assert.AreEqual("UTM-33", shortName);
      shortName = MapProjection.ProjectionShortName(ProjectionStrings.GaussKruger27E);
      Assert.AreEqual("Pulkovo_1995_3_Degree_GK_CM_27E", shortName);
      shortName = MapProjection.ProjectionShortName(ProjectionStrings.GeoGCSWgs84);
      Assert.AreEqual("GCS_WGS_1984", shortName);

      lon, lat = MapProjection.ProjectionOrigin(ProjectionStrings.Utm33N);
      Assert.AreEqual(15, lon, 1e-12);
      Assert.AreEqual(0, lat);
      lon, lat = MapProjection.ProjectionOrigin(ProjectionStrings.GaussKruger27E);
      Assert.AreEqual(27, lon, 1e-12);
      Assert.AreEqual(0, lat);

    def test_MapProjection(self):
      mapProj = MapProjection(ProjectionStrings.Utm33N);
      Assert.AreEqual("WGS_1984_UTM_Zone_33N", mapProj.Name);
      Assert.AreEqual(ProjectionStrings.Utm33N, mapProj.ProjectionString);

      lon, lat = mapProj.GetOrigin();
      Assert.AreEqual(15, lon, 1e-12);
      Assert.AreEqual(0, lat);
      # Be aware that origin is not (0,0) in (east,north)
      east, north = mapProj.Geo2Proj(15, 0);
      Assert.AreEqual(500000, east);
      Assert.AreEqual(0, north);

      Assert.AreEqual(1.63852445868573, mapProj.GetConvergence(17, 55), 1e-10);
      Assert.AreEqual(-1.63852445868573, mapProj.GetConvergence(13, 55), 1e-10);

      east, north = mapProj.Geo2Proj(17, 55);
      Assert.AreEqual(ProjectionStrings.EastRef, east, 1e-9);
      Assert.AreEqual(ProjectionStrings.NorthRef, north, 1e-9);

      lon, lat = mapProj.Proj2Geo(east, north);
      Assert.AreEqual(17, lon, 1e-10);
      Assert.AreEqual(55, lat, 1e-10);

      x, y, z = mapProj.Geo2Xyz(17, 55, 0);
      Assert.AreEqual(3506380.823629681, x, 1e-6);
      Assert.AreEqual(1072008.1986618813, y, 1e-6);
      Assert.AreEqual(5201383.5232022731, z, 1e-6);
      lon, lat, height = mapProj.Xyz2Geo(x, y, z);
      Assert.AreEqual(17, lon, 1e-10);
      Assert.AreEqual(55, lat, 1e-10);

    def test_MapProjectionRotationTest(self):
      projStr = "PROJCS[\"NZGD_2000_New_Zealand_Transverse_Mercator\",GEOGCS[\"GCS_NZGD_2000\",DATUM[\"D_NZGD_2000\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",1600000.0],PARAMETER[\"False_Northing\",10000000.0],PARAMETER[\"Central_Meridian\",173.0],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]";
      mapProj = MapProjection(projStr);
      Assert.AreEqual(-1.0137373102179, mapProj.Proj2GeoRotation(1752001, 5947201, 0), 1e-12);
      Assert.AreEqual(33.9862626897826, mapProj.Proj2GeoRotation(1752001, 5947201, 35), 1e-12);
      Assert.AreEqual(1.0137373102179, mapProj.Geo2ProjRotation(174.69959105465122, -36.608598377616083, 0), 1e-12);
      Assert.AreEqual(36.0137373102179, mapProj.Geo2ProjRotation(174.69959105465122, -36.608598377616083, 35), 1e-12);

    def test_MapProjectionCompare(self):

      projStr1 = "PROJCS[\"SWEREF99_12_00\",GEOGCS[\"GCS_SWEREF99\",DATUM[\"D_SWEREF99\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",150000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",12.0],PARAMETER[\"Scale_Factor\",1.0],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]";
      projStr2 = "PROJCS[\"SWEREF99 12 00\",GEOGCS[\"SWEREF99\",DATUM[\"SWEREF99\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6619\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.01745329251994328,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4619\"]],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",12],PARAMETER[\"scale_factor\",1],PARAMETER[\"false_easting\",150000],PARAMETER[\"false_northing\",0],AUTHORITY[\"EPSG\",\"3007\"],AXIS[\"y\",EAST],AXIS[\"x\",NORTH]]";
      projStr3 = "PROJCS[\"SWEREF99 12 00\",GEOGCS[\"SWEREF99\",DATUM[\"SWEREF99\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6619\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AXIS[\"Latitude\",NORTH],AXIS[\"Longitude\",EAST],AUTHORITY[\"EPSG\",\"4619\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",12],PARAMETER[\"scale_factor\",1],PARAMETER[\"false_easting\",150000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Northing\",NORTH],AXIS[\"Easting\",EAST],AUTHORITY[\"EPSG\",\"3007\"]]";
      b12 = MapProjection.AreIdentical(projStr1, projStr2);
      b13 = MapProjection.AreIdentical(projStr1, projStr3);
      b23 = MapProjection.AreIdentical(projStr2, projStr3);
      Assert.AreEqual(b12, True);
      Assert.AreEqual(b13, False);
      Assert.AreEqual(b23, False);

class CartographyTests(unittest.TestCase):
    #/ <summary>
    #/ Test of how to get the long projection string from the short projection string
    #/ </summary>
    def test_ShortNameTest(self):
      cart = Cartography("UTM-33");
      Assert.AreEqual("UTM-33", cart.ProjectionName);
      Assert.AreEqual(ProjectionStrings.Utm33Dhi, cart.ProjectionString);

    def test_CartographyTest(self):
      self._CheckUTM33Zone(ProjectionStrings.Utm33N);
      self._CheckUTM33Zone("UTM-33");

    def _CheckUTM33Zone(self, utm33String):
       
      ###############################/
      # First check - same as using MzMapProj (default origin and orientation)
      cart = Cartography(utm33String);

      east, north = cart.Geo2Proj(17, 55);
      Assert.AreEqual(ProjectionStrings.EastRef, east, 1e-9);
      Assert.AreEqual(ProjectionStrings.NorthRef, north, 1e-9);

      lon, lat = cart.Proj2Geo(east, north);
      Assert.AreEqual(17, lon, 1e-10);
      Assert.AreEqual(55, lat, 1e-10);

      # Now this subtracts the false-easting of 500000
      x, y = cart.Geo2Xy(17, 55);
      Assert.AreEqual(ProjectionStrings.EastRef - 500000, x, 1e-9);
      Assert.AreEqual(ProjectionStrings.NorthRef, y, 1e-9);

      lon, lat = cart.Xy2Geo(x, y);
      Assert.AreEqual(17, lon, 1e-10);
      Assert.AreEqual(55, lat, 1e-10);

      tmpX, tmpY = cart.Proj2Xy(east, north);
      Assert.AreEqual(x, tmpX, 1e-6);
      Assert.AreEqual(y, tmpY, 1e-6);

      tmpX, tmpY = cart.Xy2Proj(x, y);
      Assert.AreEqual(east, tmpX, 1e-6);
      Assert.AreEqual(north, tmpY, 1e-6);

      Assert.AreEqual(0, cart.OrientationProj);

      Assert.AreEqual(0, cart.GetTrueNorth(0, 0));
      # This equals the convergence from the map projection
      Assert.AreEqual(1.638524458686073, cart.GetTrueNorth(x, y), 1e-10);
      Assert.AreEqual(-1.638524458686073, cart.GetTrueNorth(-x, y), 1e-10);
      Assert.AreEqual(1.638524458686073, cart.Projection().GetConvergence(17, 55), 1e-10);


      ###############################/
      # Second check, rotate -45 clockwise, (x,y)=(1,1) is almost north
      cart = Cartography(utm33String, 17, 55, -45);
      if (len(utm33String) > 10):
        Assert.AreEqual("WGS_1984_UTM_Zone_33N", cart.ProjectionName);
        Assert.AreEqual(ProjectionStrings.Utm33N, cart.ProjectionString);
      else:
        Assert.AreEqual("UTM-33", cart.ProjectionName);
        Assert.AreEqual(ProjectionStrings.Utm33Dhi, cart.ProjectionString);

      Assert.AreEqual(17, cart.LonOrigin);
      Assert.AreEqual(55, cart.LatOrigin);
      Assert.AreEqual(-45, cart.Orientation);

      # Same as before
      east, north = cart.Geo2Proj(17, 55);
      Assert.AreEqual(ProjectionStrings.EastRef, east, 1e-9);
      Assert.AreEqual(ProjectionStrings.NorthRef, north, 1e-9);

      lon, lag = cart.Proj2Geo(east, north);
      Assert.AreEqual(17, lon, 1e-10);
      Assert.AreEqual(55, lat, 1e-10);

      # Should now be zero
      x, y = cart.Geo2Xy(17, 55);
      Assert.AreEqual(0, x);
      Assert.AreEqual(0, y);

      lon, lat = cart.Xy2Geo(x, y);
      Assert.AreEqual(17, lon, 1e-10);
      Assert.AreEqual(55, lat, 1e-10);

      # Go into "north" direction in (x,y), small difference in east, big in north
      east, north = cart.Xy2Proj(100, 100);
      Assert.AreEqual(ProjectionStrings.EastRef - 4.0437667433, east, 1e-6);
      Assert.AreEqual(ProjectionStrings.NorthRef + 141.363531189, north, 1e-6);

      x, y = cart.Proj2Xy(east, north);
      Assert.AreEqual(100, x, 1e-6);
      Assert.AreEqual(100, y, 1e-6);

      # Check projectionNorth, which is constant over the entire domain
      convergence = cart.Projection().GetConvergence(17, 55);
      Assert.AreEqual(cart.Orientation - convergence, cart.OrientationProj);

      # Check True North in center point, which equals the orientation
      Assert.AreEqual(cart.Orientation, cart.GetTrueNorth(0, 0), 1e-10);

      # Check True North somewhere else, needs to add a convergence delta to orientation
      x = 10000;
      y = 10000;
      lon, lat = cart.Xy2Geo(x, y);
      easth, north = cart.Xy2Proj(x, y);
      deltaConvergence = cart.Projection().GetConvergence(lon, lat) - cart.Projection().GetConvergence(17, 55);
      Assert.AreEqual(cart.Orientation + deltaConvergence, cart.GetTrueNorth(x, y));
      Assert.AreEqual(cart.OrientationProj + cart.Projection().GetConvergence(lon, lat), cart.GetTrueNorth(x, y));

    #/ <summary>
    #/ Test showing how to move origin of grid
    #/ </summary>
    def test_OriginTest(self):
      # (x,y) coordinates in first origin
      xMin = -100000;
      xMax = 150000;
      yMin = -10000;
      yMax = 90000;

      # first origin
      lon = 17;
      lat = 55;
      
      # orientation towards projected north
      orientationProj = 40;

      dx = (xMax - xMin) / 2;
      dy = (yMax - yMin) / 2;

      # Create first cartography object
      mapProj = MapProjection("UTM-32");
      convergence = mapProj.GetConvergence(lon, lat);
      cart = Cartography("UTM-32", lon, lat, orientationProj + convergence);

      # For new origin, find new (lon,lat) origin and orientation
      lon2, lat2 = cart.Xy2Geo(xMin, yMin);
      orientation2 = cart.GetTrueNorth(xMin, yMin);

      # Create new cartography object
      cart2 = Cartography("UTM-32", lon2, lat2, orientation2);

      # Projection north of the two cartography objects should equal
      Assert.AreEqual(orientationProj, cart.OrientationProj);
      Assert.AreEqual(orientationProj, cart2.OrientationProj);

      # east/nort coordinates using the two cartography objects should equal
      for j in range(3):
        for k in range(3):
          east1, north1 = cart.Xy2Proj(xMin + j*dx, yMin + k*dy);
          east2, north2 = cart2.Xy2Proj(j * dx, k * dy);
          Assert.AreEqual(east1, east2, 1e-6);
          Assert.AreEqual(north1, north2, 1e-5);


    def test_EastNorthOriginTest(self):
      cart = Cartography.CreateGeoOrigin(ProjectionStrings.Utm33N, 17, 55, 35);
      cart2 = Cartography.CreateProjOrigin(ProjectionStrings.Utm33N, cart.EastOrigin, cart.NorthOrigin, cart.OrientationProj);

      Assert.AreEqual(cart.LonOrigin, cart2.LonOrigin, 1e-12);
      Assert.AreEqual(cart.LatOrigin, cart2.LatOrigin, 1e-10);
      Assert.AreEqual(cart.Orientation, cart2.Orientation, 1e-12);
      Assert.AreEqual(cart.EastOrigin, cart2.EastOrigin, 1e-6);
      Assert.AreEqual(cart.NorthOrigin, cart2.NorthOrigin, 1e-5);
      Assert.AreEqual(cart.OrientationProj, cart2.OrientationProj);



class ReprojectorTests(unittest.TestCase):

    def test_ConversionTest(self):
      tolerance = 5e-9;

      projNad = MapProjection(ProjectionStrings.Utm20NNad1927);
      projWgs = MapProjection(ProjectionStrings.Utm20NWgs84);
      reprojector = Reprojector(ProjectionStrings.Utm20NNad1927, ProjectionStrings.Utm20NWgs84);

      # Test values from MapProjections
      lonN, latN = projNad.Proj2Geo(35000, 6000000);
      lonW, latW = projWgs.Proj2Geo(35000, 6000000);
      east, north = projWgs.Geo2Proj(lonW, latW);
      Assert.AreEqual(35000, east, 1e-7);
      Assert.AreEqual(6000000, north, 1e-5);


      # No height
      x = 35000; y = 6000000;
      x, y = reprojector.ConvertXY(x, y);
      Assert.AreEqual(34993.681407676428, x, tolerance);
      Assert.AreEqual(5999989.6551062316, y, tolerance);

      # Height of zero, should give same results as without height
      x = 35000; y = 6000000; h = 0;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(34993.681407676428, x, tolerance);
      Assert.AreEqual(5999989.6551062316, y, tolerance);
      Assert.AreEqual(-85.89599690400064, h, tolerance);
      
      # Non-zero height, x and y are slightly different
      # Default reference values
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(34993.681764005509, x, tolerance);
      Assert.AreEqual(5999989.6586505556, y, tolerance);
      Assert.AreEqual(14.104003031738102, h, tolerance);

      # Calculate GEO position from NAD pos in WGS 84
      lonNW, latNW = projWgs.Proj2Geo(x, y);

      # Test Proj2Geo - default reference values in lon-lat
      reprojector.TypeOfConversion = ReprojectorConversionType.Proj2Geo;
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(lonNW, x, 1e-12);
      Assert.AreEqual(latNW, y, 1e-11);
      Assert.AreEqual(14.104003031738102, h, 1e-9);

      # Test Geo2Proj - default reference values
      reprojector.TypeOfConversion = ReprojectorConversionType.Geo2Proj;
      x = lonN; y = latN; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(34993.681764005509, x, 1e-9);
      Assert.AreEqual(5999989.6586505556, y, 1e-9);
      Assert.AreEqual(14.104003031738102, h, 1e-9);

      # Test Geo2Geo - default reference values in lon-lat
      reprojector.TypeOfConversion = ReprojectorConversionType.Geo2Geo;
      x = lonN; y = latN; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(lonNW, x, 1e-12);
      Assert.AreEqual(latNW, y, 1e-11);
      Assert.AreEqual(14.104003031738102, h, 1e-9);


    def test_DatumShiftTest(self):
      tolerance = 5e-9;

      projNad = MapProjection(ProjectionStrings.Utm20NNad1927);
      projWgs = MapProjection(ProjectionStrings.Utm20NWgs84);
      reprojector = Reprojector(ProjectionStrings.Utm20NNad1927, ProjectionStrings.Utm20NWgs84);

      # Datum shift parameters from WGS-84 to Clarke-1866
      dx = 8;
      dy = -160;
      dz = -176;

      reprojector.TypeOfConversion = ReprojectorConversionType.Proj2Proj;

      # Adding datum shift on source side
      reprojector.SetDatumShift3Parameters(ReprojectorSide.Source, -dx, -dy, -dz);
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(35063.318438810413, x, tolerance);
      Assert.AreEqual(6000211.7322908947, y, tolerance);
      Assert.AreEqual(66.226006662473083, h, 1e-6);

      # Same datum shift, but on target side, which should give the same results
      reprojector.SetNoDatumShift(ReprojectorSide.Source);
      reprojector.SetDatumShift3Parameters(ReprojectorSide.Target, dx, dy, dz);
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(35063.318438810413, x, tolerance);
      Assert.AreEqual(6000211.7322908947, y, tolerance);
      Assert.AreEqual(66.226006662473083, h, 1e-6);

      # Adding datum shift that equals on source and target, which should equal out
      # i.e. same results as without datum shifts (default reference values)
      reprojector.SetDatumShift3Parameters(ReprojectorSide.Source, dx, dy, dz);
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(34993.681764005509, x, tolerance);
      Assert.AreEqual(5999989.6586505556, y, tolerance);
      Assert.AreEqual(14.104003031738102, h, tolerance);


      # Test bypassing datum conversions - different results
      reprojector.TypeOfConversion = ReprojectorConversionType.Proj2Proj;
      Assert.IsTrue(reprojector.DoDatumConversions);
      reprojector.BypassDatumConversions();
      Assert.IsFalse(reprojector.DoDatumConversions);
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(35016.405724000069, x, 1e-9);
      Assert.AreEqual(6000215.6857217392, y, 1e-9);
      Assert.AreEqual(100, h);

      # Check the results are the same when bypassing datum conversions and
      # when using MapProjections directly
      lon, lat = projNad.Proj2Geo(35000, 6000000);
      x, y = projWgs.Geo2Proj(lon, lat);
      Assert.AreEqual(35016.405724000069, x, 1e-9);
      Assert.AreEqual(6000215.6857217392, y, 1e-9);

      # Testing resetting of flag
      Assert.IsFalse(reprojector.DoDatumConversions);
      reprojector.ResetDoDatumConversions();
      Assert.IsTrue(reprojector.DoDatumConversions);

      # Testing the the SetNoDatumShift resets the BypassDatumConversions flag
      reprojector.BypassDatumConversions();
      Assert.IsFalse(reprojector.DoDatumConversions);
      reprojector.SetNoDatumShift(ReprojectorSide.Source);
      Assert.IsTrue(reprojector.DoDatumConversions);

      # Disable all special setup and check that results equals the
      # original results
      reprojector.SetNoDatumShift(ReprojectorSide.Source);
      reprojector.SetNoDatumShift(ReprojectorSide.Target);

      # Testing the the SetNoDatumShift resets the BypassDatumConversions flag
      Assert.IsTrue(reprojector.DoDatumConversions);

      # Non-zero height, x and y - original reference values
      x = 35000; y = 6000000; h = 100;
      x, y, h = reprojector.ConvertXYH(x, y, h);
      Assert.AreEqual(34993.681764005509, x, tolerance);
      Assert.AreEqual(5999989.6586505556, y, tolerance);
      Assert.AreEqual(14.104003031738102, h, tolerance);


class ProjectionStrings:
    NonUtm = "NON-UTM";
    LongLat = "LONG/LAT";
    Osgb = "OSGB";
    Utm33Short = "UTM-33";
    Utm33Dhi = "PROJCS[\"UTM-33\",GEOGCS[\"Unused\",DATUM[\"UTM Projections\",SPHEROID[\"WGS 1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",15],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]";
    Utm33N = "PROJCS[\"WGS_1984_UTM_Zone_33N\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",15],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]";

    Utm20NWgs84 = "PROJCS[\"WGS_1984_UTM_Zone_20N\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",-63],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]";
    Utm20NNad1927 = "PROJCS[\"NAD_1927_UTM_Zone_20N\",GEOGCS[\"GCS_North_American_1927\",DATUM[\"D_North_American_1927\",SPHEROID[\"Clarke_1866\",6378206.4,294.9786982]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",-63],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0],UNIT[\"Meter\",1]]";
    GaussKruger27E = "PROJCS[\"Pulkovo_1995_3_Degree_GK_CM_27E\",GEOGCS[\"GCS_Pulkovo_1995\",DATUM[\"D_Pulkovo_1995\",SPHEROID[\"Krasovsky_1940\",6378245.0,298.3]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Gauss_Kruger\"],PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",27.0],PARAMETER[\"Scale_Factor\",1.0],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]";
    GoogleMaps = "PROJCS[\"Google map\",GEOGCS[\"Unused\",DATUM[\"User defined\",SPHEROID[\"Google map (Sphere)\",6378137,0]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Geographical\"],UNIT[\"Degree\",1]]";
    GoogleMapsProj = "PROJCS[\"Sphere Mercator (Radius = 6378137)\",GEOGCS[\"GCS_Sphere WGS 1984\",DATUM[\"D_Sphere WGS 1984\",SPHEROID[\"Sphere (Radius = 6378137)\",6378137,0]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator\"],PARAMETER[\"False_Easting\",0],PARAMETER[\"False_Northing\",0],PARAMETER[\"Central_Meridian\",0],PARAMETER[\"Standard_Parallel_1\",0],UNIT[\"Meter\",1]]";

    GeoGCSWgs84 = "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]]";
    GeoGcsArc1950 = "GEOGCS[\"GCS_Arc_1950\",DATUM[\"D_Arc_1950\",SPHEROID[\"Clarke_1880_Arc\",6378249.145,293.466307656]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]]";
    GeoWatch14Km = "PROJCS[\"watch14km\",GEOGCS[\"Unused\",DATUM[\"User defined\",SPHEROID[\"Sphere (Radius = 6371000)\",6371000,0]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Rotated_Longitude_Latitude\"],PARAMETER[\"Longitude_Of_South_Pole\",80],PARAMETER[\"Latitude_Of_South_Pole\",-10],PARAMETER[\"Angle_Of_Rotation\",0],UNIT[\"Degree\",1]]";
    EastRef = 627928.19137650891;
    NorthRef = 6096620.7064931244;


if __name__ == '__main__':
    unittest.main()
