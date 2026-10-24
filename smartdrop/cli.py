import argparse
import json
import sys
from pathlib import Path

# Ensure root is on path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from smartdrop.core.scanner import FolderScanner
from smartdrop.core.organizer import FileOrganizer
from smartdrop.core.undo_manager import UndoManager
from smartdrop.models.config import SmartDropConfig, LANGUAGE_CATEGORY_NAMES
from smartdrop.utils.test_helper import create_sample_test_folder


def handle_scan(args):
    target = Path(args.folder).resolve()
    lang = getattr(args, "lang", "tr") or "tr"
    config = SmartDropConfig(
        language=lang,
        include_subfolders=args.subfolders,
        use_ai_classification=args.ai,
        use_smart_rename=args.rename
    )
    scanner = FolderScanner(config)
    try:
        items = scanner.scan(target)
        output = [it.to_dict() for it in items]
        print(json.dumps({"status": "success", "count": len(items), "items": output}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        sys.exit(1)


def handle_organize(args):
    target = Path(args.folder).resolve()
    lang = getattr(args, "lang", "tr") or "tr"
    config = SmartDropConfig(
        language=lang,
        include_subfolders=args.subfolders,
        use_ai_classification=args.ai,
        use_smart_rename=args.rename
    )
    scanner = FolderScanner(config)
    try:
        items = scanner.scan(target)
        # If payload JSON provided with selections
        if args.selected_files:
            try:
                selected_names = set(json.loads(args.selected_files))
                for it in items:
                    it.is_selected = it.original_name in selected_names
            except Exception:
                pass

        organizer = FileOrganizer()
        result = organizer.organize(target, items)
        print(json.dumps({"status": "success", "result": result}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        sys.exit(1)


def handle_undo(args):
    undo_mgr = UndoManager()
    success, message, restored, failed = undo_mgr.undo_last_operation(args.folder)
    print(json.dumps({
        "status": "success" if success else "warning",
        "message": message,
        "restored": restored,
        "failed": failed
    }, ensure_ascii=False))


def handle_create_test(args):
    target = Path(args.folder).resolve()
    created = create_sample_test_folder(target)
    print(json.dumps({
        "status": "success",
        "folder": str(target),
        "created_files": [p.name for p in created]
    }, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="SmartDrop CLI")
    subparsers = parser.add_subparsers(dest="command")

    # scan
    p_scan = subparsers.add_parser("scan")
    p_scan.add_argument("folder")
    p_scan.add_argument("--subfolders", action="store_true")
    p_scan.add_argument("--ai", action="store_true")
    p_scan.add_argument("--rename", action="store_true")
    p_scan.add_argument("--lang", default="tr", choices=["tr", "en", "de", "es"])

    # organize
    p_org = subparsers.add_parser("organize")
    p_org.add_argument("folder")
    p_org.add_argument("--subfolders", action="store_true")
    p_org.add_argument("--ai", action="store_true")
    p_org.add_argument("--rename", action="store_true")
    p_org.add_argument("--lang", default="tr", choices=["tr", "en", "de", "es"])
    p_org.add_argument("--selected-files", help="JSON array of selected file names")

    # undo
    p_undo = subparsers.add_parser("undo")
    p_undo.add_argument("--folder", default=None)

    # create-test
    p_test = subparsers.add_parser("create-test")
    p_test.add_argument("--folder", default="test_data/sample_downloads")

    args = parser.parse_args()

    if args.command == "scan":
        handle_scan(args)
    elif args.command == "organize":
        handle_organize(args)
    elif args.command == "undo":
        handle_undo(args)
    elif args.command == "create-test":
        handle_create_test(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
