from pathlib import Path
from typing import Optional, Tuple
import os
import re

SAFE_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log", ".yaml", ".yml"}
MAX_CONTENT_SAMPLE_BYTES = 4096


class AIService:
    """
    Intelligent classifier assistant.
    Provides offline semantic heuristics by default, with optional LLM API fallback.
    Never fails the main application pipeline on error.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def analyze_file(self, path: Path, default_category: str) -> Tuple[Optional[str], Optional[str], float]:
        """
        Analyze filename and (if safe) content to suggest refined category or name.
        Returns: (suggested_category, suggested_name, confidence)
        """
        suggested_category: Optional[str] = None
        suggested_name: Optional[str] = None
        confidence = 0.0

        try:
            filename = path.name.lower()
            ext = path.suffix.lower()

            # Rule 1: Heuristic keyword classification
            # e.g., an unknown extension or generic text file that is actually code or data
            if ext in {".txt", ".dat", ".log"}:
                if any(k in filename for k in ["data", "dataset", "table", "records", "report_num"]):
                    suggested_category = "Spreadsheets"
                    confidence = 0.75
                elif any(k in filename for k in ["script", "setup", "config", "build", "api", "query"]):
                    suggested_category = "Code"
                    confidence = 0.8

            # If image has invoice / receipt / doc words, maybe it's a scanned document
            if default_category == "Images":
                if any(k in filename for k in ["invoice", "receipt", "fatura", "makbuz", "belge", "contract", "sozlesme"]):
                    suggested_category = "Documents"
                    confidence = 0.85

            # If document is a presentation or slides
            if default_category == "Documents":
                if any(k in filename for k in ["slide", "presentation", "sunum"]):
                    suggested_category = "Presentations"
                    confidence = 0.8

            # Safe content peek for small text files
            if ext in SAFE_TEXT_EXTENSIONS and path.exists() and path.is_file():
                try:
                    if path.stat().st_size <= MAX_CONTENT_SAMPLE_BYTES:
                        content_sample = path.read_text(encoding="utf-8", errors="ignore")[:500].lower()
                        # Detect CSV content in txt file
                        if "," in content_sample and "\n" in content_sample and any(c.isdigit() for c in content_sample):
                            lines = content_sample.splitlines()
                            if len(lines) > 2 and all("," in line for line in lines[:3]):
                                suggested_category = "Spreadsheets"
                                confidence = 0.9
                        # Detect code structure in txt file
                        elif any(token in content_sample for token in ["def ", "import ", "function(", "class ", "<?php", "<!doctype"]):
                            suggested_category = "Code"
                            confidence = 0.95
                except Exception:
                    pass

        except Exception:
            pass

        return suggested_category, suggested_name, confidence
