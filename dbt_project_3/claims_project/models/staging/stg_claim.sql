{{
  config(
    materialized = 'view',
    schema = 'staging'
  )
}}

WITH source_data AS (
    SELECT 
        claim_id,
        policy_id,
        customer_id,
        claim_date,
        incident_date,
        description,
        claim_amount,
        approved_amount,
        status,
        adjuster_id,
        created_at,
        updated_at
    FROM {{ ref('raw_claims') }}
)

SELECT 
    claim_id,
    policy_id,
    customer_id,
    claim_date,
    incident_date,
    description,
    claim_amount,
    approved_amount,
    status,
    adjuster_id,
    created_at,
    updated_at
FROM source_data 