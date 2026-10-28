@echo off
setlocal
set "PYIN_FORM_PYTHON=%~dp0.venv\Scripts\pythonw.exe"
if not exist "%PYIN_FORM_PYTHON%" (
    echo Project Python was not found. Create .venv and install requirements.txt first.
    pause
    exit /b 1
)
start "" "%PYIN_FORM_PYTHON%" "%~dp0pinyin_form.pyw"
