
  create view "dbt_sample"."ecommerce_ecommerce_schema"."stg_orders__dbt_tmp"
    
    
  as (
    

SELECT
    order_id,
    customer_id,
    order_date,
    status
FROM "dbt_sample"."public"."raw_orders"
  );