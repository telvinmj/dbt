{{
    config(
        materialized='view',
        tags=['staging', 'risk', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ ref('risk_factors') }}
)

SELECT
    risk_id,
    customer_id,
    assessment_date::date as assessment_date,
    credit_score::int as credit_score,
    claim_frequency::float as claim_frequency,
    risk_score::float as risk_score,
    previous_claims_count::int as previous_claims_count,
    risk_category,
    last_assessment::date as last_assessment,
    assessment_source,
    -- Add derived fields
    case
        when risk_score >= 800 then 'Very High Risk'
        when risk_score >= 600 then 'High Risk'
        when risk_score >= 400 then 'Medium Risk'
        when risk_score >= 200 then 'Low Risk'
        else 'Very Low Risk'
    end as risk_level,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'customer_risk' AS _dbt_source_project
FROM source
