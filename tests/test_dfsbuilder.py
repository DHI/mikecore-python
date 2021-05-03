from mikecore.DfsBuilder import DfsBuilder


import pytest

def test_validate_empty_builder():

    builder = DfsBuilder("filetitle")
    
    errors = builder.Validate(dieOnError=False)

    assert len(errors) > 0

    