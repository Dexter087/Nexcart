# NexCart - E-commerce Recommendation System

**Course:** Z2004 Database Management Systems  
**Track:** Track B - AI Recommendation Engine  
**Database:** PostgreSQL  
**Application:** Streamlit dashboard + optional FastAPI endpoint  
**Repository:** https://github.com/Dexter087/Nexcart.git

## Team Members

1. Daksha Mothukuri - ZDA24B030
2. Manoj Phani Varma Vadapalli - ZDA24B040
3. V S S Preeti Ananya Yamali - ZDA24B002

---

## 1. Project Overview

NexCart is a PostgreSQL-backed e-commerce recommendation system based on the Olist marketplace dataset. The database stores customers, sellers, products, orders, order items, payments, and reviews in a normalized relational schema. The application recommends products for a selected customer using SQL-based collaborative filtering.

The app can run in two modes:

1. **Local mode:** Streamlit connects to PostgreSQL running on the laptop.
2. **Deployment mode:** Streamlit Community Cloud connects to a cloud PostgreSQL database such as Neon.

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
│   ├── display.py
│   ├── recommender.py
│   ├── main.py
│   └── streamlit_app.py
├── scripts/
│   ├── setup_env.cmd
│   ├── load_database.cmd
│   ├── load_cloud_database.cmd
│   ├── get_random_customer_id.cmd
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

## 5. Local Setup Using Command Prompt

Run all commands from the repository root:

```cmd
cd /d C:\Users\Daksh\Downloads\Nexcart
```

### Step 1 - Set PostgreSQL password for this Command Prompt session

```cmd
set PGPASSWORD=PUT_YOUR_POSTGRES_PASSWORD_HERE
```

### Step 2 - Make sure `psql` is available

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

### Step 4 - Load the local PostgreSQL database

```cmd
scripts\load_database.cmd
```

This command drops and recreates `nexcart_olist`, runs the schema, imports the seven CSV files from `dataset/`, verifies row counts, and runs `queries/performance.sql`.

### Step 5 - Start the Streamlit app locally

```cmd
scripts\run_app.cmd
```

Open:

```text
http://localhost:8501
```

---

## 6. Generate a Random Customer ID for Testing

Use this during the demo to prove that the output is not fixed.

```cmd
scripts\get_random_customer_id.cmd
```

Or run the SQL manually:

```cmd
psql -U postgres -h localhost -p 5432 -d nexcart_olist -At -c "SELECT c.customer_id FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing') GROUP BY c.customer_id ORDER BY RANDOM() LIMIT 1;"
```

Copy the generated `customer_id`, paste it into the **Recommendation Engine** section of the Streamlit app, and click **Generate Recommendations**.

---

## 7. Deployment Overview

For a public Streamlit deployment, the app cannot use `localhost` because the deployed app runs on Streamlit's servers, not on your laptop. The deployment version should use:

```text
GitHub repo + Streamlit Community Cloud + cloud PostgreSQL database
```

Recommended database option:

```text
Neon PostgreSQL
```

---

## 8. Load the Database into Neon / Cloud PostgreSQL

Create a Neon PostgreSQL database and copy its connection string. It usually looks like this:

```text
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

From Command Prompt, run:

```cmd
cd /d C:\Users\Daksh\Downloads\Nexcart
set PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin
set "CLOUD_DB_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"
scripts\load_cloud_database.cmd
```

This script will:

1. clean existing NexCart tables in the cloud database,
2. run `schema/schema.sql`,
3. import the seven Olist CSV files from `dataset/`,
4. run `queries/performance.sql`,
5. verify row counts.

---

## 9. Streamlit Community Cloud Deployment Steps

After pushing the latest code to GitHub:

1. Open Streamlit Community Cloud.
2. Click **Create app**.
3. Select the GitHub repository:

```text
Dexter087/Nexcart
```

4. Select branch:

```text
main
```

5. Set main file path:

```text
app/streamlit_app.py
```

6. Open the app's **Secrets** settings and paste the cloud PostgreSQL credentials:

```toml
DB_HOST = "YOUR_NEON_HOST"
DB_PORT = "5432"
DB_NAME = "YOUR_DATABASE_NAME"
DB_USER = "YOUR_DATABASE_USER"
DB_PASSWORD = "YOUR_DATABASE_PASSWORD"
DB_SSLMODE = "require"
```

Alternative full-URL secret:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"
```

Do not commit real credentials to GitHub. Keep `.env` and `.streamlit/secrets.toml` ignored.

---

## 10. Optional FastAPI Interface

The Streamlit app is the main demo interface. The FastAPI endpoint is included as explicit Python API evidence.

Start the API locally:

```cmd
scripts\run_api.cmd
```

Example endpoint:

```text
http://127.0.0.1:8000/recommendations/{customer_id}?top_n=5
```

---

## 11. Important SQL Files

| File | Purpose |
|---|---|
| `schema/schema.sql` | Creates the normalized PostgreSQL schema |
| `queries/queries.sql` | Contains aggregation, join, subquery, CTE, and window-function queries |
| `queries/recommendation_queries.sql` | Standalone collaborative-filtering recommendation SQL |
| `queries/performance.sql` | Index benchmarks and stored procedure for recommendation scores |

---

## 12. AI Usage Disclosure

AI tools were used for brainstorming, debugging SQL/Python structure, improving documentation, and polishing report wording. All generated content was reviewed, edited, and adapted to the NexCart schema, PostgreSQL implementation, and project requirements before submission.

---

## 13. Notes for Demo

During the demo:

1. Show that the database is connected.
2. Show database row counts.
3. Generate a random customer ID.
4. Paste it into the Recommendation Engine page.
5. Generate recommendations.
6. Repeat with another random ID to show that the output changes.
7. Show SQL Analytics.
8. Show Performance Evidence.
9. Run Stored Procedure Demo.
