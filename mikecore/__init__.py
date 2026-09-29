import contextlib
import ctypes
import os
import platform
import sys
from pathlib import Path

__version__ = "0.3.0a2.dev1"

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

# Opt-in, at the user's own risk: load a MIKE installation's libraries instead
# of the bundled ones (see README). On Linux, use them under their own names,
# so an engine in the same process shares them.
installation_bin = os.environ.get("MIKECORE_PYTHON_BIN")
if installation_bin:
    mikebin = os.path.abspath(installation_bin)
    DfsDLL.libfilename = "libufs.so"
    eumDLL.libfilename = "libeum.so"
    MzCartDLL.libfilename = "libMzCart.so"

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
        ctypes.CDLL(os.path.join(mikebin, DfsDLL.libfilename))
    eumDLL.Init()
    MzCartDLL.Init(mikebin)
    DfsDLL.Init(mikebin)
