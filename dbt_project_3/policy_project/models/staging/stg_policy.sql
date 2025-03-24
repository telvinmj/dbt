{{
  config(
    materialized = 'view',
    schema = 'staging'
  )
}}

WITH source_data AS (
    SELECT 
        policy_id,
        customer_id,
        policy_type,
        policy_number,
        premium_amount,
        coverage_limit,
        deductible_amount,
        effective_date,
        expiration_date,
        status,
        created_at,
        updated_at
    FROM {{ ref('raw_policies') }}
)

SELECT 
    policy_id,
    customer_id,
    policy_type,
    policy_number,
    premium_amount,
    coverage_limit,
    deductible_amount,
    effective_date,
    expiration_date,
    status,
    created_at,
    updated_at
FROM source_data 