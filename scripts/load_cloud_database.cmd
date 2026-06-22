@echo off
setlocal EnableExtensions

REM Run this from the repository root.
REM This imports the NexCart Olist data into a cloud PostgreSQL database such as Neon.
REM Before running, set CLOUD_DB_URL using:
REM set "CLOUD_DB_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"

set DATA_DIR=dataset
if not exist "%DATA_DIR%\olist_customers_dataset.csv" (
    set DATA_DIR=data
)
if not exist "%DATA_DIR%\olist_customers_dataset.csv" (
    set DATA_DIR=dataset_olist
)

if "%CLOUD_DB_URL%"=="" (
    echo CLOUD_DB_URL is not set.
    echo Example:
    echo set "CLOUD_DB_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"
    exit /b 1
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
    echo Dataset files were not found.
    echo Put the seven Olist CSV files inside dataset, data, or dataset_olist.
    exit /b 1
)

echo Using dataset folder: %DATA_DIR%
echo Cleaning existing cloud tables if they exist...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "DROP TABLE IF EXISTS product_recommendation_scores CASCADE; DROP TABLE IF EXISTS order_reviews CASCADE; DROP TABLE IF EXISTS order_payments CASCADE; DROP TABLE IF EXISTS order_items CASCADE; DROP TABLE IF EXISTS orders CASCADE; DROP TABLE IF EXISTS products CASCADE; DROP TABLE IF EXISTS sellers CASCADE; DROP TABLE IF EXISTS customers CASCADE;"
if errorlevel 1 exit /b 1

echo Creating tables from schema/schema.sql...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -f schema/schema.sql
if errorlevel 1 exit /b 1

echo Importing customers...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy customers FROM '%DATA_DIR%/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing sellers...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy sellers FROM '%DATA_DIR%/olist_sellers_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing products...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy products FROM '%DATA_DIR%/olist_products_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing orders...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy orders FROM '%DATA_DIR%/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing order_items...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy order_items FROM '%DATA_DIR%/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing order_payments...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy order_payments FROM '%DATA_DIR%/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER true)"
if errorlevel 1 exit /b 1

echo Importing order_reviews with LATIN1 encoding...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -c "\copy order_reviews FROM '%DATA_DIR%/olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER true, ENCODING 'LATIN1')"
if errorlevel 1 exit /b 1

echo Running performance.sql to create indexes and stored procedure...
psql -v ON_ERROR_STOP=1 "%CLOUD_DB_URL%" -f queries/performance.sql
if errorlevel 1 exit /b 1

echo Verifying row counts...
psql "%CLOUD_DB_URL%" -c "SELECT 'customers' AS table_name, COUNT(*) FROM customers UNION ALL SELECT 'sellers', COUNT(*) FROM sellers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'order_items', COUNT(*) FROM order_items UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews;"

echo Cloud database load complete.
endlocal
