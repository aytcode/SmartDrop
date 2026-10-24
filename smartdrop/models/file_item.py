from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class FileItem:
    path: Path
    original_name: str
    original_dir: Path
    extension: str
    size_bytes: int
    created_at: float
    modified_at: float
    category: str
    target_folder_name: str
    target_dir: Path
    new_name: str
    new_path: Path
    is_selected: bool = True
    is_renamed: bool = False
    is_skipped: bool = False
    skip_reason: str = ""
    ai_suggested_category: Optional[str] = None
    ai_suggested_name: Optional[str] = None
    ai_confidence: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "original_name": self.original_name,
            "original_dir": str(self.original_dir),
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "category": self.category,
            "target_folder_name": self.target_folder_name,
            "target_dir": str(self.target_dir),
            "new_name": self.new_name,
            "new_path": str(self.new_path),
            "is_selected": self.is_selected,
            "is_renamed": self.is_renamed,
            "is_skipped": self.is_skipped,
            "skip_reason": self.skip_reason,
            "ai_suggested_category": self.ai_suggested_category,
            "ai_suggested_name": self.ai_suggested_name,
            "ai_confidence": self.ai_confidence,
            "error_message": self.error_message
        }
