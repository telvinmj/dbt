{{
    config(
        materialized='table',
        tags=['mart', 'customers', 'risk', 'daily']
    )
}}

WITH customer_risk_enriched AS (
    SELECT * FROM {{ ref('int_customer_risk_enriched') }}
),

-- Reference to claims data from claims processing project
customer_claims AS (
    {% if execute %}
        {% if adapter.get_relation(this.database, 'mart', 'mart_claims_analysis') %}
            SELECT 
                customer_id,
                COUNT(*) AS total_claims,
                SUM(claim_amount) AS total_claim_amount,
                SUM(settlement_amount_clean) AS total_settlement_amount,
                AVG(days_to_settle) AS avg_days_to_settle,
                SUM(CASE WHEN claim_status = 'SETTLED' THEN 1 ELSE 0 END) AS settled_claims_count,
                SUM(CASE WHEN claim_status = 'DENIED' THEN 1 ELSE 0 END) AS denied_claims_count,
                MAX(claim_date) AS most_recent_claim_date,
                'claims_processing' AS _dbt_source_project
            FROM {{ ref('claims_processing', 'mart_claims_analysis') }}
            GROUP BY customer_id
        {% else %}
            SELECT
                'CU0000' AS customer_id,
                0 AS total_claims,
                0 AS total_claim_amount,
                0 AS total_settlement_amount,
                0 AS avg_days_to_settle,
                0 AS settled_claims_count,
                0 AS denied_claims_count,
                CAST('2000-01-01' AS DATE) AS most_recent_claim_date,
                'claims_processing' AS _dbt_source_project
            WHERE 1=0
        {% endif %}
    {% else %}
        SELECT
            'CU0000' AS customer_id,
            0 AS total_claims,
            0 AS total_claim_amount,
            0 AS total_settlement_amount,
            0 AS avg_days_to_settle,
            0 AS settled_claims_count,
            0 AS denied_claims_count,
            CAST('2000-01-01' AS DATE) AS most_recent_claim_date,
            'claims_processing' AS _dbt_source_project
        WHERE 1=0
    {% endif %}
)

SELECT
    cr.customer_id,
    cr.customer_name,
    cr.email,
    cr.city,
    cr.state,
    cr.age,
    cr.months_as_customer,
    cr.credit_score,
    cr.credit_rating,
    cr.claim_frequency,
    cr.risk_score,
    cr.age_adjusted_risk_score,
    cr.previous_claims_count,
    cr.risk_category,
    cr.customer_segment,
    -- Claims information from claims processing
    cc.total_claims,
    cc.total_claim_amount,
    cc.total_settlement_amount,
    cc.avg_days_to_settle,
    cc.settled_claims_count,
    cc.denied_claims_count,
    cc.most_recent_claim_date,
    -- Risk scoring with claim data
    CASE
        WHEN cc.total_claims > 0 THEN
            cr.age_adjusted_risk_score * (1 + (cc.total_claims / 10))
        ELSE
            cr.age_adjusted_risk_score
    END AS claims_adjusted_risk_score,
    -- Denial ratio
    CASE
        WHEN cc.total_claims > 0 THEN 
            ROUND(cc.denied_claims_count / cc.total_claims * 100, 2)
        ELSE 0
    END AS claim_denial_rate,
    -- Cross project attribution
    cr._dbt_source_project AS risk_source,
    cc._dbt_source_project AS claims_source,
    -- Metadata
    CURRENT_TIMESTAMP AS dbt_updated_at
FROM customer_risk_enriched cr
LEFT JOIN customer_claims cc ON cr.customer_id = cc.customer_id
