@echo off
setlocal

REM Run this from the repository root after scripts/setup_env.cmd and scripts/load_database.cmd.

if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found. Run scripts\setup_env.cmd first.
    exit /b 1
)

.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
endlocal
