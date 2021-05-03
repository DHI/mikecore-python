from mikecore.DfsFile import DfsFile, DfsParameters, DfsFileMode;
from mikecore.Dfs123File import Dfs123File, Dfs2File, Dfs3File
from mikecore.DfsuFile import DfsuFile

class DfsFileFactory:
    """description of class"""

    @staticmethod
    def Dfs1FileOpen(filename, parameters = None):
        dfs = Dfs123File();
        dfs.Open(filename, DfsFileMode.Read, parameters);
        return dfs;

    @staticmethod
    def Dfs1FileOpenEdit(filename, parameters = None):
        dfs = Dfs123File();
        dfs.Open(filename, DfsFileMode.Edit, parameters);
        return dfs;

    @staticmethod
    def Dfs1FileOpenAppend(filename, parameters = None):
        dfs = Dfs123File();
        dfs.Open(filename, DfsFileMode.Append, parameters);
        return dfs;


    @staticmethod
    def Dfs2FileOpen(filename, parameters = None):
        dfs = Dfs2File();
        dfs.Open(filename, DfsFileMode.Read, parameters);
        return dfs;

    @staticmethod
    def Dfs2FileOpenEdit(filename, parameters = None):
        dfs = Dfs2File();
        dfs.Open(filename, DfsFileMode.Edit, parameters);
        return dfs;

    @staticmethod
    def Dfs2FileOpenAppend(filename, parameters = None):
        dfs = Dfs2File();
        dfs.Open(filename, DfsFileMode.Append, parameters);
        return dfs;


    @staticmethod
    def Dfs3FileOpen(filename, parameters = None):
        dfs = Dfs3File();
        dfs.Open(filename, DfsFileMode.Read, parameters);
        return dfs;

    @staticmethod
    def Dfs3FileOpenEdit(filename, parameters = None):
        dfs = Dfs3File();
        dfs.Open(filename, DfsFileMode.Edit, parameters);
        return dfs;

    @staticmethod
    def Dfs3FileOpenAppend(filename, parameters = None):
        dfs = Dfs3File();
        dfs.Open(filename, DfsFileMode.Append, parameters);
        return dfs;


    @staticmethod
    def DfsuFileOpen(filename, parameters = None):
        dfsFile = DfsFileFactory.DfsGenericOpen(filename, parameters);
        return (DfsuFile(dfsFile));

    @staticmethod
    def DfsuFileOpenEdit(filename, parameters = None):
        dfsFile = DfsFileFactory.DfsGenericOpenEdit(filename, parameters);
        return (DfsuFile(dfsFile));

    @staticmethod
    def DfsuFileOpenAppend(filename, parameters):
        dfsFile = DfsFileFactory.DfsGenericOpenAppend(filename, parameters);
        return (DfsuFile(dfsFile));


    @staticmethod
    def DfsGenericOpen(filename, parameters = None):
        dfs = DfsFile();
        dfs.Open(filename, DfsFileMode.Read, parameters);
        return dfs;

    @staticmethod
    def DfsGenericOpenEdit(filename, parameters = None):
        dfs = DfsFile();
        dfs.Open(filename, DfsFileMode.Edit, parameters);
        return dfs;

    @staticmethod
    def DfsGenericOpenAppend(filename, parameters = None):
        dfs = DfsFile();
        dfs.Open(filename, DfsFileMode.Append, parameters);
        return dfs;

    @staticmethod
    def CreateDefaultParameters():
        return (DfsParameters());
