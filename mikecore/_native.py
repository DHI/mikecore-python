"""How mikecore loads its MIKE Core libraries (issue #45)."""
import ctypes
import os

# Opt-in, at the user's own risk: a MIKE installation's bin folder to load the
# MIKE Core libraries from, instead of the ones bundled with mikecore.
installation_bin = os.environ.get("MIKECORE_PYTHON_BIN") or None


def load_linux_lib(folder, name):
    """Load MIKE Core library `name` (e.g. "libeum") from `folder`."""
    if installation_bin:
        # The installation's libraries under their own names, so an engine in
        # the same process shares them.
        return ctypes.CDLL(os.path.join(folder, name + ".so"))
    # The bundled, renamed copies.
    return ctypes.CDLL(os.path.join(folder, name + "-mikecore.so"))
