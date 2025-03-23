{{
    config(
        materialized='table',
        tags=['mart', 'policies', 'daily']
    )
}}

WITH policies_enriched AS (
    SELECT * FROM {{ ref('int_policies_enriched') }}
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
    pe.policy_id,
    pe.customer_id,
    pe.policy_type,
    pe.start_date,
    pe.end_date,
    pe.premium_amount,
    pe.coverage_amount,
    pe.status,
    pe.agent_id,
    pe.policy_number,
    pe.policy_term_days,
    pe.effective_status,
    pe.coverage_premium_ratio,
    pe.agent_name,
    pe.office_location,
    pe.agent_specialization,
    pe.agent_experience,
    pe.specialization_alignment,
    -- Customer risk information
    cr.customer_name,
    cr.risk_category,
    cr.risk_score,
    cr.credit_score,
    cr.claim_frequency,
    cr.previous_claims_count,
    -- Risk-adjusted premium calculation
    CASE
        WHEN cr.risk_category = 'HIGH_RISK' THEN pe.premium_amount * 1.25
        WHEN cr.risk_category = 'MEDIUM_RISK' THEN pe.premium_amount * 1.1
        WHEN cr.risk_category = 'LOW_RISK' THEN pe.premium_amount * 0.95
        ELSE pe.premium_amount
    END AS risk_adjusted_premium,
    -- Cross project attribution
    pe._dbt_source_project AS policy_source,
    cr._dbt_source_project AS risk_source,
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM policies_enriched pe
LEFT JOIN customer_risk_profile cr ON pe.customer_id = cr.customer_id
