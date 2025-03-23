{{ config(materialized='table') }}

WITH product_costs AS (
    SELECT
        product_id,
        CAST(cost_price AS DECIMAL(10,2)) as cost_price,
        CAST(overhead_cost AS DECIMAL(10,2)) as overhead_cost,
        CAST((cost_price + overhead_cost) AS DECIMAL(10,2)) as total_cost
    FROM {{ ref('stg_product_costs') }}
),

sales_data AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        s.quantity,
        CAST(s.total_amount AS DECIMAL(10,2)) as total_amount
    FROM retail.raw_products p
    JOIN retail.raw_sales s ON p.product_id = s.product_id
    GROUP BY 1, 2, 3, 4, 5
),

profitability AS (
    SELECT
        s.product_id,
        s.product_name,
        s.category,
        COUNT(*) as total_units_sold,
        SUM(CAST(s.total_amount AS DECIMAL(10,2))) as total_revenue,
        pc.total_cost * COUNT(*) as total_cost,
        SUM(CAST(s.total_amount AS DECIMAL(10,2))) - (pc.total_cost * COUNT(*)) as gross_profit,
        CASE 
            WHEN SUM(CAST(s.total_amount AS DECIMAL(10,2))) > 0 
            THEN ((SUM(CAST(s.total_amount AS DECIMAL(10,2))) - (pc.total_cost * COUNT(*))) / SUM(CAST(s.total_amount AS DECIMAL(10,2)))) * 100 
            ELSE 0 
        END as profit_margin
    FROM sales_data s
    JOIN product_costs pc ON s.product_id = pc.product_id
    GROUP BY 1, 2, 3, pc.total_cost
)

SELECT * FROM profitability 