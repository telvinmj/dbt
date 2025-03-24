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
    start_date::date as start_date,
    end_date::date as end_date,
    premium_amount::float as premium_amount,
    coverage_amount::float as coverage_amount,
    status,
    agent_id,
    policy_number,
    -- Add derived fields
    case 
        when end_date < current_date then 'Expired'
        when status = 'ACTIVE' then 'Active'
        else 'Inactive' 
    end as policy_status,
    datediff('month', start_date, coalesce(end_date, current_date)) as policy_tenure_months,
    coverage_amount / premium_amount as coverage_premium_ratio,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'policy_management' AS _dbt_source_project
FROM source
