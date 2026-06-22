@echo off
setlocal

REM Optional FastAPI interface for Track B Python API evidence.

if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found. Run scripts\setup_env.cmd first.
    exit /b 1
)

.venv\Scripts\python.exe -m uvicorn app.main:app --reload
endlocal
