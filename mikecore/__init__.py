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

# Must match LIB_TAG in buildUtil/build.py.
LIB_TAG = "-mikecore-python"

installation_bin = os.environ.get("MIKECORE_PYTHON_BIN")
if installation_bin:
    mikebin = os.path.abspath(installation_bin)
    for wrapper in (DfsDLL, eumDLL, MzCartDLL):
        wrapper.libfilename = wrapper.libfilename.replace(LIB_TAG, "")

# Path is required for reading EUM.xml
DfsDLL.libfilepath = mikebin
eumDLL.libfilepath = mikebin

# Only while loading: the DLLs resolve their imports here and load nothing by
# name later.
_dll_dir = (
    os.add_dll_directory(mikebin)
    if platform.system() == "Windows"
    else contextlib.nullcontext()
)
with _dll_dir:
    if installation_bin and platform.system() == "Linux":
        # A MIKE installation's libeum (2025 and later) uses fnGetLanguage from
        # libufs without linking to it. The bundled libeum doesn't.
        ctypes.CDLL(os.path.join(mikebin, DfsDLL.libfilename))
    eumDLL.Init()
    MzCartDLL.Init(mikebin)
    DfsDLL.Init(mikebin)
