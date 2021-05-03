from datetime import datetime
from mikecore.DfsBuilder import DfsBuilder, DfsSimpleType, DataValueType
from mikecore.DfsFactory import DfsFactory
from mikecore.eum import eumUnit, eumQuantity, eumItem

import pytest

@pytest.fixture
def landuse():
    builder = DfsBuilder.Create()

    factory = DfsFactory()

    # Set up the header
    builder.SetDataType(0)
    builder.SetGeographicalProjection(factory.CreateProjectionGeoOrigin("NON-UTM", 0,0,0))
    builder.SetTemporalAxis(factory.CreateTemporalEqCalendarAxis(eumUnit.eumUsec, datetime(2000,  1,  1, 10, 0, 0), 0, 1))
    builder.SetSpatialAxis(factory.CreateAxisEqD2(eumUnit.eumUmeter, 62, 0, 500, 70, 0, 500))
    builder.DeleteValueFloat = -2

    # Set up dynamic items
    builder.AddCreateDynamicItem("Landuse", eumQuantity.Create(eumItem.eumIIntegerCode, eumUnit.eumUintCode), DfsSimpleType.Float, DataValueType.Instantaneous);

    return builder

def test_validate_empty_builder():

    builder = DfsBuilder("filetitle")
    
    errors = builder.Validate(dieOnError=False)

    assert len(errors) > 0


def test_empty_title(landuse : DfsBuilder, tmp_path):
        # Create and get file
        landuse.CreateFile(str(tmp_path / "notused.dfs2"))
        file = landuse.GetFile()


def test_getfile_not_possible_if_not_created(landuse: DfsBuilder):
        builder = landuse

        # Create and get file
        #builder.CreateFile("notused.dfs2") # this is an important step
        with pytest.raises(Exception):
            builder.GetFile()



def test_getfiletwice_not_allowed(landuse: DfsBuilder, tmp_path):
        builder = landuse

        # Create and get file
        builder.CreateFile(str(tmp_path / "notused.dfs2"))
        file = builder.GetFile()

        with pytest.raises(Exception):
            builder.GetFile()


def test_filetitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
        builder = landuse

        # Create and get file
        builder.CreateFile(str(tmp_path / "notused.dfs2"))
        file = builder.GetFile()

        with pytest.raises(Exception):
            builder.SetFileTitle("too late")

def test_apptitle_after_create_not_possible(landuse: DfsBuilder, tmp_path):
        builder = landuse

        # Create and get file
        builder.CreateFile(str(tmp_path / "notused.dfs2"))
        file = builder.GetFile()

        with pytest.raises(Exception):
            builder.SetApplicationTitle("too late")
