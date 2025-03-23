{{
    config(
        materialized='view',
        tags=['staging', 'policies', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ ref('policies') }}
)

SELECT
    policy_id,
    customer_id,
    policy_type,
    CAST(start_date AS DATE) AS start_date,
    CAST(end_date AS DATE) AS end_date,
    premium_amount,
    coverage_amount,
    status,
    agent_id,
    policy_number,
    -- Derived fields
    DATEDIFF('day', start_date, end_date) AS policy_term_days,
    CASE
        WHEN CURRENT_DATE() > end_date THEN 'EXPIRED'
        WHEN CURRENT_DATE() BETWEEN start_date AND end_date THEN status
        WHEN CURRENT_DATE() < start_date THEN 'FUTURE'
        ELSE 'UNKNOWN'
    END AS effective_status,
    ROUND(coverage_amount / premium_amount, 2) AS coverage_premium_ratio,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'policy_management' AS _dbt_source_project
FROM source
