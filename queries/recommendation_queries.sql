/*
===========================================================
NexCart - Recommendation Queries
Track B: AI Recommendation Engine

How to use:
1. Replace the value in input_params.customer_id with a valid customer_id.
2. Change top_n if needed.
3. Run the query in pgAdmin or psql.

This query implements user-based collaborative filtering using SQL CTEs
and window functions. It recommends products bought by similar customers
but not yet bought by the selected customer.
===========================================================
*/

WITH input_params AS (
    SELECT
        'REPLACE_WITH_CUSTOMER_ID'::VARCHAR(50) AS customer_id,
        10::INT AS top_n
),
target_customer AS (
    SELECT c.customer_unique_id
    FROM customers c
    JOIN input_params ip
        ON c.customer_id = ip.customer_id
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
LIMIT (SELECT top_n FROM input_params);
