{{ config(materialized='view') }}

SELECT
    promotion_id,
    product_id,
    promotion_name,
    discount_percentage,
    start_date,
    end_date
FROM retail.raw_promotions 