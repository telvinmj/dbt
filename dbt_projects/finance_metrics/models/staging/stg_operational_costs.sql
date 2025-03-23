{{ config(materialized='view') }}

SELECT
    cost_center_id,
    warehouse_location,
    monthly_rent,
    staff_cost,
    utilities_cost,
    month_date
FROM {{ ref('raw_operational_costs') }} 