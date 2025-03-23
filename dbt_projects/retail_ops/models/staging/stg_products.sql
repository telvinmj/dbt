{{ config(materialized='view') }}

SELECT * FROM retail.raw_products 