from __future__ import annotations

import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any
import subprocess
import platform
import struct

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def download_nuget_package(
    package_id: str, version: str, output_dir: str | Path
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
    # Otherwise a rebuild keeps the previous build's renamed copies.
    for folder in (bin_windows, bin_linux):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)

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
        (pkg.attrib["id"], pkg.attrib["version"]) for pkg in root.findall("package")
    ]


# Must match LIB_TAG in mikecore/__init__.py. The Windows DLLs aren't renamed:
# patching their imports would invalidate DHI's signature (ADR 0002).
LIB_TAG = "-mikecore-python"


def tagged(name: str) -> str:
    """libintlc.so.5 -> libintlc-mikecore-python.so.5"""
    return name.replace(".so", LIB_TAG + ".so", 1)


def isolate_linux_libs(bin_folder: str | Path):
    """Unique names (#45), and DT_RPATH rather than DT_RUNPATH so
    LD_LIBRARY_PATH can't override $ORIGIN."""
    patchelf_path = shutil.which("patchelf")
    libs = list(Path(bin_folder).glob("*.so*"))
    renames = {so.name: tagged(so.name) for so in libs}
    for so in libs:
        new_name = renames[so.name]
        print(f"Isolating {so.name} as {new_name}")
        args = [
            patchelf_path,
            "--force-rpath",
            "--set-rpath",
            "$ORIGIN",
            "--set-soname",
            new_name,
        ]
        for old, new in renames.items():
            args += ["--replace-needed", old, new]
        subprocess.run(args + [str(so.absolute())], check=True)
        so.replace(so.with_name(new_name))


def check_isolated(bin_folder: str | Path) -> None:
    libs = [lib for lib in Path(bin_folder).iterdir() if ".so" in lib.name]
    untagged = {lib.name.replace(LIB_TAG, "") for lib in libs}
    problems = []
    for lib in libs:
        if print_elf(lib, "--print-soname") != [lib.name]:
            problems.append(f"{lib.name}: SONAME isn't the file name")
        if print_elf(lib, "--print-rpath") != ["$ORIGIN"]:
            problems.append(f"{lib.name}: RPATH isn't $ORIGIN")
        problems += [
            f"{lib.name}: needs untagged {name}"
            for name in print_elf(lib, "--print-needed")
            if name in untagged
        ]
    if problems:
        raise RuntimeError("Bundled libraries aren't isolated:\n" + "\n".join(problems))


def check_signed(bin_folder: str | Path) -> None:
    """Checks a signature is present, not that it's valid."""
    unsigned = [dll.name for dll in Path(bin_folder).glob("*.dll") if not signed(dll)]
    if unsigned:
        raise RuntimeError("Bundled DLLs aren't signed: " + ", ".join(unsigned))


def signed(dll: Path) -> bool:
    data = dll.read_bytes()
    optional_header = struct.unpack_from("<I", data, 0x3C)[0] + 24
    pe32_plus = struct.unpack_from("<H", data, optional_header)[0] == 0x20B
    # Data directory 4 is the certificate table; each entry is 8 bytes.
    data_directories = optional_header + (112 if pe32_plus else 96)
    return struct.unpack_from("<I", data, data_directories + 4 * 8 + 4)[0] > 0


def print_elf(lib: Path, flag: str) -> list[str]:
    query = [shutil.which("patchelf"), flag, str(lib)]
    return subprocess.run(
        query, check=True, capture_output=True, text=True
    ).stdout.split()


def setup():
    """Setup function to download NuGet packages and copy native libraries into bin folder."""
    packages = read_packages_config("buildUtil/packages.config")
    for name, version in packages:
        download_nuget_package(name, version, output_dir="packages")
    copy_native_libs_to_bin("packages", "mikecore/bin")

    check_signed("mikecore/bin/windows")
    if platform.system().lower() == "linux":
        isolate_linux_libs("mikecore/bin/linux")
        check_isolated("mikecore/bin/linux")


class BuildHook(BuildHookInterface):
    """Custom build hook to run setup during the build process."""

    def initialize(self, version: str, build_data: dict[str:Any]) -> None:
        """Initialize the build hook."""
        setup()


if __name__ == "__main__":
    setup()
