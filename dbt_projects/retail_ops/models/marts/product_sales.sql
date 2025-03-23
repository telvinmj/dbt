{{ config(materialized='table') }}

WITH product_sales AS (
    SELECT 
        s.sale_id,
        s.customer_id,
        p.product_id,
        p.product_name,
        p.category,
        s.quantity,
        s.sale_date,
        s.total_amount
    FROM {{ ref('stg_sales') }} s
    JOIN {{ ref('stg_products') }} p ON s.product_id = p.product_id
)

SELECT * FROM product_sales 