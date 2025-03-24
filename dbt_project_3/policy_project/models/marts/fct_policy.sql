{{
  config(
    materialized = 'table',
    schema = 'marts'
  )
}}

WITH stg_policy AS (
    SELECT * FROM {{ ref('stg_policy', 'policy_project') }}
),

-- Explicit cross-project reference to customer data
customer_dim AS (
    SELECT * FROM {{ ref('stg_customer', 'customer_project') }}
),

policy_fact AS (
    SELECT
        p.policy_id,
        p.customer_id,
        p.policy_type,
        p.policy_number,
        p.premium_amount,
        p.coverage_limit,
        p.deductible_amount,
        p.effective_date,
        p.expiration_date,
        p.status,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.email AS customer_email,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_of_birth)) AS customer_age,
        DATEDIFF('day', p.effective_date, p.expiration_date) AS policy_duration_days,
        CASE 
            WHEN p.status = 'active' AND CURRENT_DATE > p.expiration_date THEN 'expired'
            ELSE p.status
        END AS current_status,
        p.created_at,
        p.updated_at
    FROM stg_policy p
    LEFT JOIN customer_dim c ON p.customer_id = c.customer_id
)

SELECT * FROM policy_fact 