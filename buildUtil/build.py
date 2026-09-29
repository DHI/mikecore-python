from __future__ import annotations

import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any
import subprocess
import platform

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def download_nuget_package(
    package_id: str,
    version: str,
    output_dir: str | Path
) -> None:
    """
    Download a NuGet package (.nupkg) to output_dir.
    """
    package_id_lower: str = package_id.lower()
    version_lower: str = version.lower()
    url: str = f"https://api.nuget.org/v3-flatcontainer/{package_id_lower}/{version_lower}/{package_id_lower}.{version_lower}.nupkg"
    output_dir = Path(output_dir)
    nupkg_path: Path = output_dir / f"{package_id}.{version}.nupkg"
    extract_path: Path = output_dir / f"{package_id}"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {package_id} {version} from {url}...")
    with urllib.request.urlopen(url) as response, nupkg_path.open("wb") as f:
        f.write(response.read())

    print(f"Extracting {nupkg_path} to {extract_path}...")
    with zipfile.ZipFile(nupkg_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    print("Done.")

def copy_native_libs_to_bin(packages_dir: str | Path, bin_dir: str | Path) -> None:
    """
    Copy native shared libraries from NuGet packages to bin directory.
    """
    packages_dir = Path(packages_dir)
    bin_windows = Path(bin_dir) / "windows"
    bin_linux = Path(bin_dir) / "linux"
    bin_windows.mkdir(parents=True, exist_ok=True)
    bin_linux.mkdir(parents=True, exist_ok=True)

    for package in packages_dir.iterdir():
        win_native = package / "runtimes" / "win-x64" / "native"
        linux_native = package / "runtimes" / "linux-x64" / "native"

        if win_native.exists():
            for lib in win_native.glob("*"):
                dest = bin_windows / lib.name
                print(f"Copying {lib} to {dest}")
                shutil.copy2(lib, dest)

        if linux_native.exists():
            for lib in linux_native.glob("*"):
                dest = bin_linux / lib.name
                print(f"Copying {lib} to {dest}")
                shutil.copy2(lib, dest)

def read_packages_config(filepath: str | Path) -> list[tuple[str, str]]:
    """
    Reads NuGet packages.config and returns a list of (id, version) tuples.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    return [
        (pkg.attrib["id"], pkg.attrib["version"])
        for pkg in root.findall("package")
    ]

LINUX_LIB_TAG = "-mikecore"


def isolate_linux_libs(bin_folder: str | Path):
    """Keep the bundled libraries from colliding with same-named ones from a
    MIKE installation (issue #45), for example libeum.so -> libeum-mikecore.so:

    - Unique file names, SONAMEs and NEEDED entries, so the loader never
      shares a library with an engine that loaded its own copy by name.
    - DT_RPATH $ORIGIN instead of DT_RUNPATH, so dependencies resolve to this
      folder before LD_LIBRARY_PATH.
    """
    patchelf_path = shutil.which("patchelf")
    libs = [so for so in Path(bin_folder).glob("*.so*") if LINUX_LIB_TAG not in so.name]
    # libintlc.so.5 -> libintlc-mikecore.so.5
    renames = {so.name: so.name.replace(".so", LINUX_LIB_TAG + ".so", 1) for so in libs}
    for so in libs:
        new_name = renames[so.name]
        print(f"Isolating {so.name} as {new_name}")
        args = [patchelf_path, "--force-rpath", "--set-rpath", "$ORIGIN", "--set-soname", new_name]
        for old, new in renames.items():
            args += ["--replace-needed", old, new]
        subprocess.run(args + [str(so.absolute())], check=True)
        so.replace(so.with_name(new_name))

def setup():
    """Setup function to download NuGet packages and copy native libraries into bin folder.
    """
    packages = read_packages_config("buildUtil/packages.config")
    for name, version in packages:
        download_nuget_package(name, version, output_dir="packages")
    copy_native_libs_to_bin("packages", "mikecore/bin")

    if platform.system().lower() == "linux":
        isolate_linux_libs("mikecore/bin/linux")


class BuildHook(BuildHookInterface):
    """Custom build hook to run setup during the build process."""
    
    def initialize(self, version: str, build_data: dict[str : Any]) -> None:
        """Initialize the build hook."""
        setup()

if __name__ == "__main__":
    setup()