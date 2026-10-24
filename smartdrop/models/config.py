from dataclasses import dataclass, field, asdict
from typing import Dict, Any
import json
from pathlib import Path


LANGUAGE_CATEGORY_NAMES: Dict[str, Dict[str, str]] = {
    "tr": {
        "Documents": "Belgeler",
        "Images": "Resimler",
        "Videos": "Videolar",
        "Audio": "Müzikler",
        "Archives": "Arşivler",
        "Code": "Kodlar",
        "Spreadsheets": "Tablolar",
        "Presentations": "Sunumlar",
        "Installers": "Kurulumlar",
        "Fonts": "Yazı Tipleri",
        "Others": "Diğerleri"
    },
    "en": {
        "Documents": "Documents",
        "Images": "Images",
        "Videos": "Videos",
        "Audio": "Audio",
        "Archives": "Archives",
        "Code": "Code",
        "Spreadsheets": "Spreadsheets",
        "Presentations": "Presentations",
        "Installers": "Installers",
        "Fonts": "Fonts",
        "Others": "Others"
    },
    "de": {
        "Documents": "Dokumente",
        "Images": "Bilder",
        "Videos": "Videos",
        "Audio": "Audio",
        "Archives": "Archive",
        "Code": "Code",
        "Spreadsheets": "Tabellen",
        "Presentations": "Präsentationen",
        "Installers": "Installationsdateien",
        "Fonts": "Schriftarten",
        "Others": "Sonstiges"
    },
    "es": {
        "Documents": "Documentos",
        "Images": "Imágenes",
        "Videos": "Videos",
        "Audio": "Audio",
        "Archives": "Archivos",
        "Code": "Código",
        "Spreadsheets": "Hojas de Cálculo",
        "Presentations": "Presentaciones",
        "Installers": "Instaladores",
        "Fonts": "Fuentes",
        "Others": "Otros"
    }
}

DEFAULT_CATEGORY_FOLDERS: Dict[str, str] = dict(LANGUAGE_CATEGORY_NAMES["en"])


@dataclass
class SmartDropConfig:
    language: str = "en"
    include_subfolders: bool = False
    use_ai_classification: bool = False
    use_smart_rename: bool = False
    open_folder_after_organize: bool = False
    ignore_hidden_files: bool = True
    safe_overwrite_protection: bool = True
    theme: str = "dark"
    gemini_api_key: str = ""
    category_folders: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_CATEGORY_FOLDERS))

    def __post_init__(self):
        if not self.category_folders or self.category_folders == DEFAULT_CATEGORY_FOLDERS:
            lang_defaults = LANGUAGE_CATEGORY_NAMES.get(self.language, LANGUAGE_CATEGORY_NAMES["en"])
            self.category_folders = dict(lang_defaults)

    def get_category_folders(self) -> Dict[str, str]:
        lang_defaults = LANGUAGE_CATEGORY_NAMES.get(self.language, LANGUAGE_CATEGORY_NAMES["en"])
        res = dict(lang_defaults)
        if self.category_folders:
            res.update(self.category_folders)
        return res

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SmartDropConfig":
        lang = str(data.get("language", "en"))
        lang_defaults = LANGUAGE_CATEGORY_NAMES.get(lang, LANGUAGE_CATEGORY_NAMES["en"])
        category_folders = data.get("category_folders", dict(lang_defaults))
        merged_categories = dict(lang_defaults)
        merged_categories.update(category_folders)

        return cls(
            language=lang,
            include_subfolders=bool(data.get("include_subfolders", False)),
            use_ai_classification=bool(data.get("use_ai_classification", False)),
            use_smart_rename=bool(data.get("use_smart_rename", False)),
            open_folder_after_organize=bool(data.get("open_folder_after_organize", False)),
            ignore_hidden_files=bool(data.get("ignore_hidden_files", True)),
            safe_overwrite_protection=bool(data.get("safe_overwrite_protection", True)),
            theme=str(data.get("theme", "dark")),
            gemini_api_key=str(data.get("gemini_api_key", "")),
            category_folders=merged_categories
        )

    def save(self, config_path: Path) -> None:
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def load(cls, config_path: Path) -> "SmartDropConfig":
        if config_path.exists() and config_path.is_file():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls.from_dict(data)
            except Exception:
                pass
        return cls()
