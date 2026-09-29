import contextlib
import os
import platform
import sys
from pathlib import Path

from mikecore._native import installation_bin, load_linux_lib

__version__ = "0.3.0a1"

if platform.machine().lower() not in ("x86_64", "amd64") or sys.maxsize <= 2**32:
    raise Exception("This library requires 64 bit Python on an x86-64 CPU")

if platform.system() == "Windows":
    bundled_bin = str(Path(__file__).parent / "bin/windows")
elif platform.system() == "Linux":
    bundled_bin = str(Path(__file__).parent / "bin/linux")
else:
    raise Exception("Unsupported platform: " + platform.system())

# MIKECORE_PYTHON_BIN opts into a MIKE installation's libraries (see README)
mikebin = os.path.abspath(installation_bin) if installation_bin else bundled_bin

from mikecore.DfsDLL import DfsDLL
from mikecore.eum import eumDLL
from mikecore.Projections import MzCartDLL

# Path is required for reading EUM.xml
DfsDLL.libfilepath = mikebin
eumDLL.libfilepath = mikebin

# On Windows, add mikebin to the process-wide DLL search path only while
# mikecore loads its DLLs, so it doesn't affect other DLLs loaded later.
# The DLLs' own LoadLibrary calls later on still work: the only bundled DLLs
# they name are ones already loaded here, which Windows reuses by name.
_dll_dir = os.add_dll_directory(mikebin) if platform.system() == "Windows" else contextlib.nullcontext()
with _dll_dir:
    if installation_bin and platform.system() == "Linux":
        # Recent libeum imports fnGetLanguage from libufs without linking to
        # it, so load libufs, which pulls in libeum, first.
        load_linux_lib(mikebin, "libufs")
    eumDLL.Init()
    MzCartDLL.Init(mikebin)
    DfsDLL.Init(mikebin)
