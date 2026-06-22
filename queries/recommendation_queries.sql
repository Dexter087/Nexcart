-- =========================================================
-- NexCart Recommendation Query
-- PostgreSQL version
-- Purpose: standalone collaborative-filtering SQL evidence
-- =========================================================

-- This query selects one valid customer from the dataset and returns
-- top-N recommendations using CTEs and window functions.
-- The Streamlit app and FastAPI endpoint use the same logic in Python.

WITH selected_customer AS (
    SELECT c.customer_id
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status IN ('delivered', 'shipped', 'invoiced', 'processing')
    LIMIT 1
),
target_customer AS (
    SELECT c.customer_id, c.customer_unique_id
    FROM customers c
    JOIN selected_customer sc ON c.customer_id = sc.customer_id
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
LIMIT 10;
