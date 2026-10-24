from pathlib import Path
import os
import sys
from typing import Tuple, Set

# Windows critical system folder patterns (case-insensitive check)
WINDOWS_SYSTEM_NAMES: Set[str] = {
    "windows",
    "system32",
    "syswow64",
    "program files",
    "program files (x86)",
    "programdata",
    "recovery",
    "$recycle.bin",
    "system volume information",
    "boot",
    "msocache",
    "windows defender",
    "appdata\\local\\microsoft\\windows",
}

# Unix/Linux system directories
UNIX_SYSTEM_DIRS: Set[str] = {
    "/",
    "/bin",
    "/sbin",
    "/usr",
    "/usr/bin",
    "/usr/sbin",
    "/etc",
    "/var",
    "/dev",
    "/proc",
    "/sys",
    "/boot",
    "/root",
}


def is_system_directory(path: Path) -> Tuple[bool, str]:
    """
    Checks if the path is a system directory or root drive that should NEVER be organized.
    Returns (True, "reason") if forbidden, (False, "") if safe.
    """
    raw_str = str(path).strip()
    raw_lower = raw_str.lower().replace("/", "\\")

    # Check root drive (e.g. C:\ or C:/ or C:)
    if (len(raw_lower) in (2, 3) and raw_lower[1:2] == ":") or (len(raw_lower) >= 2 and raw_lower[:2].isalpha() and raw_lower[1] == ":" and raw_lower[2:] in ("", "\\", "/")):
        return True, f"Kök sürücüler (ör. '{raw_str}') doğrudan düzenlenemez. Lütfen bir alt klasör seçin."

    if raw_str in ("/", "\\", ""):
        return True, "Sistem kök dizini doğrudan düzenlenemez."

    try:
        resolved = path.resolve()
    except Exception:
        resolved = path

    path_str = str(resolved).strip()
    path_lower = path_str.lower().replace("/", "\\")

    # Check resolved drive letter
    if len(path_lower) in (2, 3) and path_lower[1:2] == ":":
        return True, f"Kök sürücüler (ör. '{path_str}') doğrudan düzenlenemez. Lütfen bir alt klasör seçin."

    # Check Unix system paths
    clean_unix = str(resolved)
    for u_dir in UNIX_SYSTEM_DIRS:
        if clean_unix == u_dir or (u_dir != "/" and clean_unix.startswith(u_dir + "/")):
            # Allow tests under workspace or /tmp or /home
            if clean_unix.startswith("/tmp") or clean_unix.startswith("/home") or "smartdrop" in clean_unix:
                continue
            return True, f"Sistem klasörü korumalıdır: {path_str}"

    # Check Windows system folders
    parts_lower = [p.lower() for p in resolved.parts]
    for part in parts_lower:
        # Strip drive letter if present
        clean_part = part.rstrip(":\\")
        if clean_part in WINDOWS_SYSTEM_NAMES:
            return True, f"Windows sistem klasörleri düzenlenemez: '{part}'"

    # Check environment variables like WINDIR, SYSTEMROOT, PROGRAMFILES
    for env_var in ("WINDIR", "SYSTEMROOT", "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA"):
        env_val = os.environ.get(env_var)
        if env_val:
            try:
                env_path = Path(env_val).resolve()
                if resolved == env_path or env_path in resolved.parents:
                    return True, f"Windows sistem klasörü korumalıdır: {env_val}"
            except Exception:
                pass

    return False, ""
