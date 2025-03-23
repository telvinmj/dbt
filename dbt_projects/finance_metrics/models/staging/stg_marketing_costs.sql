{{ config(materialized='view') }}

SELECT
    campaign_id,
    product_id,
    campaign_name,
    marketing_cost,
    start_date,
    end_date
FROM {{ ref('raw_marketing_costs') }} 