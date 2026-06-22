@echo off
setlocal

REM Run this from the repository root.
REM It creates a Python virtual environment, installs requirements, and creates .env for local PostgreSQL.

if "%PGPASSWORD%"=="" (
    set /p PGPASSWORD=Enter local PostgreSQL password for user postgres: 
)

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found in PATH. Please install Python or add it to PATH.
    exit /b 1
)

python -m venv .venv
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

(
    echo DB_HOST=localhost
    echo DB_PORT=5432
    echo DB_NAME=nexcart_olist
    echo DB_USER=postgres
    echo DB_PASSWORD=%PGPASSWORD%
    echo DB_SSLMODE=prefer
) > .env

echo Setup complete. The .env file was created locally and should not be committed.
endlocal
