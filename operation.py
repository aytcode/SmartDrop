from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import uuid
import datetime


@dataclass
class FileMoveRecord:
    source: str
    destination: str
    original_name: str
    new_name: str
    category: str
    size_bytes: int = 0
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileMoveRecord":
        return cls(**data)


@dataclass
class BatchOperation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    base_folder: str = ""
    records: List[FileMoveRecord] = field(default_factory=list)
    total_files: int = 0
    successful_moves: int = 0
    failed_moves: int = 0
    is_undone: bool = False
    undo_timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "base_folder": self.base_folder,
            "records": [r.to_dict() for r in self.records],
            "total_files": self.total_files,
            "successful_moves": self.successful_moves,
            "failed_moves": self.failed_moves,
            "is_undone": self.is_undone,
            "undo_timestamp": self.undo_timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchOperation":
        records = [FileMoveRecord.from_dict(r) for r in data.get("records", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", ""),
            base_folder=data.get("base_folder", ""),
            records=records,
            total_files=int(data.get("total_files", len(records))),
            successful_moves=int(data.get("successful_moves", 0)),
            failed_moves=int(data.get("failed_moves", 0)),
            is_undone=bool(data.get("is_undone", False)),
            undo_timestamp=data.get("undo_timestamp")
        )
