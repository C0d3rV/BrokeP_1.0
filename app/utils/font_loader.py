import os
import sys
import ctypes


def load_bundled_font(font_path: str) -> bool:
    """Loads a .ttf for this process only -- no system-wide install needed.
    Windows-only, matching BrokeP's target platform. Returns True on success."""
    if sys.platform != "win32":
        return False
    if not os.path.exists(font_path):
        return False

    FR_PRIVATE = 0x10
    added = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
    return added > 0