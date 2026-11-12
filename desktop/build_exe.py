"""Script to package ADA Desktop Companion into a standalone Windows .exe using PyInstaller."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
WEB_DOWNLOADS_DIR = REPO_ROOT / "web" / "public" / "downloads"

def build():
    print("Building ADA Windows Standalone Executable...")
    os.chdir(BASE_DIR)

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",  # onedir is faster and more reliable for large Qt libraries, or onefile
        "--windowed",
        "--name=ADA-Desktop",
        f"--paths={BASE_DIR}",
        "--hidden-import=pydantic",
        "--hidden-import=pydantic_settings",
        "--hidden-import=mss",
        "--hidden-import=PIL",
        "--hidden-import=structlog",
        "--hidden-import=httpx",
        "--hidden-import=websockets",
        "--hidden-import=ada_desktop",
        str(BASE_DIR / "ada_desktop" / "main.py"),
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Build failed with code {result.returncode}")
        sys.exit(result.returncode)

    print("PyInstaller build complete!")

    # Ensure web/public/downloads exists
    WEB_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Create a zip archive of the onedir build for portable distribution, and copy to web/public/downloads
    dist_output = DIST_DIR / "ADA-Desktop"
    if dist_output.exists():
        archive_name = WEB_DOWNLOADS_DIR / "ada-desktop-windows-x64"
        print(f"Creating distribution zip at {archive_name}.zip ...")
        shutil.make_archive(str(archive_name), 'zip', dist_output)
        
        # Also copy the primary exe as ada-desktop-setup.exe for quick link
        main_exe = dist_output / "ADA-Desktop.exe"
        if main_exe.exists():
            target_exe = WEB_DOWNLOADS_DIR / "ada-desktop-setup.exe"
            shutil.copy2(main_exe, target_exe)
            print(f"Copied {main_exe} -> {target_exe}")

    print("Desktop build and packaging completed successfully!")

if __name__ == "__main__":
    build()
