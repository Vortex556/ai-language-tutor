@echo off
chcp 65001 >nul 2>&1
set "PYTHONIOENCODING=utf-8"
echo.
echo ============================================================
echo    Markdown -^> Word
echo ============================================================
echo.
python "%~dp0convert_to_word.py" "%~1"
echo.
if errorlevel 1 pause
