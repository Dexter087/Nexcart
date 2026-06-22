@echo off
setlocal EnableExtensions

REM Run this from the repository root.
REM This script recreates the local PostgreSQL database and imports the Olist CSV files.

set DB_NAME=nexcart_olist
set DB_USER=postgres
set DB_HOST=localhost
set DB_PORT=5432
set DATA_DIR=dataset_olist

if "%PGPASSWORD%"=="" (
    set /p PGPASSWORD=Enter PostgreSQL password for user postgres: 
)

where psql >nul 2>&1
if errorlevel 1 (
    set "PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin"
)

where psql >nul 2>&1
if errorlevel 1 (
    echo psql was not found. Add PostgreSQL bin folder to PATH and try again.
    exit /b 1
)

if not exist "%DATA_DIR%\olist_customers_dataset.csv" (
    echo Dataset files were not found in %DATA_DIR%.
    echo Make sure the seven Olist CSV files are inside the dataset_olist folder.
    exit /b 1
)

if not exist report mkdir report

echo Recreating database %DB_NAME%...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d postgres -c "DROP DATABASE IF EXISTS %DB_NAME% WITH (FORCE);"
if errorlevel 1 exit /b 1

psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d postgres -c "CREATE DATABASE %DB_NAME%;"
if errorlevel 1 exit /b 1

echo Creating tables from schema/schema.sql...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f schema/schema.sql
if errorlevel 1 exit /b 1

echo Importing customers...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy customers FROM '%DATA_DIR%/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing sellers...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy sellers FROM '%DATA_DIR%/olist_sellers_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing products...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy products FROM '%DATA_DIR%/olist_products_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing orders...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy orders FROM '%DATA_DIR%/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing order_items...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy order_items FROM '%DATA_DIR%/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing order_payments...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy order_payments FROM '%DATA_DIR%/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing order_reviews with LATIN1 encoding...
psql -v ON_ERROR_STOP=1 -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "\copy order_reviews FROM '%DATA_DIR%/olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER true, ENCODING 'LATIN1')"
if errorlevel 1 exit /b 1

echo Verifying row counts...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -c "SELECT 'customers' AS table_name, COUNT(*) FROM customers UNION ALL SELECT 'sellers', COUNT(*) FROM sellers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'order_items', COUNT(*) FROM order_items UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews;"

echo Running performance script and saving report\performance_output.txt...
psql -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d %DB_NAME% -f queries/performance.sql > report\performance_output.txt 2>&1
if errorlevel 1 exit /b 1

echo Database load complete.
echo Run scripts\run_app.cmd to start the Streamlit application.
endlocal
