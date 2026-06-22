"""Analytics queries used by the Streamlit dashboard."""

from __future__ import annotations

import pandas as pd

from app.db import run_query


ROW_COUNTS_QUERY = """
SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews
ORDER BY table_name;
"""

STATE_ORDERS_QUERY = """
SELECT c.customer_state, COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_state
ORDER BY total_orders DESC
LIMIT %s;
"""

CATEGORY_SALES_QUERY = """
SELECT
    COALESCE(p.product_category_name, 'unknown') AS product_category_name,
    COUNT(*) AS total_items_sold,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY COALESCE(p.product_category_name, 'unknown')
ORDER BY total_items_sold DESC
LIMIT %s;
"""

PAYMENT_QUERY = """
SELECT
    payment_type,
    COUNT(*) AS total_payments,
    ROUND(AVG(payment_value)::numeric, 2) AS avg_payment_value,
    ROUND(SUM(payment_value)::numeric, 2) AS total_payment_value
FROM order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;
"""

REVIEW_QUERY = """
SELECT
    review_score,
    COUNT(*) AS total_reviews
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;
"""

PERFORMANCE_SUMMARY = pd.DataFrame([
    {
        "query": "Customer order history",
        "before_index_ms": 6.521,
        "after_index_ms": 0.162,
        "change": "Improved about 40.3x",
        "main_plan_change": "Seq Scan on orders changed to Index Scan using idx_orders_customer_id."
    },
    {
        "query": "Top-selling products",
        "before_index_ms": 477.947,
        "after_index_ms": 305.587,
        "change": "Improved about 1.56x",
        "main_plan_change": "Hash Join changed to Merge Join using idx_order_items_product_id."
    },
    {
        "query": "Seller revenue ranking",
        "before_index_ms": 69.428,
        "after_index_ms": 99.546,
        "change": "Slower in this run",
        "main_plan_change": "Planner still used full scans/hash aggregation because the query aggregates nearly all rows."
    },
    {
        "query": "Precomputed recommendation scores",
        "before_index_ms": None,
        "after_index_ms": 42.359,
        "change": "Stored score table query",
        "main_plan_change": "Reads product_recommendation_scores and joins products for final display."
    }
])


def get_row_counts() -> pd.DataFrame:
    return run_query(ROW_COUNTS_QUERY)


def get_orders_by_state(limit: int = 15) -> pd.DataFrame:
    return run_query(STATE_ORDERS_QUERY, (limit,))


def get_category_sales(limit: int = 15) -> pd.DataFrame:
    return run_query(CATEGORY_SALES_QUERY, (limit,))


def get_payment_summary() -> pd.DataFrame:
    return run_query(PAYMENT_QUERY)


def get_review_summary() -> pd.DataFrame:
    return run_query(REVIEW_QUERY)
