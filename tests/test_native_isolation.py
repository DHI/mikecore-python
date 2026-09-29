"""Issue #45: mikecore's bundled Linux libraries must not collide with
same-named libraries from a MIKE installation, and importing mikecore must
not change the environment that child processes inherit."""
import os
import platform
import shutil
import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")

# Names of the bundled libraries as shipped in the MIKE Core NuGet package,
# which a MIKE installation's bin also uses.
MIKE_LIB_NAMES = ["libeum.so", "libufs.so", "libpfs2004.so", "libMzCart.so", "libxerces-c-3.2.so",
                  "libimf.so", "libiomp5.so", "libsvml.so", "libirng.so", "libintlc.so.5"]

USE_MIKECORE = """
import mikecore
from mikecore.DfsFileFactory import DfsFileFactory
dfs = DfsFileFactory.DfsGenericOpen("testdata/Rain_accumulated.dfs0")
assert dfs.ReadItemTimeStepNext() is not None
dfs.Close()
"""


@pytest.fixture
def mike_bin(tmp_path):
    """Stand-in for a MIKE installation's bin: an empty library under each name."""
    cc = compiler()
    src = tmp_path / "decoy.c"
    src.write_text("int decoy;\n")
    for name in MIKE_LIB_NAMES:
        subprocess.run([cc, "-shared", "-fPIC", "-o", str(tmp_path / name), str(src)], check=True)
    return tmp_path


def default_env(**env):
    """The test process's environment, without the MIKECORE_BIN opt-in."""
    base = {k: v for k, v in os.environ.items() if k not in ("MIKECORE_BIN", "LD_LIBRARY_PATH")}
    return dict(base, **env)


def run_python(code, env):
    code = "import ctypes, os\nNAMES = %r\n%s" % (MIKE_LIB_NAMES, code)
    return subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)


def compiler():
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        pytest.skip("needs a C compiler")
    return cc


def test_bundled_libs_do_not_use_openmp():
    """So the bundled libiomp5 never starts, and can't abort with "OMP: Error
    #15" next to an engine's OpenMP runtime."""
    nm = shutil.which("nm")
    if nm is None:
        pytest.skip("needs nm")
    import mikecore
    for f in os.listdir(mikecore.mikebin):
        if ".so" in f and not f.startswith("libiomp5"):
            out = subprocess.run([nm, "-D", "--undefined-only", os.path.join(mikecore.mikebin, f)],
                                 capture_output=True, text=True, check=True).stdout
            syms = [line.split()[-1] for line in out.splitlines()]
            assert not [s for s in syms if s.startswith(("omp_", "kmp_", "__kmp", "GOMP_"))], f


def test_import_with_mike_bin_on_ld_library_path(mike_bin):
    env = default_env(LD_LIBRARY_PATH=str(mike_bin))
    r = run_python(USE_MIKECORE, env)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("mode", ["RTLD_LOCAL", "RTLD_GLOBAL"])
def test_import_after_mike_libs_loaded_by_name(mike_bin, mode):
    env = default_env(LD_LIBRARY_PATH=str(mike_bin))
    load = "for n in NAMES:\n    ctypes.CDLL(n, ctypes.%s)\n" % mode
    r = run_python(load + USE_MIKECORE, env)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("ld_library_path", [None, "", "/some/dir"])
def test_import_leaves_environment_alone(ld_library_path):
    env = default_env()
    if ld_library_path is not None:
        env["LD_LIBRARY_PATH"] = ld_library_path
    r = run_python("before = dict(os.environ)\nimport mikecore\nassert dict(os.environ) == before", env)
    assert r.returncode == 0, r.stderr


@pytest.fixture
def installation_bin(tmp_path):
    """Stand-in for a MIKE installation's bin: the bundled files, with the
    libraries also under the names an installation uses."""
    import mikecore
    bundled = os.path.join(os.path.dirname(mikecore.__file__), "bin", "linux")
    for f in os.listdir(bundled):
        os.symlink(os.path.join(bundled, f), tmp_path / f)
        if "-mikecore" in f:
            os.symlink(os.path.join(bundled, f), tmp_path / f.replace("-mikecore", ""))
    return tmp_path


def test_mikecore_bin_uses_installation(installation_bin):
    env = default_env(MIKECORE_BIN=str(installation_bin))
    code = USE_MIKECORE + "assert mikecore.mikebin == %r, mikecore.mikebin\n" % str(installation_bin)
    r = run_python(code, env)
    assert r.returncode == 0, r.stderr


def test_mikecore_bin_does_not_fall_back_to_bundled(tmp_path):
    env = default_env(MIKECORE_BIN=str(tmp_path))
    r = run_python("import mikecore", env)
    assert r.returncode != 0
    assert str(tmp_path / "libufs.so") in r.stderr
