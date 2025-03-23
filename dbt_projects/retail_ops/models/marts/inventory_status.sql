{{ config(materialized='table') }}

WITH inventory_metrics AS (
    SELECT 
        i.inventory_id,
        i.warehouse_location,
        p.product_id,
        p.product_name,
        p.category,
        i.quantity_on_hand,
        i.reorder_point,
        i.last_restock_date,
        CASE 
            WHEN i.quantity_on_hand <= i.reorder_point THEN 'Reorder Required'
            WHEN i.quantity_on_hand <= (i.reorder_point * 1.5) THEN 'Low Stock'
            ELSE 'Sufficient Stock'
        END as stock_status
    FROM {{ ref('stg_inventory') }} i
    JOIN {{ ref('stg_products') }} p ON i.product_id = p.product_id
)

SELECT * FROM inventory_metrics 