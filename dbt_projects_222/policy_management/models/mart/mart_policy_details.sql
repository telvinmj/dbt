{{
    config(
        materialized='table',
        tags=['mart', 'policies', 'daily']
    )
}}

WITH policies_enriched AS (
    SELECT * FROM {{ ref('int_policies_enriched') }}
),

-- Reference cross-project models
claims AS (
    SELECT * FROM {{ ref('claims_processing', 'stg_claims') }}
),

customer_risk AS (
    SELECT * FROM {{ ref('customer_risk', 'mart_customer_risk_profile') }}
),

-- Calculate policy claim metrics
policy_claims AS (
    SELECT
        policy_id,
        COUNT(*) AS claim_count,
        SUM(claim_amount) AS total_claim_amount,
        AVG(claim_amount) AS avg_claim_amount,
        MAX(claim_date) AS last_claim_date,
        MIN(claim_date) AS first_claim_date,
        SUM(CASE WHEN claim_status = 'SETTLED' THEN 1 ELSE 0 END) AS settled_claims,
        SUM(CASE WHEN claim_status = 'DENIED' THEN 1 ELSE 0 END) AS denied_claims,
        SUM(CASE WHEN claim_status = 'PENDING' THEN 1 ELSE 0 END) AS pending_claims
    FROM claims
    GROUP BY 1
),

-- Reference to the customer risk project
customer_risk_profile AS (
    {% if execute %}
        {% if adapter.get_relation(this.database, 'mart', 'mart_customer_risk_profile') %}
            SELECT * FROM {{ ref('customer_risk', 'mart_customer_risk_profile') }}
        {% else %}
            SELECT
                'CU0000' AS customer_id,
                0 AS credit_score,
                'UNKNOWN' AS claim_frequency,
                0 AS risk_score,
                0 AS previous_claims_count,
                'UNKNOWN' AS risk_category,
                'UNKNOWN' AS customer_name,
                'customer_risk' AS _dbt_source_project
            WHERE 1=0
        {% endif %}
    {% else %}
        SELECT
            'CU0000' AS customer_id,
            0 AS credit_score,
            'UNKNOWN' AS claim_frequency,
            0 AS risk_score,
            0 AS previous_claims_count,
            'UNKNOWN' AS risk_category,
            'UNKNOWN' AS customer_name,
            'customer_risk' AS _dbt_source_project
        WHERE 1=0
    {% endif %}
)

SELECT
    p.*,
    
    -- Claims information
    COALESCE(pc.claim_count, 0) AS claim_count,
    COALESCE(pc.total_claim_amount, 0) AS total_claim_amount,
    COALESCE(pc.avg_claim_amount, 0) AS avg_claim_amount,
    pc.last_claim_date,
    pc.first_claim_date,
    COALESCE(pc.settled_claims, 0) AS settled_claims,
    COALESCE(pc.denied_claims, 0) AS denied_claims,
    COALESCE(pc.pending_claims, 0) AS pending_claims,
    
    -- Additional customer risk information
    cr.composite_risk_level,
    cr.customer_value_segment,
    
    -- Derived policy metrics
    CASE 
        WHEN COALESCE(pc.claim_count, 0) = 0 THEN 'No Claims'
        WHEN pc.claim_count = 1 THEN 'Single Claim'
        WHEN pc.claim_count BETWEEN 2 AND 3 THEN 'Multiple Claims'
        ELSE 'High Claims'
    END AS claim_frequency_category,
    
    -- Loss ratio
    CASE
        WHEN p.premium_amount > 0 
        THEN ROUND(COALESCE(pc.total_claim_amount, 0) / p.premium_amount, 2)
        ELSE 0
    END AS loss_ratio,
    
    -- Profitability assessment
    CASE
        WHEN p.premium_amount = 0 THEN 'Unknown'
        WHEN (COALESCE(pc.total_claim_amount, 0) / p.premium_amount) > 1 THEN 'Loss'
        WHEN (COALESCE(pc.total_claim_amount, 0) / p.premium_amount) > 0.7 THEN 'Marginal'
        WHEN (COALESCE(pc.total_claim_amount, 0) / p.premium_amount) > 0.5 THEN 'Moderate'
        ELSE 'Profitable'
    END AS profitability_category,
    
    -- Renewal recommendation
    CASE
        WHEN p.policy_status = 'Expired' THEN 'N/A'
        WHEN (COALESCE(pc.total_claim_amount, 0) / p.premium_amount) > 1.2 THEN 'Increase Premium'
        WHEN cr.composite_risk_level IN ('Very High', 'High') THEN 'Increase Premium'
        WHEN cr.composite_risk_level = 'Medium' AND (COALESCE(pc.total_claim_amount, 0) / p.premium_amount) > 0.7 THEN 'Review'
        WHEN cr.composite_risk_level IN ('Low', 'Very Low') AND (COALESCE(pc.total_claim_amount, 0) / p.premium_amount) < 0.5 THEN 'Discount'
        ELSE 'Standard Renewal'
    END AS renewal_recommendation
FROM policies_enriched p
LEFT JOIN policy_claims pc ON p.policy_id = pc.policy_id
LEFT JOIN customer_risk cr ON p.customer_id = cr.customer_id
