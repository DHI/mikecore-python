from importlib.metadata import version

import mikecore


def test_version_matches_installed_package():
    # pyproject.toml is the one place the version is set; mikecore.__version__
    # must report what was installed from it.
    assert mikecore.__version__ == version("mikecore")
