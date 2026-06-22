/*
===========================================================
NexCart - Milestone 3 Performance Evidence
Database: PostgreSQL
Project Track: Track B - AI Recommendation Engine

This script:
1. Checks dataset size.
2. Runs EXPLAIN ANALYZE before indexing.
3. Creates indexes.
4. Runs EXPLAIN ANALYZE after indexing.
5. Creates and runs a stored procedure for recommendation scores.
===========================================================
*/


/*
===========================================================
SECTION 1: DATASET SIZE CHECKS
===========================================================
*/

SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL
SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers;


/*
===========================================================
SECTION 2: RESET ONLY MILESTONE 3 INDEXES
This ensures the BEFORE-index tests are actually before indexing.
===========================================================
*/

DROP INDEX IF EXISTS idx_orders_customer_id;
DROP INDEX IF EXISTS idx_order_items_order_id;
DROP INDEX IF EXISTS idx_order_items_product_id;
DROP INDEX IF EXISTS idx_order_items_seller_id;
DROP INDEX IF EXISTS idx_orders_purchase_timestamp;

ANALYZE;


/*
===========================================================
SECTION 3: BEFORE-INDEX PERFORMANCE TESTS
===========================================================
*/


/*
Query 1: Customer Order History
*/

EXPLAIN ANALYZE
SELECT 
    c.customer_id,
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    oi.product_id,
    p.product_category_name,
    oi.price,
    oi.freight_value
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE c.customer_id = (
    SELECT customer_id
    FROM customers
    LIMIT 1
)
ORDER BY o.order_purchase_timestamp DESC;


/*
Query 2: Top-Selling Products
*/

EXPLAIN ANALYZE
SELECT 
    p.product_id,
    p.product_category_name,
    COUNT(oi.order_id) AS total_items_sold,
    SUM(oi.price) AS total_revenue
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY 
    p.product_id,
    p.product_category_name
ORDER BY total_items_sold DESC, total_revenue DESC
LIMIT 10;


/*
Query 3: Seller Performance
*/

EXPLAIN ANALYZE
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(oi.order_id) AS total_items_sold,
    SUM(oi.price) AS total_sales_value
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
GROUP BY 
    s.seller_id,
    s.seller_city,
    s.seller_state
ORDER BY total_sales_value DESC
LIMIT 10;


/*
===========================================================
SECTION 4: INDEX CREATION
===========================================================
*/

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id
ON order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
ON order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller_id
ON order_items(seller_id);

CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp
ON orders(order_purchase_timestamp);

ANALYZE;


/*
===========================================================
SECTION 5: AFTER-INDEX PERFORMANCE TESTS
===========================================================
*/


/*
Query 1 After Indexing: Customer Order History
*/

EXPLAIN ANALYZE
SELECT 
    c.customer_id,
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    oi.product_id,
    p.product_category_name,
    oi.price,
    oi.freight_value
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE c.customer_id = (
    SELECT customer_id
    FROM customers
    LIMIT 1
)
ORDER BY o.order_purchase_timestamp DESC;


/*
Query 2 After Indexing: Top-Selling Products
*/

EXPLAIN ANALYZE
SELECT 
    p.product_id,
    p.product_category_name,
    COUNT(oi.order_id) AS total_items_sold,
    SUM(oi.price) AS total_revenue
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY 
    p.product_id,
    p.product_category_name
ORDER BY total_items_sold DESC, total_revenue DESC
LIMIT 10;


/*
Query 3 After Indexing: Seller Performance
*/

EXPLAIN ANALYZE
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(oi.order_id) AS total_items_sold,
    SUM(oi.price) AS total_sales_value
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
GROUP BY 
    s.seller_id,
    s.seller_city,
    s.seller_state
ORDER BY total_sales_value DESC
LIMIT 10;


/*
===========================================================
SECTION 6: RECOMMENDATION SCORE TABLE
===========================================================
*/

CREATE TABLE IF NOT EXISTS product_recommendation_scores (
    product_id VARCHAR(50) PRIMARY KEY,
    total_units_sold INTEGER NOT NULL DEFAULT 0,
    total_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0,
    recommendation_score NUMERIC(12, 2) NOT NULL DEFAULT 0,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recommendation_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


/*
===========================================================
SECTION 7: STORED PROCEDURE
This procedure refreshes product recommendation scores using
existing order_items data. It modifies the recommendation score
table and supports the recommendation engine.
===========================================================
*/

CREATE OR REPLACE PROCEDURE refresh_product_recommendation_scores()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE product_recommendation_scores;

    INSERT INTO product_recommendation_scores (
        product_id,
        total_units_sold,
        total_revenue,
        recommendation_score,
        last_updated
    )
    SELECT 
        oi.product_id,
        COUNT(*) AS total_units_sold,
        SUM(oi.price) AS total_revenue,
        COUNT(*) * 0.7 + SUM(oi.price) * 0.3 AS recommendation_score,
        CURRENT_TIMESTAMP
    FROM order_items oi
    GROUP BY oi.product_id;
END;
$$;


/*
Run the stored procedure.
*/

CALL refresh_product_recommendation_scores();


/*
Verify that the stored procedure populated the score table.
*/

SELECT 
    COUNT(*) AS products_with_scores,
    SUM(total_units_sold) AS total_units_counted,
    SUM(total_revenue) AS total_revenue_counted
FROM product_recommendation_scores;


/*
===========================================================
SECTION 8: TOP-N RECOMMENDATION QUERY
===========================================================
*/

EXPLAIN ANALYZE
SELECT 
    prs.product_id,
    p.product_category_name,
    prs.total_units_sold,
    prs.total_revenue,
    prs.recommendation_score
FROM product_recommendation_scores prs
JOIN products p
    ON prs.product_id = p.product_id
ORDER BY prs.recommendation_score DESC
LIMIT 10;