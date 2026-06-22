@echo off
setlocal EnableExtensions

REM Generates one random valid customer_id for testing the recommendation page.

if "%PGPASSWORD%"=="" (
    set /p PGPASSWORD=Enter local PostgreSQL password for user postgres: 
)

where psql >nul 2>&1
if errorlevel 1 (
    set "PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin"
)

psql -U postgres -h localhost -p 5432 -d nexcart_olist -At -c "SELECT c.customer_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing') GROUP BY c.customer_id ORDER BY RANDOM() LIMIT 1;"
endlocal
