# NexCart - E-commerce Recommendation System

**Course:** Z2004 Database Management Systems  
**Project Track:** Track B - AI Recommendation Engine  
**Database:** PostgreSQL  
**Repository:** https://github.com/Dexter087/Nexcart.git

## Team Members

1. Daksha Mothukuri - ZDA24B030
2. Manoj Phani Varma Vadapalli - ZDA24B040
3. V S S Preeti Ananya Yamali - ZDA24B002

## 1. Project Overview

NexCart is a relational e-commerce recommendation system built using PostgreSQL and a Python API. The system is based on the Olist Brazilian E-Commerce Public Dataset and stores customers, sellers, products, orders, order items, payments, and reviews in a normalized relational schema.

The main goal of the project is to recommend top-N products for a given customer using purchase history. The recommendation logic is implemented using SQL joins, CTEs, and window functions, while the Python API exposes the recommendation output through a simple endpoint.

## 2. Track B Requirement Mapping

| Track B Requirement | NexCart Implementation |
|---|---|
| Normalized PostgreSQL database with at least 5 tables | 7 core relational tables: customers, sellers, products, orders, order_items, order_payments, order_reviews |
| At least 2000 rows of transactional data | Olist dataset contains large-scale transactional e-commerce records |
| Collaborative filtering using SQL window functions | `queries/recommendation_queries.sql` and `app/recommender.py` use customer purchase overlap and ranking functions |
| Python API returning top-N recommendations | FastAPI app in `app/main.py` |
| Performance benchmark with and without indexes | `queries/performance.sql` contains before-index and after-index EXPLAIN ANALYZE blocks |
| Stored procedure or trigger updating recommendation scores | `refresh_product_recommendation_scores()` procedure in `queries/performance.sql` |

## 3. Repository Structure

```text
Nexcart/
├── README.md
├── requirements.txt
├── .env.example
├── schema/
│   ├── schema.sql
│   └── er_diagram.png
├── data/
│   └── README_DATA.md
├── queries/
│   ├── queries.sql
│   ├── performance.sql
│   └── recommendation_queries.sql
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── recommender.py
│   └── main.py
├── report/
│   ├── NexCart_Final_Report.docx
│   └── NexCart_Final_Report.pdf
└── demo/
    └── demo_script.txt
```

## 4. Dataset

The project uses the Olist Brazilian E-Commerce Public Dataset. The following CSV files are required:

1. `olist_customers_dataset.csv`
2. `olist_sellers_dataset.csv`
3. `olist_products_dataset.csv`
4. `olist_orders_dataset.csv`
5. `olist_order_items_dataset.csv`
6. `olist_order_payments_dataset.csv`
7. `olist_order_reviews_dataset.csv`

The geolocation file is not used in the final implementation. The category translation file is also not used because the final working schema stores `product_category_name` directly in the `products` table.

## 5. Final Working Tables

| Table | Purpose |
|---|---|
| `customers` | Stores customer identity and location fields |
| `sellers` | Stores marketplace seller details |
| `products` | Stores product details and category names |
| `orders` | Stores order-level transaction records |
| `order_items` | Links orders to products and sellers |
| `order_payments` | Stores payment method and payment value details |
| `order_reviews` | Stores review scores and review messages |
| `product_recommendation_scores` | Created by `performance.sql`; stores refreshed product-level recommendation scores |

## 6. Setup Instructions

### Step 1 - Create and activate a Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 2 - Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 - Create the PostgreSQL database

Open pgAdmin or psql and create the database:

```sql
CREATE DATABASE nexcart_olist;
```

### Step 4 - Run the schema

Run:

```sql
\i schema/schema.sql
```

If using pgAdmin, open `schema/schema.sql` in Query Tool and execute it inside the `nexcart_olist` database.

### Step 5 - Import the CSV files

Import the dataset files in this exact order:

1. `customers` <- `olist_customers_dataset.csv`
2. `sellers` <- `olist_sellers_dataset.csv`
3. `products` <- `olist_products_dataset.csv`
4. `orders` <- `olist_orders_dataset.csv`
5. `order_items` <- `olist_order_items_dataset.csv`
6. `order_payments` <- `olist_order_payments_dataset.csv`
7. `order_reviews` <- `olist_order_reviews_dataset.csv`

Use these import settings in pgAdmin:

```text
Format: CSV
Header: Yes
Delimiter: ,
Quote: "
Escape: "
Encoding: UTF8
```

### Step 6 - Verify row counts

```sql
SELECT 'customers' AS table_name, COUNT(*) FROM customers
UNION ALL SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews;
```

### Step 7 - Run analytical SQL queries

Run:

```sql
\i queries/queries.sql
```

In pgAdmin, open `queries/queries.sql` and execute the queries one by one.

### Step 8 - Run performance and recommendation score setup

Run:

```sql
\i queries/performance.sql
```

This script checks dataset size, runs EXPLAIN ANALYZE before indexing, creates indexes, runs EXPLAIN ANALYZE after indexing, creates the recommendation score table, and runs the stored procedure.

## 7. Python API Setup

### Step 1 - Create `.env`

Copy `.env.example` to `.env` and update your PostgreSQL password.

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nexcart_olist
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### Step 2 - Start the API

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Step 3 - Get recommendations

Use this endpoint:

```text
GET /recommendations/{customer_id}?top_n=5
```

Example:

```text
http://127.0.0.1:8000/recommendations/REPLACE_WITH_CUSTOMER_ID?top_n=5
```

You can also test from the command line:

```bash
python -m app.main --customer_id REPLACE_WITH_CUSTOMER_ID --top_n 5
```

## 8. Recommendation Logic

NexCart uses user-based collaborative filtering. The SQL first finds the selected customer's purchase history using `customer_unique_id`, then identifies other customers who overlap with the target customer by product or product category. Candidate products are taken from these similar customers but products already bought by the target customer are removed.

The final candidates are ranked using SQL window functions:

- `RANK()` ranks recommendation candidates by similarity weight and purchase frequency.
- `ROW_NUMBER() OVER (PARTITION BY product_category_name ...)` limits repeated recommendations from the same category.

If the selected customer does not have enough purchase history, the API falls back to globally popular products ranked by sales and revenue.

## 9. Performance Evidence

`queries/performance.sql` contains:

1. Dataset row-count checks
2. Before-index `EXPLAIN ANALYZE` tests
3. Index creation statements
4. After-index `EXPLAIN ANALYZE` tests
5. Stored procedure creation and execution
6. Top-N recommendation score query

Indexes used:

```sql
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp ON orders(order_purchase_timestamp);
```

These indexes were selected because the major queries repeatedly join and filter using `customer_id`, `order_id`, `product_id`, `seller_id`, and order purchase timestamps.

## 10. Stored Procedure

The stored procedure `refresh_product_recommendation_scores()` refreshes the `product_recommendation_scores` table using the latest records from `order_items`.

Run it using:

```sql
CALL refresh_product_recommendation_scores();
```

This procedure modifies data by truncating and repopulating the recommendation score table. It supports recommendation output by maintaining updated product-level popularity and revenue scores.

## 11. Demo Video Guide

The demo should show:

1. Repository structure
2. PostgreSQL tables and row counts
3. Analytical SQL query execution
4. Recommendation SQL query or API output
5. Performance SQL with before/after indexing
6. Stored procedure execution
7. Final report overview

A 5-minute speaking script is provided in `demo/demo_script.txt`.

## 12. AI Usage Disclosure

AI tools were used for brainstorming, debugging SQL/Python structure, drafting documentation, and improving wording in the README and report. All generated code and text were reviewed, edited, and adapted for the NexCart schema and PostgreSQL implementation before submission.

## 13. Limitations

The Olist dataset is historical and does not include live user browsing behavior, cart events, or product images. Therefore, the recommendation system uses transaction-based collaborative filtering rather than real-time behavioral personalization. Some customers have limited purchase history, so the API includes a popularity-based fallback.

## 14. Future Work

Future improvements can include product embeddings, category translation, inventory extensions, user browsing events, and a web frontend for interactive recommendations.
