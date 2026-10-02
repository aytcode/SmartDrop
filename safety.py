from pathlib import Path
from typing import Tuple, List
from smartdrop.utils.system_paths import is_system_directory


class SafetyGuard:
    """
    Enforces non-destructive file operations and guards against system corruption.
    Ensures SmartDrop never touches Windows / system directories, never deletes,
    and never overwrites files.
    """

    @staticmethod
    def validate_target_directory(directory: Path) -> Tuple[bool, str]:
        """Validate if directory is safe to scan and organize."""
        if not directory.exists():
            return False, f"Klasör mevcut değil: '{directory}'"

        if not directory.is_dir():
            return False, f"Seçilen yol bir klasör değil: '{directory}'"

        # Check system directory rules
        is_sys, reason = is_system_directory(directory)
        if is_sys:
            return False, reason

        return True, ""

    @staticmethod
    def validate_move(source: Path, destination: Path) -> Tuple[bool, str]:
        """Validate a single move operation."""
        if not source.exists():
            return False, f"Kaynak dosya bulunamadı: '{source.name}'"

        # Safety check: Cannot move directory into itself
        try:
            if destination.resolve() == source.resolve():
                return False, f"Kaynak ve hedef dosya aynı: '{source.name}'"
        except Exception:
            pass

        # Protect against writing to system directory
        is_sys, reason = is_system_directory(destination.parent)
        if is_sys:
            return False, f"Güvenlik engeli: {reason}"

        return True, ""
