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
    CAST(assessment_date AS DATE) AS assessment_date,
    credit_score,
    claim_frequency,
    risk_score,
    previous_claims_count,
    risk_category,
    CAST(last_assessment AS DATE) AS last_assessment,
    assessment_source,
    -- Derived fields
    DATEDIFF('day', last_assessment, assessment_date) AS days_since_last_assessment,
    CASE
        WHEN credit_score >= 750 THEN 'EXCELLENT'
        WHEN credit_score >= 700 THEN 'GOOD'
        WHEN credit_score >= 650 THEN 'FAIR'
        WHEN credit_score >= 600 THEN 'POOR'
        ELSE 'VERY_POOR'
    END AS credit_rating,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'customer_risk' AS _dbt_source_project
FROM source
