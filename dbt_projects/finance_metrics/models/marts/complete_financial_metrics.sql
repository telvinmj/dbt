{{ config(materialized='table') }}

WITH sales_data AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        s.quantity,
        CAST(s.total_amount AS DECIMAL(10,2)) as total_amount
    FROM {{ ref('stg_products') }} p
    JOIN {{ ref('stg_sales') }} s ON p.product_id = s.product_id
),

product_metrics AS (
    SELECT
        s.*,
        pc.cost_price,
        pc.overhead_cost,
        CAST(mc.marketing_cost AS DECIMAL(10,2)) as marketing_cost,
        mc.campaign_name
    FROM sales_data s
    LEFT JOIN {{ ref('stg_product_costs') }} pc ON s.product_id = pc.product_id
    LEFT JOIN {{ ref('stg_marketing_costs') }} mc ON s.product_id = mc.product_id
),

final_metrics AS (
    SELECT
        product_id,
        product_name,
        category,
        SUM(quantity) as total_units_sold,
        SUM(total_amount) as total_revenue,
        SUM(quantity * (cost_price + overhead_cost)) as total_cost,
        SUM(total_amount - (quantity * (cost_price + overhead_cost))) as gross_profit,
        marketing_cost,
        campaign_name
    FROM product_metrics
    GROUP BY 1, 2, 3, marketing_cost, campaign_name
)

SELECT 
    *,
    gross_profit - marketing_cost as net_profit,
    (gross_profit - marketing_cost) / NULLIF(total_revenue, 0) * 100 as net_profit_margin
FROM final_metrics 