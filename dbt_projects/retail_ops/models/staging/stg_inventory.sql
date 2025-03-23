{{ config(materialized='view') }}

SELECT
    inventory_id,
    product_id,
    warehouse_location,
    quantity_on_hand,
    reorder_point,
    last_restock_date
FROM retail.raw_inventory 