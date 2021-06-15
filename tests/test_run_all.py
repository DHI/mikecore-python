import tests.test_eum
import tests.test_projections
import tests.test_miketools
import tests.test_dfs_basic
import tests.test_dfs_temporal_axis
import tests.test_dfs_custom_block
import tests.test_dfs_spatial_axis
import tests.test_dfs_static_item
import tests.examples_dfs2
import tests.examples_dfs0
import tests.test_dfs0
import tests.test_dfs2
import tests.test_dfsu2D
import tests.test_dfsu_file
import os

if not os.path.isdir("testdata/testtmp"):
    os.mkdir("testdata/testtmp")

print("-- EUM -------------------------------------------")
eum_tests = tests.test_eum.TestEUM()
eum_tests.test_wrapper()
eum_tests.test_converter()

print("-- MapProjection ---------------------------------")
mapprojection_tests = tests.test_projections.MapProjectionsTest()
mapprojection_tests.test_MapProjectionStaticMethods();
mapprojection_tests.test_MapProjection();
mapprojection_tests.test_MapProjectionRotationTest();
mapprojection_tests.test_MapProjectionCompare();

print("-- Cartography -----------------------------------")
cartography_tests = tests.test_projections.CartographyTests()
cartography_tests.test_ShortNameTest()
cartography_tests.test_CartographyTest()
cartography_tests.test_OriginTest()
cartography_tests.test_EastNorthOriginTest()

print("-- Reprojector -----------------------------------")
reprojector_tests = tests.test_projections.ReprojectorTests()
reprojector_tests.test_ConversionTest()
reprojector_tests.test_DatumShiftTest()

print("-- miketools -------------------------------------")
miketools_tests = tests.test_miketools.Test_miketools()
miketools_tests.test_Dfs0ToAscii();

print("-- dfs misc --------------------------------------")
tests.test_dfs_basic.test_error_reporting()

print("-- dfs temporal axis -----------------------------")
custom_temporal_axis = tests.test_dfs_temporal_axis.Test_dfs_temporal_axis()
custom_temporal_axis.test_ModifyEqCalTest()

print("-- dfs custom blocks -----------------------------")
custom_block_tests = tests.test_dfs_custom_block.Test_dfs_custom_block()
custom_block_tests.test_dfs2()
custom_block_tests.test_dfsu()
custom_block_tests.test_UpdateCustomBlockDataTest()

print("-- dfs static items ------------------------------")
static_item_tests = tests.test_dfs_static_item.Test_dfs_static_item()
static_item_tests.test_static_item();

print("-- dfs0 tests ------------------------------------")
dfs0_tests = tests.test_dfs0.Dfs0Tests()
dfs0_tests.test_CreateEqTimeTest()
dfs0_tests.test_CreateEqCalTest()
dfs0_tests.test_CreateNeqTimeTest()
dfs0_tests.test_CreateNeqCalFileTest()
dfs0_tests.test_AppendEqTimeTest()
dfs0_tests.test_AppendEqCalTest()
dfs0_tests.test_AppendNeqTimeTest()
dfs0_tests.test_AppendNeqCalTest()

print("-- dfs2 tests ------------------------------------")
dfs2_tests = tests.test_dfs2.Dfs2Tests()
dfs2_tests.test_FirstExample()
dfs2_tests.test_ModifyDfs2Bathymetry()
dfs2_tests.test_ReadOresundHDTest()
dfs2_tests.test_ReadOresundBathy900Test()
dfs2_tests.test_ReadLanduseTest()
dfs2_tests.test_CreateOresundHDTest()
dfs2_tests.test_CreateOresundHDGenericTest()
dfs2_tests.test_CreateLanduseTest()
dfs2_tests.test_CreateOresundBathy900Test()
##dfs2_tests.test_ModifyAxisTest()
##dfs2_tests.test_ModifyLanduseItemInfoTest()
dfs2_tests.test_ModifyLanduseDataTest()

print("-- dfsu2D tests ----------------------------------")
dfsu2D_tests = tests.test_dfsu2D.Dfsu2DTests()
dfsu2D_tests.test_FirstExample()
dfsu2D_tests.test_FindElementForCoordinate()
dfsu2D_tests.test_CreateDfsuFromDfs2()
dfsu2D_tests.test_ExtractSubareaDfsu2D()
dfsu2D_tests.test_ExtractDfs0FromDfsuTest()
dfsu2D_tests.test_CreateOresundHDTest()
dfsu2D_tests.test_ReadOdenseHD2DTest()
dfsu2D_tests.test_CreateOdenseHD2DTest()
##dfsu2D_tests.test_UpdateGeometryOresundHDTest()
dfsu2D_tests.test_DeleteValueTest()
dfsu2D_tests.test_CreateOresundHDGenericTest()

print("-- dfsu tests ------------------------------------")
dfsuFile_tests = tests.test_dfsu_file.DfsuFileTests()
dfsuFile_tests.test_VerticalProfileSigmaReadTest()
dfsuFile_tests.test_VerticalProfileSigmaCreateTest()
dfsuFile_tests.test_VerticalProfileSigmaZReadTest()
dfsuFile_tests.test_VerticalProfileSigmaZCreateTest()
dfsuFile_tests.test_VerticalColumnReadTest()
dfsuFile_tests.test_VerticalColumnCreateTest()
dfsuFile_tests.test_Read3DSigmaZOresundTest()
dfsuFile_tests.test_Create3DSigmaZOresundTest()
dfsuFile_tests.test_Read3DSigmaOdenseTest()
dfsuFile_tests.test_Create3DSigmaOdenseTest()

print("-- Done!!! ---------------------------------------")
