@echo off
echo ============================================================
echo ADA Mobile - React Native Standalone APK Builder
echo ============================================================
echo.
echo Sideloading direct APK builds without Google Play Store limits.
echo.
cd /d %~dp0
call npx expo export --platform android
echo.
echo Standalone web/mobile export complete.
echo To generate a signed local APK without cloud EAS:
echo   npx expo prebuild --platform android
echo   cd android && gradlew assembleRelease
echo.
pause
