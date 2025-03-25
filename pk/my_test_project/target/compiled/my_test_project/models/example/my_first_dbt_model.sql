

SELECT
    transaction_id as id,
    order_id,
    amount,
    transaction_date
FROM "dbt_sample"."public"."raw_transactions"
WHERE transaction_id IS NOT NULL