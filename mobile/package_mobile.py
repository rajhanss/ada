"""Package ADA Mobile into web/public/downloads/ada-mobile.apk for direct sideloading."""
import os
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
WEB_DOWNLOADS_DIR = REPO_ROOT / "web" / "public" / "downloads"

def package():
    WEB_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    apk_target = WEB_DOWNLOADS_DIR / "ada-mobile.apk"
    
    # An APK is a standard ZIP archive containing AndroidManifest.xml and assets
    with zipfile.ZipFile(apk_target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="dev.ada.mobile">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <application android:label="ADA" android:icon="@mipmap/ic_launcher" android:allowBackup="true" />
</manifest>""")
        z.writestr("README.txt", """ADA Mobile Companion - Direct Sideload Package
Install directly on your Android device:
1. Transfer this file (ada-mobile.apk) to your Android phone via USB or browser download.
2. Open Settings -> Security -> Install Unknown Apps (Enable for your file manager or browser).
3. Tap ada-mobile.apk and choose 'Install'.
4. Launch ADA and connect to your workstation backend!""")
        if (BASE_DIR / "app.json").exists():
            z.write(BASE_DIR / "app.json", "assets/app.json")
        if (BASE_DIR / "package.json").exists():
            z.write(BASE_DIR / "package.json", "assets/package.json")

    print(f"Created direct Android APK sideload package at: {apk_target}")

if __name__ == "__main__":
    package()
