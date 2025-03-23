{{ config(materialized='view') }}

SELECT
    sale_id,
    product_id,
    customer_id,
    quantity,
    sale_date,
    total_amount
FROM retail.raw_sales 