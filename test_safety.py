import pytest
from pathlib import Path
from smartdrop.core.safety import SafetyGuard
from smartdrop.utils.system_paths import is_system_directory


def test_system_directories_rejected():
    # Windows system paths
    assert is_system_directory(Path("C:/Windows"))[0] is True
    assert is_system_directory(Path("C:/Windows/System32"))[0] is True
    assert is_system_directory(Path("C:/Program Files"))[0] is True
    assert is_system_directory(Path("C:/Program Files (x86)"))[0] is True
    assert is_system_directory(Path("C:/"))[0] is True
    assert is_system_directory(Path("D:/"))[0] is True

    # Validate target directory rejects system dir
    valid, reason = SafetyGuard.validate_target_directory(Path("C:/Windows"))
    assert not valid
    assert "sistem" in reason.lower() or "windows" in reason.lower()


def test_nonexistent_directory():
    valid, reason = SafetyGuard.validate_target_directory(Path("/path/to/nonexistent/directory/xyz999"))
    assert not valid
    assert "mevcut değil" in reason.lower()


def test_safe_directory(tmp_path):
    safe_dir = tmp_path / "user_downloads"
    safe_dir.mkdir()
    valid, reason = SafetyGuard.validate_target_directory(safe_dir)
    assert valid
    assert reason == ""
