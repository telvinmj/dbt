{{
    config(
        materialized='table',
        tags=['mart', 'customers', 'risk', 'daily']
    )
}}

WITH customer_risk_enriched AS (
    SELECT * FROM {{ ref('int_customer_risk_enriched') }}
),

-- Reference cross-project models
claims AS (
    SELECT * FROM {{ ref('claims_processing', 'stg_claims') }}
),

policies AS (
    SELECT * FROM {{ ref('policy_management', 'stg_policies') }}
),

-- Calculate claim history metrics
customer_claims AS (
    SELECT
        customer_id,
        COUNT(*) AS total_claims,
        SUM(claim_amount) AS total_claim_amount,
        SUM(CASE WHEN claim_status = 'SETTLED' THEN settlement_amount ELSE 0 END) AS total_settlement_amount,
        AVG(claim_amount) AS avg_claim_amount,
        MAX(claim_date) AS last_claim_date,
        MIN(claim_date) AS first_claim_date
    FROM claims
    GROUP BY 1
),

-- Calculate policy metrics
customer_policies AS (
    SELECT
        customer_id,
        COUNT(*) AS active_policies,
        SUM(premium_amount) AS total_premium_amount,
        SUM(coverage_amount) AS total_coverage_amount,
        LISTAGG(policy_type, ', ') AS policy_types,
        MAX(start_date) AS newest_policy_date
    FROM policies
    WHERE status = 'ACTIVE'
    GROUP BY 1
)

SELECT
    cr.*,
    
    -- Claim history
    COALESCE(cc.total_claims, 0) AS total_claims,
    COALESCE(cc.total_claim_amount, 0) AS total_claim_amount,
    COALESCE(cc.total_settlement_amount, 0) AS total_settlement_amount,
    COALESCE(cc.avg_claim_amount, 0) AS avg_claim_amount,
    cc.last_claim_date,
    cc.first_claim_date,
    
    -- Policy information
    COALESCE(cp.active_policies, 0) AS active_policies,
    COALESCE(cp.total_premium_amount, 0) AS total_premium_amount,
    COALESCE(cp.total_coverage_amount, 0) AS total_coverage_amount,
    cp.policy_types,
    cp.newest_policy_date,
    
    -- Derived risk profile metrics
    CASE 
        WHEN cr.weighted_risk_score > 700 THEN 'Very High'
        WHEN cr.weighted_risk_score > 500 THEN 'High'
        WHEN cr.weighted_risk_score > 300 THEN 'Medium'
        WHEN cr.weighted_risk_score > 200 THEN 'Low'
        ELSE 'Very Low'
    END AS composite_risk_level,
    
    -- Risk-premium ratio
    CASE
        WHEN COALESCE(cp.total_premium_amount, 0) > 0 
        THEN ROUND(cr.weighted_risk_score / cp.total_premium_amount, 2)
        ELSE NULL
    END AS risk_premium_ratio,
    
    -- Customer value assessment
    CASE
        WHEN COALESCE(cp.active_policies, 0) >= 3 AND cr.weighted_risk_score < 300 THEN 'High Value'
        WHEN COALESCE(cp.active_policies, 0) >= 2 AND cr.weighted_risk_score < 500 THEN 'Medium Value'
        WHEN COALESCE(cp.active_policies, 0) = 1 AND cr.weighted_risk_score < 600 THEN 'Standard Value'
        ELSE 'Monitored'
    END AS customer_value_segment,
    
    -- Activity indication
    CASE
        WHEN cc.last_claim_date IS NOT NULL AND cc.last_claim_date > DATEADD('month', -6, CURRENT_DATE) THEN 'Recent Claim'
        WHEN cp.newest_policy_date IS NOT NULL AND cp.newest_policy_date > DATEADD('month', -3, CURRENT_DATE) THEN 'Recent Policy'
        ELSE 'No Recent Activity'
    END AS recent_activity
FROM customer_risk_enriched cr
LEFT JOIN customer_claims cc ON cr.customer_id = cc.customer_id
LEFT JOIN customer_policies cp ON cr.customer_id = cp.customer_id
