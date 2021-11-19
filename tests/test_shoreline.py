from mikecore.DfsFileFactory import DfsFileFactory


def test_read_shoreline_profile_dfs2():

    filename = "testdata/shoreline_profile.dfs2"

    dfs2File = DfsFileFactory.Dfs2FileOpen(filename)

    assert True