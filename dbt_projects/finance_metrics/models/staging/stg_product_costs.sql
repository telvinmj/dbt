{{ config(materialized='view') }}

SELECT * FROM finance.raw_product_costs 