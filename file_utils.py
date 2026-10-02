from pathlib import Path
import os
import stat
from typing import Tuple, Optional


def format_file_size(size_bytes: int) -> str:
    """Format bytes into readable string (B, KB, MB, GB)."""
    if size_bytes < 0:
        return "0 B"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def resolve_collision(target_dir: Path, desired_name: str) -> str:
    """
    If desired_name exists in target_dir, generate non-colliding name:
    'photo.jpg' -> 'photo (1).jpg', 'photo (2).jpg', etc.
    Guarantees no overwrite.
    """
    target_path = target_dir / desired_name
    if not target_path.exists():
        return desired_name

    p = Path(desired_name)
    stem = p.stem
    suffix = p.suffix

    counter = 1
    while True:
        candidate_name = f"{stem} ({counter}){suffix}"
        candidate_path = target_dir / candidate_name
        if not candidate_path.exists():
            return candidate_name
        counter += 1


def is_hidden_file(path: Path) -> bool:
    """Check if file or directory is hidden (dot prefix or Windows hidden attribute)."""
    name = path.name
    if name.startswith("."):
        return True

    # Windows hidden file check
    try:
        if os.name == "nt":
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs != -1 and bool(attrs & 2):  # FILE_ATTRIBUTE_HIDDEN = 0x2
                return True
    except Exception:
        pass

    return False


def get_file_timestamps(path: Path) -> Tuple[float, float, int]:
    """
    Returns (created_at, modified_at, size_bytes) safely.
    Handles unreadable or locked files without crashing.
    """
    try:
        st = path.stat()
        created = getattr(st, "st_ctime", 0.0)
        modified = getattr(st, "st_mtime", 0.0)
        size = st.st_size
        return created, modified, size
    except Exception:
        return 0.0, 0.0, 0
