from pathlib import Path
import json
import shutil
from typing import List, Optional, Tuple
from smartdrop.models.operation import BatchOperation, FileMoveRecord
from smartdrop.utils.file_utils import resolve_collision
from smartdrop.services.logger_service import AppLogger


class UndoManager:
    """
    Manages transaction history and safe reversibility of all file migrations.
    Never overwrites files even during undo operations.
    """

    def __init__(self, history_file_path: Optional[Path] = None):
        if history_file_path is None:
            # Default to user home or current directory
            home_history = Path.home() / ".smartdrop_history.json"
            self.history_file = home_history
        else:
            self.history_file = history_file_path

        self.logger = AppLogger.get_instance()

    def _load_history(self) -> List[BatchOperation]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [BatchOperation.from_dict(item) for item in data]
        except Exception as e:
            self.logger.log(f"Geçmiş yüklenirken hata: {e}", "WARNING")
            return []

    def _save_history(self, history: List[BatchOperation]) -> None:
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                data = [op.to_dict() for op in history]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.log(f"Geçmiş kaydedilirken hata: {e}", "ERROR")

    def record_operation(self, operation: BatchOperation) -> None:
        history = self._load_history()
        history.append(operation)
        self._save_history(history)
        self.logger.log(f"Yeni işlem kaydedildi: {operation.successful_moves} dosya taşındı (ID: {operation.id[:8]})")

    def get_last_active_operation(self, base_folder: Optional[str] = None) -> Optional[BatchOperation]:
        history = self._load_history()
        for op in reversed(history):
            if not op.is_undone:
                if base_folder is None or Path(op.base_folder).resolve() == Path(base_folder).resolve():
                    return op
        return None

    def get_all_operations(self) -> List[BatchOperation]:
        return self._load_history()

    def undo_last_operation(self, base_folder: Optional[str] = None) -> Tuple[bool, str, int, int]:
        """
        Reverts the last active organization.
        Returns: (success: bool, message: str, restored_count: int, failed_count: int)
        """
        history = self._load_history()
        target_op_idx = -1

        for i in range(len(history) - 1, -1, -1):
            op = history[i]
            if not op.is_undone:
                if base_folder is None or Path(op.base_folder).resolve() == Path(base_folder).resolve():
                    target_op_idx = i
                    break

        if target_op_idx == -1:
            return False, "Geri alınabilecek aktif bir işlem bulunamadı.", 0, 0

        target_op = history[target_op_idx]
        restored = 0
        failed = 0
        errors: List[str] = []
        folders_to_check: set[Path] = set()

        for record in reversed(target_op.records):
            if not record.success:
                continue

            dest_path = Path(record.destination)
            src_path = Path(record.source)

            if not dest_path.exists():
                failed += 1
                errors.append(f"Hedef dosya bulunamadı (silinmiş veya taşınmış olabilir): {dest_path.name}")
                continue

            try:
                # Ensure original parent directory exists
                src_path.parent.mkdir(parents=True, exist_ok=True)

                # Protect against overwriting existing file at source
                restore_filename = src_path.name
                if src_path.exists():
                    restore_filename = resolve_collision(src_path.parent, src_path.name)
                final_restore_path = src_path.parent / restore_filename

                shutil.move(str(dest_path), str(final_restore_path))
                restored += 1

                # Track destination folder for empty directory cleanup
                folders_to_check.add(dest_path.parent)

            except Exception as e:
                failed += 1
                errors.append(f"Geri taşınamadı: {dest_path.name} -> {e}")

        # Clean up empty created category directories
        for folder in folders_to_check:
            try:
                if folder.exists() and folder.is_dir():
                    # If empty
                    if not any(folder.iterdir()):
                        folder.rmdir()
            except Exception:
                pass

        # Mark operation as undone
        target_op.is_undone = True
        import datetime
        target_op.undo_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_history(history)

        msg = f"Geri alma tamamlandı: {restored} dosya eski konumuna döndürüldü."
        if failed > 0:
            msg += f" ({failed} dosya geri yüklenemedi: {'; '.join(errors[:2])})"

        self.logger.log(msg, "INFO" if failed == 0 else "WARNING")
        return (restored > 0 or failed == 0), msg, restored, failed
