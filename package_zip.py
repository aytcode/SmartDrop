import zipfile
import os
from pathlib import Path

def create_bundle(output_zip: str = "SmartDrop-Windows.zip"):
    files_to_zip = [
        "app.py",
        "setup.bat",
        "run.bat",
        "requirements.txt",
        "README.md",
        "pytest.ini",
        ".env.example"
    ]

    dirs_to_zip = [
        "smartdrop",
        "tests",
        "tools"
    ]

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files_to_zip:
            if os.path.exists(f):
                z.write(f, arcname=f)

        for d in dirs_to_zip:
            for root, dirs, files in os.walk(d):
                if "__pycache__" in root or ".pytest_cache" in root or ".git" in root:
                    continue
                for file in files:
                    filepath = os.path.join(root, file)
                    z.write(filepath, arcname=filepath)

    print("ZIP_OK")

if __name__ == "__main__":
    create_bundle()
