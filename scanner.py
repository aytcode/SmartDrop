from pathlib import Path
from typing import List, Callable, Optional
from smartdrop.models.config import SmartDropConfig
from smartdrop.models.file_item import FileItem
from smartdrop.core.classifier import FileClassifier
from smartdrop.core.renamer import SmartRenamer
from smartdrop.services.ai_service import AIService
from smartdrop.utils.file_utils import is_hidden_file, get_file_timestamps
from smartdrop.core.safety import SafetyGuard


class FolderScanner:
    """
    Scans directories, extracts comprehensive metadata, applies categorizations,
    and constructs the reorganization preview plan.
    """

    def __init__(self, config: Optional[SmartDropConfig] = None):
        self.config = config or SmartDropConfig()
        self.classifier = FileClassifier(self.config.category_folders, language=self.config.language)
        self.ai_service = AIService(self.config.gemini_api_key) if self.config.use_ai_classification else None

    def scan(
        self,
        folder_path: Path,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[FileItem]:
        """
        Scans folder_path and returns list of FileItems with preview locations.
        """
        valid, reason = SafetyGuard.validate_target_directory(folder_path)
        if not valid:
            raise ValueError(reason)

        folder_path = folder_path.resolve()
        candidate_paths: List[Path] = []

        # Category folder names to exclude from source scan if they match organized dirs
        category_dirs = {
            self.classifier.get_target_folder_name(cat).lower()
            for cat in FileClassifier.get_all_categories()
        }

        # Step 1: Collect files
        try:
            if self.config.include_subfolders:
                for p in folder_path.rglob("*"):
                    if p.is_file():
                        candidate_paths.append(p)
            else:
                for p in folder_path.iterdir():
                    if p.is_file():
                        candidate_paths.append(p)
        except Exception as e:
            raise RuntimeError(f"Klasör taranırken erişim hatası: {e}")

        total_files = len(candidate_paths)
        file_items: List[FileItem] = []

        for index, file_path in enumerate(candidate_paths):
            if progress_callback:
                progress_callback(index + 1, total_files, file_path.name)

            # Skip hidden files if configured
            if self.config.ignore_hidden_files and is_hidden_file(file_path):
                continue

            # Don't touch SmartDrop history or lock files
            if file_path.name in (".smartdrop_history.json", ".smartdrop_config.json"):
                continue

            created_at, modified_at, size_bytes = get_file_timestamps(file_path)
            ext = file_path.suffix.lower()

            # Primary classification
            category = self.classifier.classify(file_path)

            # Optional AI enhancement
            ai_category = None
            ai_name = None
            ai_conf = 0.0
            if self.config.use_ai_classification and self.ai_service:
                ai_category, ai_name, ai_conf = self.ai_service.analyze_file(file_path, category)
                if ai_category and ai_conf >= 0.75:
                    category = ai_category

            target_folder_name = self.classifier.get_target_folder_name(category)
            target_dir = folder_path / target_folder_name

            # Smart renaming
            new_name = file_path.name
            is_renamed = False
            if self.config.use_smart_rename:
                smart_name = SmartRenamer.suggest_smart_name(file_path, category)
                if smart_name and smart_name != file_path.name:
                    new_name = smart_name
                    is_renamed = True

            new_path = target_dir / new_name

            # Check if file is already organized in target directory with matching name
            is_skipped = False
            skip_reason = ""
            if file_path.parent == target_dir and new_name == file_path.name:
                is_skipped = True
                skip_reason = "Zaten hedef klasörde"

            item = FileItem(
                path=file_path,
                original_name=file_path.name,
                original_dir=file_path.parent,
                extension=ext,
                size_bytes=size_bytes,
                created_at=created_at,
                modified_at=modified_at,
                category=category,
                target_folder_name=target_folder_name,
                target_dir=target_dir,
                new_name=new_name,
                new_path=new_path,
                is_selected=not is_skipped,
                is_renamed=is_renamed,
                is_skipped=is_skipped,
                skip_reason=skip_reason,
                ai_suggested_category=ai_category,
                ai_suggested_name=ai_name,
                ai_confidence=ai_conf
            )
            file_items.append(item)

        return file_items
