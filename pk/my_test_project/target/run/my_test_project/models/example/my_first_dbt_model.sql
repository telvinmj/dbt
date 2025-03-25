
  
    

  create  table "dbt_sample"."my_test_my_test"."my_first_dbt_model__dbt_tmp"
  
  
    as
  
  (
    

SELECT
    transaction_id as id,
    order_id,
    amount,
    transaction_date
FROM "dbt_sample"."public"."raw_transactions"
WHERE transaction_id IS NOT NULL
  );
  