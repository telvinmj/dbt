{{
    config(
        materialized='view',
        tags=['intermediate', 'customers', 'risk', 'daily']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

risk_factors AS (
    SELECT * FROM {{ ref('stg_risk_factors') }}
)

SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    c.phone,
    c.address,
    c.city,
    c.state,
    c.zip_code,
    c.date_of_birth,
    c.gender,
    c.joining_date,
    c.age,
    c.months_as_customer,
    -- Risk information
    r.risk_id,
    r.assessment_date,
    r.credit_score,
    r.credit_rating,
    r.claim_frequency,
    r.risk_score,
    r.previous_claims_count,
    r.risk_category,
    r.days_since_last_assessment,
    -- Risk factor adjustments
    CASE
        WHEN c.age < 25 OR c.age > 70 THEN r.risk_score * 1.2
        ELSE r.risk_score
    END AS age_adjusted_risk_score,
    -- Customer segments
    CASE
        WHEN c.months_as_customer >= 36 AND r.risk_category = 'LOW_RISK' THEN 'PREMIUM'
        WHEN c.months_as_customer >= 24 AND r.risk_category IN ('LOW_RISK', 'MEDIUM_RISK') THEN 'PREFERRED'
        WHEN c.months_as_customer >= 12 THEN 'STANDARD'
        ELSE 'NEW'
    END AS customer_segment,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    c._dbt_source_project
FROM customers c
LEFT JOIN risk_factors r ON c.customer_id = r.customer_id
