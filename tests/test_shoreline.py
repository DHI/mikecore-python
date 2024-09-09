from mikecore.DfsFileFactory import DfsFileFactory


def test_read_shoreline_profile_dfs2():


    # this file has a problematic spatial axis unit
    filename = "testdata/shoreline_profile.dfs2"

    dfs2File = DfsFileFactory.Dfs2FileOpen(filename)

    assert dfs2File.SpatialAxis.XCount == 300
    assert dfs2File.SpatialAxis.YCount == 120