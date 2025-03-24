{{
  config(
    materialized = 'table',
    schema = 'marts'
  )
}}

WITH stg_claim AS (
    SELECT * FROM {{ ref('stg_claim') }}
),

-- Local reference to customer data
customer_dim AS (
    SELECT * FROM {{ ref('stg_customer') }}
),

-- Local reference to policy data
policy_fact AS (
    SELECT * FROM {{ ref('stg_policy') }}
),

claim_fact AS (
    SELECT
        c.claim_id,
        c.policy_id,
        c.customer_id,
        c.claim_date,
        c.incident_date,
        c.description,
        c.claim_amount,
        c.approved_amount,
        c.status,
        c.adjuster_id,
        
        -- Customer information
        cust.first_name || ' ' || cust.last_name AS customer_name,
        cust.email AS customer_email,
        
        -- Policy information
        p.policy_type,
        p.policy_number,
        p.premium_amount,
        p.coverage_limit,
        p.deductible_amount,
        
        -- Calculated fields
        DATEDIFF('day', c.incident_date, c.claim_date) AS days_to_file_claim,
        CASE 
            WHEN c.approved_amount IS NULL THEN NULL
            ELSE c.approved_amount / NULLIF(c.claim_amount, 0) 
        END AS approval_ratio,
        
        CASE
            WHEN c.approved_amount > p.coverage_limit THEN p.coverage_limit
            ELSE c.approved_amount
        END AS final_approved_amount,
        
        c.created_at,
        c.updated_at
    FROM stg_claim c
    LEFT JOIN customer_dim cust ON c.customer_id = cust.customer_id
    LEFT JOIN policy_fact p ON c.policy_id = p.policy_id
)

SELECT * FROM claim_fact 