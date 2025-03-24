{{
    config(
        materialized='view',
        tags=['intermediate', 'policies', 'daily']
    )
}}

WITH policies AS (
    SELECT * FROM {{ ref('stg_policies') }}
),

agents AS (
    SELECT * FROM {{ ref('stg_agents') }}
),

-- Reference cross-project models using the full project path
customer_risk AS (
    SELECT * FROM {{ ref('customer_risk', 'int_customer_risk_enriched') }}
)

SELECT
    p.policy_id,
    p.customer_id,
    p.policy_type,
    p.start_date,
    p.end_date,
    p.premium_amount,
    p.coverage_amount,
    p.status,
    p.agent_id,
    p.policy_number,
    p.policy_status,
    p.policy_tenure_months,
    p.coverage_premium_ratio,
    -- Agent information
    a.agent_name,
    a.office_location,
    a.commission_rate,
    a.agent_status,
    a.tenure_months as agent_tenure_months,
    -- Customer risk information
    cr.full_name as customer_name,
    cr.risk_score,
    cr.risk_level,
    cr.risk_category,
    cr.credit_score,
    cr.previous_claims_count,
    cr.weighted_risk_score,
    -- Additional derived metrics
    CASE
        WHEN p.policy_type = 'AUTO' AND cr.previous_claims_count > 2 THEN 'High'
        WHEN p.policy_type = 'HOME' AND cr.risk_score > 600 THEN 'High'
        WHEN p.policy_type = 'LIFE' AND cr.age > 65 THEN 'High'
        WHEN cr.risk_level IN ('Very High Risk', 'High Risk') THEN 'High'
        WHEN cr.risk_level = 'Medium Risk' THEN 'Medium'
        ELSE 'Low'
    END AS policy_risk_level,
    
    -- Premium adjustment suggestion based on risk
    CASE
        WHEN cr.weighted_risk_score > 700 THEN ROUND(p.premium_amount * 1.15, 2)
        WHEN cr.weighted_risk_score > 500 THEN ROUND(p.premium_amount * 1.10, 2)
        WHEN cr.weighted_risk_score > 300 THEN ROUND(p.premium_amount * 1.05, 2)
        WHEN cr.weighted_risk_score < 200 THEN ROUND(p.premium_amount * 0.95, 2)
        ELSE p.premium_amount
    END AS suggested_premium,
    
    -- Commission amount
    ROUND(p.premium_amount * a.commission_rate, 2) AS commission_amount
FROM policies p
LEFT JOIN agents a ON p.agent_id = a.agent_id
LEFT JOIN customer_risk cr ON p.customer_id = cr.customer_id
