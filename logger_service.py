import datetime
import logging
from pathlib import Path
from typing import List, Callable, Optional


class AppLogger:
    """
    Central logging service for SmartDrop with in-memory subscriber callbacks
    (for UI status updates) and optional persistent file logging.
    """

    _instance: Optional["AppLogger"] = None

    def __init__(self):
        self.log_history: List[str] = []
        self.subscribers: List[Callable[[str], None]] = []

    @classmethod
    def get_instance(cls) -> "AppLogger":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def subscribe(self, callback: Callable[[str], None]) -> None:
        self.subscribers.append(callback)

    def log(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.log_history.append(entry)
        for sub in self.subscribers:
            try:
                sub(entry)
            except Exception:
                pass

    def get_logs(self) -> List[str]:
        return list(self.log_history)

    def clear(self) -> None:
        self.log_history.clear()
