"""Recommendation queries for NexCart.

The main method implements user-based collaborative filtering in SQL. It finds
customers with overlapping product/category behaviour, gathers candidate products
from those similar customers, and ranks candidates using SQL window functions.
"""

from __future__ import annotations

import pandas as pd

from app.db import execute_statement, run_query


CUSTOMER_SAMPLE_QUERY = """
SELECT DISTINCT c.customer_id
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing')
ORDER BY c.customer_id
LIMIT %s;
"""


CUSTOMER_DETAIL_QUERY = """
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(oi.product_id) AS total_items,
    COALESCE(SUM(oi.price), 0) AS total_item_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE c.customer_id = %s
GROUP BY c.customer_id, c.customer_unique_id, c.customer_city, c.customer_state;
"""


RECOMMENDATION_QUERY = """
WITH target_customer AS (
    SELECT customer_id, customer_unique_id
    FROM customers
    WHERE customer_id = %s
),
target_orders AS (
    SELECT o.order_id
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN target_customer tc ON c.customer_unique_id = tc.customer_unique_id
    WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing')
),
target_purchases AS (
    SELECT DISTINCT
        oi.product_id,
        COALESCE(p.product_category_name, 'unknown') AS product_category_name
    FROM target_orders tor
    JOIN order_items oi ON tor.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
),
all_interactions AS (
    SELECT
        c.customer_unique_id,
        oi.product_id,
        COALESCE(p.product_category_name, 'unknown') AS product_category_name,
        COUNT(*) AS purchase_count,
        AVG(oi.price) AS avg_price
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing')
    GROUP BY c.customer_unique_id, oi.product_id, COALESCE(p.product_category_name, 'unknown')
),
overlap_events AS (
    SELECT
        ai.customer_unique_id AS similar_customer_unique_id,
        ai.product_id,
        ai.product_category_name,
        CASE
            WHEN ai.product_id = tp.product_id THEN 3
            WHEN ai.product_category_name = tp.product_category_name THEN 1
            ELSE 0
        END AS overlap_weight
    FROM all_interactions ai
    JOIN target_purchases tp
      ON ai.product_id = tp.product_id
      OR ai.product_category_name = tp.product_category_name
    JOIN target_customer tc
      ON ai.customer_unique_id <> tc.customer_unique_id
),
overlap_scores AS (
    SELECT DISTINCT
        similar_customer_unique_id,
        SUM(overlap_weight) OVER (PARTITION BY similar_customer_unique_id) AS similarity_score
    FROM overlap_events
    WHERE overlap_weight > 0
),
similar_customers AS (
    SELECT
        similar_customer_unique_id,
        similarity_score,
        RANK() OVER (ORDER BY similarity_score DESC) AS similarity_rank
    FROM overlap_scores
),
candidate_products AS (
    SELECT
        ai.product_id,
        ai.product_category_name,
        SUM(sc.similarity_score * ai.purchase_count) AS collaborative_score,
        COUNT(DISTINCT ai.customer_unique_id) AS similar_customer_count,
        SUM(ai.purchase_count) AS similar_purchase_count,
        AVG(ai.avg_price) AS avg_price
    FROM all_interactions ai
    JOIN similar_customers sc
      ON ai.customer_unique_id = sc.similar_customer_unique_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM target_purchases tp
        WHERE tp.product_id = ai.product_id
    )
    GROUP BY ai.product_id, ai.product_category_name
),
ranked_products AS (
    SELECT
        cp.product_id,
        cp.product_category_name,
        ROUND(cp.avg_price::numeric, 2) AS avg_price,
        cp.similar_customer_count,
        cp.similar_purchase_count,
        ROUND(cp.collaborative_score::numeric, 2) AS recommendation_score,
        RANK() OVER (
            ORDER BY cp.collaborative_score DESC,
                     cp.similar_customer_count DESC,
                     cp.similar_purchase_count DESC,
                     cp.avg_price DESC
        ) AS recommendation_rank,
        ROW_NUMBER() OVER (
            PARTITION BY cp.product_category_name
            ORDER BY cp.collaborative_score DESC,
                     cp.similar_customer_count DESC,
                     cp.similar_purchase_count DESC
        ) AS category_row_number
    FROM candidate_products cp
)
SELECT
    product_id,
    product_category_name,
    avg_price,
    similar_customer_count,
    similar_purchase_count,
    recommendation_score,
    recommendation_rank
FROM ranked_products
WHERE category_row_number <= 3
ORDER BY recommendation_rank
LIMIT %s;
"""


POPULARITY_FALLBACK_QUERY = """
WITH product_sales AS (
    SELECT
        p.product_id,
        COALESCE(p.product_category_name, 'unknown') AS product_category_name,
        COUNT(oi.order_id) AS total_units_sold,
        SUM(oi.price) AS total_revenue,
        AVG(oi.price) AS avg_price
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, COALESCE(p.product_category_name, 'unknown')
),
ranked AS (
    SELECT
        product_id,
        product_category_name,
        ROUND(avg_price::numeric, 2) AS avg_price,
        total_units_sold AS similar_purchase_count,
        total_revenue AS recommendation_score,
        RANK() OVER (ORDER BY total_units_sold DESC, total_revenue DESC) AS recommendation_rank,
        ROW_NUMBER() OVER (PARTITION BY product_category_name ORDER BY total_units_sold DESC, total_revenue DESC) AS category_row_number
    FROM product_sales
)
SELECT
    product_id,
    product_category_name,
    avg_price,
    NULL::integer AS similar_customer_count,
    similar_purchase_count,
    ROUND(recommendation_score::numeric, 2) AS recommendation_score,
    recommendation_rank
FROM ranked
WHERE category_row_number <= 3
ORDER BY recommendation_rank
LIMIT %s;
"""


SCORES_QUERY = """
SELECT
    prs.product_id,
    p.product_category_name,
    prs.total_units_sold,
    prs.total_revenue,
    prs.recommendation_score
FROM product_recommendation_scores prs
JOIN products p ON prs.product_id = p.product_id
ORDER BY prs.recommendation_score DESC
LIMIT %s;
"""


def get_sample_customer_ids(limit: int = 100) -> list[str]:
    df = run_query(CUSTOMER_SAMPLE_QUERY, (limit,))
    return df["customer_id"].tolist()


def get_customer_detail(customer_id: str) -> pd.DataFrame:
    return run_query(CUSTOMER_DETAIL_QUERY, (customer_id,))


def get_recommendations(customer_id: str, top_n: int = 10) -> tuple[pd.DataFrame, str]:
    """Return top-N recommendations and a note about the strategy used."""
    recs = run_query(RECOMMENDATION_QUERY, (customer_id, top_n))
    if recs.empty:
        recs = run_query(POPULARITY_FALLBACK_QUERY, (top_n,))
        return recs, "Popularity fallback used because this customer has too little usable purchase overlap."
    return recs, "Collaborative filtering used based on overlapping product/category purchases."


def refresh_recommendation_scores() -> None:
    execute_statement("CALL refresh_product_recommendation_scores();")


def get_precomputed_scores(limit: int = 10) -> pd.DataFrame:
    return run_query(SCORES_QUERY, (limit,))
