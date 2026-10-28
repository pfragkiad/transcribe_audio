"""Platform-specific native library setup."""

import os
import sys
from pathlib import Path

# Make NVIDIA libraries installed in this virtual environment visible on Windows.
# Keep the handles alive so Windows retains the DLL search directories.
_cuda_dll_handles = []


def configure_utf8_stdio():
    """Use UTF-8 for console and redirected standard streams on every platform."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def configure_cuda_libraries():
    """Register virtual-environment NVIDIA DLLs before importing the backend."""
    if sys.platform != "win32" or _cuda_dll_handles:
        return

    _nvidia_dir = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    for _dll_dir in sorted(_nvidia_dir.glob("*/bin")):
        os.environ["PATH"] = str(_dll_dir) + os.pathsep + os.environ.get("PATH", "")
        _cuda_dll_handles.append(os.add_dll_directory(str(_dll_dir)))

