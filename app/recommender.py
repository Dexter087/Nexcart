"""
Recommendation logic for NexCart.

The main recommendation query uses user-based collaborative filtering:
1. Find products/categories bought by the target customer's unique account.
2. Find other customers with overlapping purchases/categories.
3. Recommend products bought by those similar customers but not yet bought by the target.
4. Rank the candidates using SQL window functions.

If a customer has no usable purchase history, the code falls back to globally
popular products from product_recommendation_scores or order_items.
"""

from typing import Any, Dict, List

from .db import get_cursor


COLLABORATIVE_FILTERING_SQL = """
WITH target_customer AS (
    SELECT customer_unique_id
    FROM customers
    WHERE customer_id = %s
    LIMIT 1
),
target_products AS (
    SELECT DISTINCT oi.product_id
    FROM target_customer tc
    JOIN customers c
        ON c.customer_unique_id = tc.customer_unique_id
    JOIN orders o
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON oi.order_id = o.order_id
    WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing')
),
target_categories AS (
    SELECT DISTINCT p.product_category_name
    FROM target_products tp
    JOIN products p
        ON p.product_id = tp.product_id
    WHERE p.product_category_name IS NOT NULL
),
similar_customers AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT CASE
            WHEN oi.product_id IN (SELECT product_id FROM target_products)
            THEN oi.product_id
        END) AS overlapping_products,
        COUNT(DISTINCT CASE
            WHEN p.product_category_name IN (SELECT product_category_name FROM target_categories)
            THEN p.product_category_name
        END) AS overlapping_categories
    FROM customers c
    JOIN orders o
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON oi.order_id = o.order_id
    JOIN products p
        ON p.product_id = oi.product_id
    WHERE c.customer_unique_id <> (SELECT customer_unique_id FROM target_customer)
      AND (
            oi.product_id IN (SELECT product_id FROM target_products)
            OR p.product_category_name IN (SELECT product_category_name FROM target_categories)
          )
    GROUP BY c.customer_unique_id
),
candidate_products AS (
    SELECT
        oi.product_id,
        p.product_category_name,
        COUNT(*) AS similar_customer_purchases,
        SUM(sc.overlapping_products + sc.overlapping_categories) AS similarity_weight,
        AVG(oi.price) AS avg_price
    FROM similar_customers sc
    JOIN customers c
        ON c.customer_unique_id = sc.customer_unique_id
    JOIN orders o
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON oi.order_id = o.order_id
    JOIN products p
        ON p.product_id = oi.product_id
    WHERE oi.product_id NOT IN (SELECT product_id FROM target_products)
    GROUP BY oi.product_id, p.product_category_name
),
ranked_recommendations AS (
    SELECT
        product_id,
        product_category_name,
        similar_customer_purchases,
        similarity_weight,
        ROUND(avg_price, 2) AS avg_price,
        RANK() OVER (
            ORDER BY similarity_weight DESC,
                     similar_customer_purchases DESC,
                     avg_price DESC
        ) AS recommendation_rank,
        ROW_NUMBER() OVER (
            PARTITION BY product_category_name
            ORDER BY similarity_weight DESC,
                     similar_customer_purchases DESC,
                     avg_price DESC
        ) AS category_rank
    FROM candidate_products
)
SELECT
    product_id,
    product_category_name,
    similar_customer_purchases,
    similarity_weight,
    avg_price,
    recommendation_rank
FROM ranked_recommendations
WHERE category_rank <= 5
ORDER BY recommendation_rank
LIMIT %s;
"""


FALLBACK_SQL = """
WITH popular_products AS (
    SELECT
        oi.product_id,
        p.product_category_name,
        COUNT(*) AS total_units_sold,
        SUM(oi.price) AS total_revenue,
        COUNT(*) * 0.7 + SUM(oi.price) * 0.3 AS recommendation_score
    FROM order_items oi
    JOIN products p
        ON p.product_id = oi.product_id
    GROUP BY oi.product_id, p.product_category_name
),
ranked_products AS (
    SELECT
        product_id,
        product_category_name,
        total_units_sold,
        total_revenue,
        recommendation_score,
        ROW_NUMBER() OVER (ORDER BY recommendation_score DESC) AS recommendation_rank
    FROM popular_products
)
SELECT
    product_id,
    product_category_name,
    total_units_sold AS similar_customer_purchases,
    recommendation_score AS similarity_weight,
    ROUND(total_revenue / NULLIF(total_units_sold, 0), 2) AS avg_price,
    recommendation_rank
FROM ranked_products
ORDER BY recommendation_rank
LIMIT %s;
"""


def get_recommendations(customer_id: str, top_n: int = 10) -> Dict[str, Any]:
    """
    Return top-N recommendations for a customer.

    Parameters
    ----------
    customer_id:
        The Olist customer_id for which recommendations are required.
    top_n:
        Number of recommendations to return.
    """
    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")

    with get_cursor() as cursor:
        cursor.execute(COLLABORATIVE_FILTERING_SQL, (customer_id, top_n))
        rows: List[Dict[str, Any]] = list(cursor.fetchall())

        method = "collaborative_filtering"
        if not rows:
            cursor.execute(FALLBACK_SQL, (top_n,))
            rows = list(cursor.fetchall())
            method = "fallback_popularity"

    return {
        "customer_id": customer_id,
        "top_n": top_n,
        "method": method,
        "recommendations": rows,
    }
