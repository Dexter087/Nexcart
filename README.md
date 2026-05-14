GitHub Repository Link:
https://github.com/Dexter087/Nexcart.git

Project Title: NexCart — E-commerce Recommendation System
Course: Z2004 Database Management Systems
Milestone 2 — Dataset and Queries
Database Used: PostgreSQL

Team Members:
1. Daksha Mothukuri - ZDA24B030
2. Manoj Phani Varma Vadapalli - ZDA24B040
3. V S S Preeti Ananya Yamali - ZDA24B002

==================================================================

1. PROJECT OVERVIEW

NexCart is an e-commerce recommendation system built on top of a relational PostgreSQL database using the Olist-style marketplace dataset. The aim of this milestone is to load the dataset into PostgreSQL, preserve the relational links between customers, sellers, products, orders, payments, and reviews, and then run a set of analytical SQL queries that demonstrate different query types required in the course rubric.

This milestone submission contains:
- the dataset files used for loading
- the SQL query files
- this README file with reproduction instructions, data dictionary, and explanation of the query design


2. IMPORTANT NOTE ON THE SCHEMA CHANGE

In Milestone 1, the ER diagram included a table named category_translation because the source dataset also provides a translation file for product categories.

However, during actual PostgreSQL implementation and dataset import, that table was removed from the final working schema. The reason was practical: some values present in products.product_category_name did not match properly with the translation file during import, which caused foreign key problems. Since category translation is not a transactional requirement and does not affect the core customer-order-product-payment-review relationships, the final schema was simplified by keeping product_category_name directly in the products table.

This means:
- the Milestone 1 ER diagram and the Milestone 2 working schema are slightly different
- the final implemented schema does not contain category_translation
- all queries in this milestone are written using the final implemented schema only


3. FINAL WORKING TABLES

The final PostgreSQL database contains the following tables:

1. customers
2. sellers
3. products
4. orders
5. order_items
6. order_payments
7. order_reviews


4. DATASET FILES USED

The following CSV files were used from the dataset folder:

1. olist_customers_dataset.csv
2. olist_sellers_dataset.csv
3. olist_products_dataset.csv
4. olist_orders_dataset.csv
5. olist_order_items_dataset.csv
6. olist_order_payments_dataset.csv
7. olist_order_reviews_dataset.csv

The geolocation file was not used in the final implementation.


5. DATA DICTIONARY

customers
- customer_id: unique customer identifier
- customer_unique_id: grouped customer identifier used in the dataset
- customer_zip_code_prefix: customer ZIP code prefix
- customer_city: customer city
- customer_state: customer state

sellers
- seller_id: unique seller identifier
- seller_zip_code_prefix: seller ZIP code prefix
- seller_city: seller city
- seller_state: seller state

products
- product_id: unique product identifier
- product_category_name: category name of the product
- product_name_length: length of product name
- product_description_length: length of product description
- product_photos_qty: number of product photos
- product_weight_g: product weight in grams
- product_length_cm: product length in centimetres
- product_height_cm: product height in centimetres
- product_width_cm: product width in centimetres

orders
- order_id: unique order identifier
- customer_id: customer linked to the order
- order_status: status of the order
- order_purchase_timestamp: timestamp when order was placed
- order_approved_at: timestamp when order was approved
- order_delivered_carrier_date: timestamp when order reached carrier
- order_delivered_customer_date: timestamp when order reached customer
- order_estimated_delivery_date: estimated delivery date

order_items
- order_id: order identifier
- order_item_id: item number inside an order
- product_id: product linked to the order item
- seller_id: seller linked to the order item
- shipping_limit_date: shipping deadline
- price: item price
- freight_value: freight or shipping charge

order_payments
- order_id: order identifier
- payment_sequential: sequence number of payment for an order
- payment_type: type of payment
- payment_installments: number of installments
- payment_value: payment amount

order_reviews
- review_id: review identifier
- order_id: order identifier linked to the review
- review_score: review rating from 1 to 5
- review_comment_title: short review title
- review_comment_message: review text
- review_creation_date: date when review was created
- review_answer_timestamp: timestamp related to review handling


6. STEP-BY-STEP REPRODUCTION GUIDE

Step 1 — Open PostgreSQL in pgAdmin

Open pgAdmin and connect to the local PostgreSQL server.

Step 2 — Create the project database

Create a new database by running:

CREATE DATABASE nexcart_olist;

After creating it, open Query Tool inside the nexcart_olist database.

Step 3 — Run the schema

Run the  schema.sql file inside nexcart_olist (This is the updated schema file).

This creates the following tables:
- customers
- sellers
- products
- orders
- order_items
- order_payments
- order_reviews

Step 4 — Import the dataset

Use pgAdmin Import/Export Data for each table.

For every import, use:
- Format: csv
- Header: Yes
- Delimiter: ,
- Quote: "
- Escape: "
- Encoding: UTF8

Exact order of import:
1. customers ← olist_customers_dataset.csv
2. sellers ← olist_sellers_dataset.csv
3. products ← olist_products_dataset.csv
4. orders ← olist_orders_dataset.csv
5. order_items ← olist_order_items_dataset.csv
6. order_payments ← olist_order_payments_dataset.csv
7. order_reviews ← olist_order_reviews_dataset.csv

This order is important because:
- orders depends on customers
- order_items depends on orders, products, and sellers
- order_payments depends on orders
- order_reviews depends on orders

Step 5 — Verify that the import worked

Run the following:

SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM sellers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;
SELECT COUNT(*) FROM order_payments;
SELECT COUNT(*) FROM order_reviews;

If each query returns a valid count, the dataset has been loaded successfully.


7. QUERY FILES

The queries for this milestone are provided in one combined SQL file:

queries.sql

This file contains all 10 required queries for Milestone 2. The queries are arranged from simpler analytical tasks to more advanced ones so that they can be checked and run in a logical order.


8. EXPLANATION OF THE QUERIES

Query 1
This query counts the total number of orders from each customer state. It joins customers with orders through customer_id, groups the data by customer_state, and counts the number of orders in each state. This helps identify which states contribute the highest order volume.

Query 2
This query calculates the average payment value for each payment type. It uses the order_payments table, groups the rows by payment_type, and computes the average payment_value for each group. This helps compare customer payment behaviour across different payment methods.

Query 3
This query joins orders with customers so that each order can be viewed together with customer city and state. It helps connect transactional data with customer location information and confirms that the customer-order relationship has been loaded correctly.

Query 4
This query joins order_items with sellers using seller_id. It shows which seller handled each sold item and where that seller is located. This helps in seller-level transaction analysis.

Query 5
This query finds customers whose number of orders is greater than the average customer order count. It uses subqueries to first calculate order counts per customer and then compare them to the average. This helps identify highly active customers.

Query 6
This query finds products that were never sold. It checks which products in the products table do not appear in order_items. This helps identify listed products that never entered any transaction.

Query 7
This query uses a Common Table Expression to isolate delivered orders with valid delivery dates and then calculates delivery delay in days. It helps evaluate delivery performance by comparing actual delivery date with estimated delivery date.

Query 8
This query uses a Common Table Expression to calculate how many sold items belong to each product category. It helps identify the most frequently sold categories in the dataset.

Query 9
This query calculates total customer spending by joining orders with order_payments and then ranks customers from highest spender to lowest spender using a window function. This helps identify high-value customers.

Query 10
This query calculates the average selling price of each product and ranks products within each category using a window function. This helps compare products inside their own categories rather than across the entire dataset.


9. HOW TO RUN THE QUERIES

Open Query Tool in pgAdmin after the dataset has been imported.

Open the file queries.sql and run the queries in the same order in which they appear in the file i.e. from query 1 to 10.

This order is recommended because the file begins with simpler aggregation and join queries, then moves to subqueries, followed by Common Table Expressions, and finally window functions. Running them in this sequence makes the results easier to check and understand.


10. QUERY COVERAGE SUMMARY

The final query set satisfies the Milestone 2 requirements:
- 2 Aggregations
- 2 Joins
- 2 Subqueries
- 2 CTEs
- 2 Window Functions


11. AI USAGE DISCLOSURE

This section is included because the course guideline asks for a short AI usage disclosure in the README or report.

AI tools were used for:
- refining PostgreSQL table definitions
- correcting errors and polishing SQL queries
- improving README structure and wording

All generated content was reviewed, edited, and adapted before use in the final submission.

12. CONCLUSION

The final implementation uses PostgreSQL and a cleaned Olist-based dataset structure to support reproducible query execution. The schema was adjusted during implementation to make the dataset load successfully and allow all milestone queries to run consistently on a fresh local database.
