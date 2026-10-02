from pathlib import Path
import shutil
from typing import List, Callable, Optional, Dict, Any
from smartdrop.models.file_item import FileItem
from smartdrop.models.operation import BatchOperation, FileMoveRecord
from smartdrop.core.undo_manager import UndoManager
from smartdrop.utils.file_utils import resolve_collision
from smartdrop.core.safety import SafetyGuard
from smartdrop.services.logger_service import AppLogger


class FileOrganizer:
    """
    Executes previewed file operations safely, with guaranteed non-destructive moves,
    collision resolution, granular error tolerance, and full transaction logging.
    """

    def __init__(self, undo_manager: Optional[UndoManager] = None):
        self.undo_manager = undo_manager or UndoManager()
        self.logger = AppLogger.get_instance()

    def organize(
        self,
        base_folder: Path,
        items: List[FileItem],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Organizes selected items.
        Returns a summary dictionary with counts and error details.
        """
        selected_items = [it for it in items if it.is_selected and not it.is_skipped]
        total_count = len(selected_items)

        batch_op = BatchOperation(
            base_folder=str(base_folder.resolve()),
            total_files=total_count
        )

        successful_moves = 0
        failed_moves = 0
        errors: List[str] = []

        self.logger.log(f"Dosya düzenleme başlatıldı: {total_count} dosya işlenecek.")

        for index, item in enumerate(selected_items):
            if progress_callback:
                progress_callback(index + 1, total_count, item.original_name)

            source_path = item.path

            # Guard 1: verify source exists
            if not source_path.exists():
                failed_moves += 1
                err = f"Kaynak dosya bulunamadı: {item.original_name}"
                errors.append(err)
                batch_op.records.append(FileMoveRecord(
                    source=str(source_path),
                    destination="",
                    original_name=item.original_name,
                    new_name=item.new_name,
                    category=item.category,
                    size_bytes=item.size_bytes,
                    success=False,
                    error=err
                ))
                continue

            # Ensure destination directory exists
            try:
                item.target_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                failed_moves += 1
                err = f"Hedef klasör oluşturulamadı: {item.target_dir.name} ({e})"
                errors.append(err)
                batch_op.records.append(FileMoveRecord(
                    source=str(source_path),
                    destination=str(item.target_dir),
                    original_name=item.original_name,
                    new_name=item.new_name,
                    category=item.category,
                    size_bytes=item.size_bytes,
                    success=False,
                    error=err
                ))
                continue

            # Guard 2: resolve collisions to guarantee zero overwrite
            destination_filename = item.new_name
            target_path = item.target_dir / destination_filename

            # If target exists and is not the exact same file
            if target_path.exists():
                try:
                    if target_path.resolve() != source_path.resolve():
                        destination_filename = resolve_collision(item.target_dir, destination_filename)
                        target_path = item.target_dir / destination_filename
                except Exception:
                    destination_filename = resolve_collision(item.target_dir, destination_filename)
                    target_path = item.target_dir / destination_filename

            # Validate move safety
            is_valid, reason = SafetyGuard.validate_move(source_path, target_path)
            if not is_valid:
                failed_moves += 1
                errors.append(f"{item.original_name}: {reason}")
                batch_op.records.append(FileMoveRecord(
                    source=str(source_path),
                    destination=str(target_path),
                    original_name=item.original_name,
                    new_name=destination_filename,
                    category=item.category,
                    size_bytes=item.size_bytes,
                    success=False,
                    error=reason
                ))
                continue

            # Perform the move
            try:
                # If target is identical path (no-op), skip moving
                if source_path.resolve() == target_path.resolve():
                    continue

                shutil.move(str(source_path), str(target_path))
                successful_moves += 1

                batch_op.records.append(FileMoveRecord(
                    source=str(source_path),
                    destination=str(target_path),
                    original_name=item.original_name,
                    new_name=destination_filename,
                    category=item.category,
                    size_bytes=item.size_bytes,
                    success=True
                ))

            except Exception as e:
                failed_moves += 1
                err = f"{item.original_name} taşınamadı: {e}"
                errors.append(err)
                batch_op.records.append(FileMoveRecord(
                    source=str(source_path),
                    destination=str(target_path),
                    original_name=item.original_name,
                    new_name=destination_filename,
                    category=item.category,
                    size_bytes=item.size_bytes,
                    success=False,
                    error=str(e)
                ))

        batch_op.successful_moves = successful_moves
        batch_op.failed_moves = failed_moves

        # Persist to undo manager if any moves were made
        if successful_moves > 0:
            self.undo_manager.record_operation(batch_op)

        summary_msg = f"{total_count} dosya işlendi. {successful_moves} başarılı, {failed_moves} başarısız."
        self.logger.log(summary_msg, "INFO" if failed_moves == 0 else "WARNING")

        return {
            "batch_id": batch_op.id,
            "total_files": total_count,
            "successful_moves": successful_moves,
            "failed_moves": failed_moves,
            "errors": errors,
            "message": summary_msg
        }
