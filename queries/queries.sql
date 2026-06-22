-- =========================================================
-- NexCart Milestone 2 Queries
-- PostgreSQL version
-- Based on imported Olist dataset
-- =========================================================

-- -------------------------------------------------------------------
-- Q1. Aggregation
-- Total number of orders by customer state
-- Purpose:
-- Counts how many orders were placed by customers from each state.
-- This helps identify the states contributing the highest order volume.
-- -------------------------------------------------------------------
SELECT
    c.customer_state,
    COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_state
ORDER BY total_orders DESC;


-- -------------------------------------------------------------------
-- Q2. Aggregation
-- Average payment value by payment type
-- Purpose:
-- Groups payment records by payment type and computes the average
-- payment value for each category.
-- -------------------------------------------------------------------
SELECT
    payment_type,
    ROUND(AVG(payment_value), 2) AS avg_payment_value
FROM order_payments
GROUP BY payment_type
ORDER BY avg_payment_value DESC;


-- -------------------------------------------------------------------
-- Q3. Join
-- Orders with customer location details
-- Purpose:
-- Combines orders with customer city and state so each order can be
-- viewed together with customer location data.
-- -------------------------------------------------------------------
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_city,
    c.customer_state
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
ORDER BY o.order_purchase_timestamp
LIMIT 50;


-- -------------------------------------------------------------------
-- Q4. Join
-- Order items with seller details
-- Purpose:
-- Joins order items with seller information to show who supplied each
-- item and where that seller is located.
-- -------------------------------------------------------------------
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    oi.price,
    oi.freight_value
FROM order_items oi
JOIN sellers s
    ON oi.seller_id = s.seller_id
ORDER BY oi.order_id, oi.order_item_id
LIMIT 50;


-- -------------------------------------------------------------------
-- Q5. Subquery
-- Customers who placed more orders than the average customer
-- Purpose:
-- Finds highly active customers by comparing each customer's order
-- count against the average order count per customer.
-- -------------------------------------------------------------------
SELECT
    customer_id,
    order_count
FROM (
    SELECT
        customer_id,
        COUNT(order_id) AS order_count
    FROM orders
    GROUP BY customer_id
) customer_orders
WHERE order_count > (
    SELECT AVG(order_total)
    FROM (
        SELECT COUNT(order_id) AS order_total
        FROM orders
        GROUP BY customer_id
    ) avg_orders
)
ORDER BY order_count DESC;


-- -------------------------------------------------------------------
-- Q6. Subquery
-- Products that have never been ordered
-- Purpose:
-- Identifies listed products that do not appear in the order_items
-- table and therefore have never been sold.
-- -------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_category_name
FROM products p
WHERE NOT EXISTS (
    SELECT 1
    FROM order_items oi
    WHERE oi.product_id = p.product_id
)
ORDER BY p.product_id;


-- -------------------------------------------------------------------
-- Q7. CTE
-- Delivered orders and their delivery delay in days
-- Purpose:
-- Creates a temporary set of delivered orders with valid delivery
-- dates, then calculates delay as actual delivery date minus estimated
-- delivery date.
-- Positive values indicate late delivery.
-- -------------------------------------------------------------------
WITH delivered_orders AS (
    SELECT
        order_id,
        order_purchase_timestamp,
        order_delivered_customer_date,
        order_estimated_delivery_date
    FROM orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
)
SELECT
    order_id,
    order_purchase_timestamp,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    (order_delivered_customer_date::date - order_estimated_delivery_date::date) AS delivery_delay_days
FROM delivered_orders
ORDER BY delivery_delay_days DESC
LIMIT 50;


-- -------------------------------------------------------------------
-- Q8. CTE
-- Top product categories by number of sold items
-- Purpose:
-- Builds a temporary summary of total sold items per category and then
-- returns the most frequently sold product categories.
-- -------------------------------------------------------------------
WITH category_sales AS (
    SELECT
        p.product_category_name,
        COUNT(*) AS total_items_sold
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY p.product_category_name
)
SELECT
    product_category_name,
    total_items_sold
FROM category_sales
ORDER BY total_items_sold DESC
LIMIT 20;


-- -------------------------------------------------------------------
-- Q9. Window Function
-- Top 10 customers by total spending
-- Purpose:
-- Calculates total spending per customer and ranks customers from
-- highest spender to lowest spender using RANK().
-- -------------------------------------------------------------------
SELECT
    customer_id,
    total_spent,
    RANK() OVER (ORDER BY total_spent DESC) AS spending_rank
FROM (
    SELECT
        o.customer_id,
        SUM(op.payment_value) AS total_spent
    FROM orders o
    JOIN order_payments op
        ON o.order_id = op.order_id
    GROUP BY o.customer_id
) customer_spending
ORDER BY spending_rank
LIMIT 10;


-- -------------------------------------------------------------------
-- Q10. Window Function
-- Rank products within each category by average price
-- Purpose:
-- Computes the average selling price of each product and ranks
-- products separately inside each category using ROW_NUMBER().
-- -------------------------------------------------------------------
SELECT
    product_category_name,
    product_id,
    avg_price,
    ROW_NUMBER() OVER (
        PARTITION BY product_category_name
        ORDER BY avg_price DESC
    ) AS category_price_rank
FROM (
    SELECT
        p.product_category_name,
        oi.product_id,
        ROUND(AVG(oi.price), 2) AS avg_price
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY p.product_category_name, oi.product_id
) ranked_products
ORDER BY product_category_name, category_price_rank;
