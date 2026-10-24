import re
from pathlib import Path
from typing import Optional


class SmartRenamer:
    """
    Optional intelligent file renamer that tidies up camera dumps,
    browser downloads with duplicate numbers like 'document(1).pdf',
    and illegal filesystem characters.
    Never alters extension and never overwrites.
    """

    ILLEGAL_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

    @classmethod
    def sanitize_name(cls, name: str) -> str:
        """Removes characters forbidden in Windows / NTFS filenames."""
        cleaned = cls.ILLEGAL_CHARS_PATTERN.sub("_", name)
        # Avoid ending with dot or space in Windows
        cleaned = cleaned.strip(". ")
        return cleaned or "unnamed_file"

    @classmethod
    def suggest_smart_name(cls, path: Path, category: str) -> Optional[str]:
        original_name = path.name
        stem = path.stem
        suffix = path.suffix

        new_stem = stem

        # Pattern 1: Browser duplicate downloads like "file (1)", "file(2)", "file (copy)"
        # e.g. "invoice(4)" -> "invoice_4"
        bracket_match = re.search(r'[\s_]*\(([0-9]+)\)$', new_stem)
        if bracket_match:
            idx = bracket_match.group(1)
            base = new_stem[:bracket_match.start()].strip()
            new_stem = f"{base}_{idx}"

        # Pattern 2: Generic camera timestamps:
        # IMG_20260920_1832 -> photo_20260920_1832
        # Screenshot_2026-09-20-18-32 -> screenshot_20260920_1832
        # VID_20260920_1832 -> video_20260920_1832
        img_match = re.match(r'^(IMG|DSC|PXL|PHOTO)[-_](\d{8})[-_](\d{4,6})', new_stem, re.IGNORECASE)
        if img_match:
            date_part = img_match.group(2)
            time_part = img_match.group(3)
            new_stem = f"photo_{date_part}_{time_part}"

        vid_match = re.match(r'^(VID|MOV|VIDEO)[-_](\d{8})[-_](\d{4,6})', new_stem, re.IGNORECASE)
        if vid_match:
            date_part = vid_match.group(2)
            time_part = vid_match.group(3)
            new_stem = f"video_{date_part}_{time_part}"

        screenshot_match = re.match(r'^(Screenshot|Screen_Shot|Ekran_Alintisi|Ekran_Görüntüsü)[-_](\d{4}[-_]?\d{2}[-_]?\d{2})', new_stem, re.IGNORECASE)
        if screenshot_match:
            date_part = screenshot_match.group(2).replace("-", "").replace("_", "")
            new_stem = f"screenshot_{date_part}"

        # Clean spaces to underscores if needed, or collapse multiple spaces
        new_stem = re.sub(r'\s+', '_', new_stem.strip())

        sanitized_stem = cls.sanitize_name(new_stem)
        candidate = f"{sanitized_stem}{suffix}"

        if candidate.lower() != original_name.lower():
            return candidate

        return None
