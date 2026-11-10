import contextlib
import ctypes
import importlib.metadata
import os
import platform
import sys
from pathlib import Path

# The version is set in pyproject.toml and read here from the installed metadata.
try:
    __version__ = importlib.metadata.version("mikecore")
except importlib.metadata.PackageNotFoundError:
    # Imported from a checkout on sys.path without being installed.
    __version__ = "unknown"

if platform.machine().lower() not in ("x86_64", "amd64") or sys.maxsize <= 2**32:
    raise Exception("This library requires 64 bit Python on an x86-64 CPU")

if platform.system() == "Windows":
    mikebin = str(Path(__file__).parent / "bin/windows")
elif platform.system() == "Linux":
    mikebin = str(Path(__file__).parent / "bin/linux")
else:
    raise Exception("Unsupported platform: " + platform.system())

from mikecore.DfsDLL import DfsDLL
from mikecore.eum import eumDLL
from mikecore.Projections import MzCartDLL

# The build adds this tag to the bundled libraries' names (see
# buildUtil/build.py, which has the same constant), so they never collide with
# same-named libraries a MIKE engine in the same process has loaded.
LIB_TAG = "-mikecore-python"

# Opt-in, at the user's own risk: load a MIKE installation's libraries instead
# of the bundled ones (see README), under their own names, so an engine in the
# same process shares them.
installation_bin = os.environ.get("MIKECORE_PYTHON_BIN")
if installation_bin:
    mikebin = os.path.abspath(installation_bin)
    for wrapper in (DfsDLL, eumDLL, MzCartDLL):
        wrapper.libfilename = wrapper.libfilename.replace(LIB_TAG, "")

# Path is required for reading EUM.xml
DfsDLL.libfilepath = mikebin
eumDLL.libfilepath = mikebin

# On Windows, add mikebin to the process-wide DLL search path only while
# mikecore loads its DLLs, so it doesn't affect other DLLs loaded later.
# That is enough: the DLLs import each other statically, resolved while they
# load here, and none of them loads another bundled DLL by name later on.
_dll_dir = (
    os.add_dll_directory(mikebin)
    if platform.system() == "Windows"
    else contextlib.nullcontext()
)
with _dll_dir:
    if installation_bin and platform.system() == "Linux":
        # Recent libeum imports fnGetLanguage from libufs without linking to
        # it, so load libufs, which pulls in libeum, first.
        ctypes.CDLL(os.path.join(mikebin, DfsDLL.libfilename))
    eumDLL.Init()
    MzCartDLL.Init(mikebin)
    DfsDLL.Init(mikebin)
