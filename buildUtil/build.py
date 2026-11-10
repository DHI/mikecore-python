from __future__ import annotations

import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any
import subprocess
import platform

import pefile
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
    # Start from empty folders: the libraries are renamed after copying, so
    # a rebuild would otherwise keep the previous build's renamed copies.
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


# Added to every bundled library's name, for example ufs.dll ->
# ufs-mikecore-python.dll. mikecore/__init__.py has the same constant and
# removes it when MIKECORE_PYTHON_BIN points at a MIKE installation.
LIB_TAG = "-mikecore-python"


def tagged(name: str) -> str:
    """ufs.dll -> ufs-mikecore-python.dll, libintlc.so.5 -> libintlc-mikecore-python.so.5"""
    ext = ".dll" if name.lower().endswith(".dll") else ".so"
    return name.replace(ext, LIB_TAG + ext, 1)


def isolate_linux_libs(bin_folder: str | Path):
    """Keep the bundled libraries from colliding with same-named ones from a
    MIKE installation (issue #45):

    - Unique file names, SONAMEs and NEEDED entries, so the loader never
      shares a library with an engine that loaded its own copy by name.
    - DT_RPATH $ORIGIN instead of DT_RUNPATH, so dependencies resolve to this
      folder before LD_LIBRARY_PATH.
    """
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


def isolate_windows_dlls(bin_folder: str | Path):
    """Give the bundled DLLs unique names, so Windows doesn't reuse a
    same-named DLL that a MIKE engine has already loaded, and rewrite their
    imports of each other to match (issue #45). Only static imports need
    rewriting: none of the DLLs loads a bundled DLL by name at runtime.

    Patching invalidates DHI's Authenticode signature, so it is removed.
    """
    dlls = list(Path(bin_folder).glob("*.dll"))
    renames = {dll.name.lower(): tagged(dll.name) for dll in dlls}
    for dll in dlls:
        new_name = renames[dll.name.lower()]
        print(f"Isolating {dll.name} as {new_name}")
        replace_dll_imports(dll, renames)
        dll.replace(dll.with_name(new_name))


def replace_dll_imports(dll: Path, renames: dict[str, str]) -> None:
    """Point dll's imports of the DLLs in renames (keyed by lowercase name) at
    their new names, as delvewheel does: the longer names can't overwrite the
    old ones, so they go into unused padding at the end of read-only data
    sections, and each import descriptor's Name is repointed at its new name.
    """
    pe = pefile.PE(data=dll.read_bytes())
    for entry in getattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT", []):
        if entry.dll.decode().lower() in renames:
            raise RuntimeError(f"{dll.name}: delay-load imports are not supported")
    imports = [
        entry
        for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])
        if entry.dll.decode().lower() in renames
    ]
    if not imports:
        return

    sections = sorted(pe.sections, key=lambda section: section.VirtualAddress)
    pending = list(imports)
    for i, section in enumerate(sections):
        if not is_read_only_data(section):
            continue
        # Padding: raw data past the section's in-memory size, but not past
        # the start of the next section in memory.
        end_rva = section.VirtualAddress + section.SizeOfRawData
        if i + 1 < len(sections):
            end_rva = min(end_rva, sections[i + 1].VirtualAddress)
        while pending:
            new_name = renames[pending[0].dll.decode().lower()].encode() + b"\0"
            rva = section.VirtualAddress + section.Misc_VirtualSize
            if rva + len(new_name) > end_rva:
                break
            pe.set_bytes_at_rva(rva, new_name)
            pending.pop(0).struct.Name = rva
            section.Misc_VirtualSize += len(new_name)
    if pending:
        raise RuntimeError(f"{dll.name}: no room for the new import names")

    pe.OPTIONAL_HEADER.SizeOfImage = round_up(
        sections[-1].VirtualAddress + sections[-1].Misc_VirtualSize,
        pe.OPTIONAL_HEADER.SectionAlignment,
    )
    pe.OPTIONAL_HEADER.SizeOfInitializedData = sum(
        max(
            section.SizeOfRawData,
            round_up(section.Misc_VirtualSize, pe.OPTIONAL_HEADER.FileAlignment),
        )
        for section in sections
        if section.IMAGE_SCN_CNT_INITIALIZED_DATA
    )

    # Remove the signature. It must be the only data after the image, so
    # removing it doesn't cut anything else off.
    size = len(pe.__data__)
    certificate = pe.OPTIONAL_HEADER.DATA_DIRECTORY[
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_SECURITY"]
    ]
    if certificate.Size:
        image_end = max(s.PointerToRawData + s.SizeOfRawData for s in sections)
        if (
            certificate.VirtualAddress != round_up(image_end, 8)
            or certificate.VirtualAddress + certificate.Size != size
        ):
            raise RuntimeError(
                f"{dll.name}: data besides the signature after the image"
            )
        size = image_end
        certificate.VirtualAddress = certificate.Size = 0

    patched = pefile.PE(data=pe.write()[:size])
    patched.OPTIONAL_HEADER.CheckSum = patched.generate_checksum()
    dll.write_bytes(patched.write())


def is_read_only_data(section) -> bool:
    return bool(
        section.IMAGE_SCN_CNT_INITIALIZED_DATA
        and section.IMAGE_SCN_MEM_READ
        and not section.IMAGE_SCN_CNT_CODE
        and not section.IMAGE_SCN_CNT_UNINITIALIZED_DATA
        and not section.IMAGE_SCN_MEM_EXECUTE
        and not section.IMAGE_SCN_MEM_WRITE
        and not section.IMAGE_SCN_MEM_DISCARDABLE
    )


def round_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def setup():
    """Setup function to download NuGet packages and copy native libraries into bin folder."""
    packages = read_packages_config("buildUtil/packages.config")
    for name, version in packages:
        download_nuget_package(name, version, output_dir="packages")
    copy_native_libs_to_bin("packages", "mikecore/bin")

    # pefile is pure Python, so the DLLs are patched on every platform;
    # patchelf only runs on Linux.
    isolate_windows_dlls("mikecore/bin/windows")
    if platform.system().lower() == "linux":
        isolate_linux_libs("mikecore/bin/linux")


class BuildHook(BuildHookInterface):
    """Custom build hook to run setup during the build process."""

    def initialize(self, version: str, build_data: dict[str:Any]) -> None:
        """Initialize the build hook."""
        setup()


if __name__ == "__main__":
    setup()
