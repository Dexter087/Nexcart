# NexCart - E-commerce Recommendation System

**Course:** Z2004 Database Management Systems  
**Track:** Track B - AI Recommendation Engine  
**Database:** PostgreSQL  
**Application:** Local Streamlit dashboard + optional FastAPI endpoint  
**Repository:** https://github.com/Dexter087/Nexcart.git

## Team Members

1. Daksha Mothukuri - ZDA24B030
2. Manoj Phani Varma Vadapalli - ZDA24B040
3. V S S Preeti Ananya Yamali - ZDA24B002

---

## 1. Project Overview

NexCart is a PostgreSQL-backed e-commerce recommendation system based on the Olist marketplace dataset. The database stores customers, sellers, products, orders, order items, payments, and reviews in a normalized relational schema. The application recommends products for a selected customer using SQL-based collaborative filtering.

The final app runs locally using Streamlit and connects to a local PostgreSQL database through `.env` variables.

---

## 2. Requirement Mapping

| Track B Requirement | NexCart Implementation |
|---|---|
| Normalized database with at least 5 tables | 7 core PostgreSQL tables |
| At least 2000 rows of transactional data | Olist dataset with 112,650 order item rows |
| Collaborative filtering using SQL window functions | Implemented in `queries/recommendation_queries.sql` and `app/recommender.py` |
| Python API returning top-N recommendations | `app/main.py` FastAPI endpoint and CLI |
| App/demo interface | `app/streamlit_app.py` Streamlit dashboard |
| Performance benchmark with and without indexes | `queries/performance.sql` and `report/performance_output.txt` |
| Stored procedure or trigger | `refresh_product_recommendation_scores()` in `queries/performance.sql` |

---

## 3. Repository Structure

```text
Nexcart/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── schema/
│   ├── schema.sql
│   └── er_diagram.png
├── dataset/
│   ├── README_DATA.md
│   ├── olist_customers_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   └── olist_order_reviews_dataset.csv
├── queries/
│   ├── queries.sql
│   ├── performance.sql
│   └── recommendation_queries.sql
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── analytics.py
│   ├── recommender.py
│   ├── main.py
│   └── streamlit_app.py
├── scripts/
│   ├── setup_env.cmd
│   ├── load_database.cmd
│   ├── run_app.cmd
│   └── run_api.cmd
├── report/
│   ├── Report.pdf
│   ├── Report.docx
│   └── performance_output.txt
└── demo/
    └── demo_video_link.txt
```

---

## 4. Dataset Files Required

Place the following files inside `dataset/`:

```text
olist_customers_dataset.csv
olist_sellers_dataset.csv
olist_products_dataset.csv
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
```

The geolocation and category translation files are not required for the final implementation.

---

## 5. Full Setup Using Command Prompt

Run all commands from the repository root. Example:

```cmd
cd /d C:\Users\Daksh\Downloads\Nexcart
```

### Step 1 - Set PostgreSQL password for this Command Prompt session

Replace the password value with your local PostgreSQL password.

```cmd
set PGPASSWORD=PUT_YOUR_POSTGRES_PASSWORD_HERE
```

### Step 2 - Check that PostgreSQL command-line tools are available

```cmd
psql --version
```

If `psql` is not recognized, run:

```cmd
set PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin
psql --version
```

### Step 3 - Create Python environment and `.env`

```cmd
scripts\setup_env.cmd
```

This creates `.venv`, installs Python packages, and writes a local `.env` file. Do not commit `.env`.

### Step 4 - Load the database from scratch

```cmd
scripts\load_database.cmd
```

This command does all of the following:

1. drops any old `nexcart_olist` database,
2. creates a fresh `nexcart_olist` database,
3. runs `schema/schema.sql`,
4. imports the seven CSV files from `dataset/`,
5. verifies row counts,
6. runs `queries/performance.sql`,
7. saves performance evidence to `report/performance_output.txt`.

### Step 5 - Start the Streamlit app

```cmd
scripts\run_app.cmd
```

Then open:

```text
http://localhost:8501
```

---

## 6. Manual Database Loading Commands

If you do not want to use `scripts/load_database.cmd`, run these commands manually from the repository root.

```cmd
set PGPASSWORD=PUT_YOUR_POSTGRES_PASSWORD_HERE
set PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin
```

```cmd
psql -U postgres -h localhost -p 5432 -d postgres -c "DROP DATABASE IF EXISTS nexcart_olist WITH (FORCE);"
psql -U postgres -h localhost -p 5432 -d postgres -c "CREATE DATABASE nexcart_olist;"
```

```cmd
psql -U postgres -h localhost -p 5432 -d nexcart_olist -f schema/schema.sql
```

```cmd
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy customers FROM 'dataset/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true)"
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy sellers FROM 'dataset/olist_sellers_dataset.csv' WITH (FORMAT csv, HEADER true)"
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy products FROM 'dataset/olist_products_dataset.csv' WITH (FORMAT csv, HEADER true)"
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy orders FROM 'dataset/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true)"
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy order_items FROM 'dataset/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER true)"
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy order_payments FROM 'dataset/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER true)"
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "\copy order_reviews FROM 'dataset/olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER true, ENCODING 'LATIN1')"
```

Verify row counts:

```cmd
psql -U postgres -h localhost -p 5432 -d nexcart_olist -c "SELECT 'customers' AS table_name, COUNT(*) FROM customers UNION ALL SELECT 'sellers', COUNT(*) FROM sellers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'order_items', COUNT(*) FROM order_items UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews;"
```

Run SQL files:

```cmd
psql -U postgres -h localhost -p 5432 -d nexcart_olist -f queries/queries.sql
psql -U postgres -h localhost -p 5432 -d nexcart_olist -f queries/recommendation_queries.sql
psql -U postgres -h localhost -p 5432 -d nexcart_olist -f queries/performance.sql > report\performance_output.txt 2>&1
```

---


## 7. Generate a Random Customer ID for Testing

During the demo, use a random valid customer ID to show that the recommendation output is generated from the database and is not fixed.

For Windows Command Prompt, run this from the repository root:

```cmd
set PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin
psql -U postgres -h localhost -p 5432 -d nexcart_olist -At -c "SELECT c.customer_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing') GROUP BY c.customer_id ORDER BY RANDOM() LIMIT 1;"
```

Copy the generated `customer_id`, paste it into the **Recommendation Engine** section of the Streamlit app, and click **Generate Recommendations**.

Run the same command again to get a different customer ID and show that the recommendations change.

## 8. Optional FastAPI Interface

The Streamlit app is the main demo interface. The FastAPI endpoint is included as explicit Python API evidence.

Start the API:

```cmd
scripts\run_api.cmd
```

Open:

```text
http://127.0.0.1:8000/docs
```

Endpoint:

```text
GET /recommendations/{customer_id}?top_n=5
```

CLI test:

```cmd
.venv\Scripts\python.exe -m app.main --customer_id REPLACE_WITH_CUSTOMER_ID --top_n 5
```

---

## 9. Application Features

The Streamlit app contains:

1. Home / project overview
2. Database summary and table row counts
3. Customer-based product recommendations
4. SQL analytics charts
5. Performance benchmark summary
6. Stored procedure demo for refreshing recommendation scores

---

## 10. Recommendation Logic

NexCart uses user-based collaborative filtering. The target customer is mapped to `customer_unique_id`, then the system finds products and product categories previously purchased by that customer. It searches for similar customers who bought overlapping products or categories, collects candidate products bought by those similar customers, removes products already purchased by the target customer, and ranks the remaining products.

The main SQL logic uses:

```sql
SUM(...) OVER (PARTITION BY ...)
RANK() OVER (...)
ROW_NUMBER() OVER (PARTITION BY ...)
```

These are present in `queries/recommendation_queries.sql` and in the SQL query inside `app/recommender.py`.

---

## 11. Performance Evidence

The performance script creates these indexes:

```sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp ON orders(order_purchase_timestamp);
```

The local benchmark produced these results:

| Query | Before Index | After Index | Result |
|---|---:|---:|---|
| Customer order history | 6.521 ms | 0.162 ms | improved about 40.3x |
| Top-selling products | 477.947 ms | 305.587 ms | improved about 1.56x |
| Seller revenue ranking | 69.428 ms | 99.546 ms | slower in this run because the query aggregates almost all rows |
| Precomputed recommendation scores | - | 42.359 ms | stored score table output |

The full captured output is stored in `report/performance_output.txt`.

---

## 12. Stored Procedure

`queries/performance.sql` creates and runs:

```sql
CALL refresh_product_recommendation_scores();
```

This procedure refreshes `product_recommendation_scores` using current order item data. In the captured run, it generated scores for 32,951 products, counted 112,650 units, and produced total counted revenue of 13,591,643.70.

---

## 13. AI Usage Disclosure

AI tools were used for brainstorming, debugging, code structuring, README drafting, and report writing support. The project files were reviewed and adapted for the NexCart schema, local PostgreSQL setup, Olist dataset structure, and final DBMS project requirements before submission.

---


---

## Local Demo / Deployment Note

This version is designed for a local DBMS demo. The app connects to the local PostgreSQL database `nexcart_olist`, so it should be run with:

```cmd
scripts\run_app.cmd
```

Then open:

```text
http://localhost:8501
```

The Streamlit Cloud **Deploy** button should not be used unless the PostgreSQL database is also moved to a cloud database service, because Streamlit Cloud cannot connect to `localhost` on the laptop.

## 14. No Secrets Policy

No passwords or API keys should be committed. Local database credentials must stay in `.env`, which is excluded by `.gitignore`. Use `.env.example` only as a template.
