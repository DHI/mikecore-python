import os
import platform
from pathlib import Path

__version__ = "0.1.0"

p = platform.architecture()
if not "64" in p[0]:
    raise Exception("This library is 64 bit only!!!! Please use 64 bit Python")

if platform.system() == "Windows":
    mikebin = str(Path(__file__).parent / "bin/windows")
    os.environ["PATH"] = mikebin + ";" + os.environ["PATH"]
elif platform.system() == "Linux":
    mikebin = str(Path(__file__).parent / "bin/linux")
else:
    raise Exception("Unsupported platform: " + platform.system())

os.environ["LD_LIBRARY_PATH"] = mikebin

from mikecore.DfsDLL import DfsDLL
from mikecore.eum import eumDLL
from mikecore.Projections import MzCartDLL

# Path is required for reading EUM.xml
DfsDLL.libfilepath = mikebin
eumDLL.libfilepath = mikebin

eumDLL.Init()
MzCartDLL.Init(mikebin)
DfsDLL.Init(mikebin)

