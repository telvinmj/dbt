{{
    config(
        materialized='view',
        tags=['staging', 'agents', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ ref('agents') }}
)

SELECT
    agent_id,
    agent_name,
    email,
    phone,
    office_location,
    hire_date::date as hire_date,
    termination_date::date as termination_date,
    commission_rate::float as commission_rate,
    active::boolean as is_active,
    -- Add derived fields
    CASE
        WHEN termination_date is null and active = TRUE then 'Active'
        WHEN termination_date is not null then 'Terminated'
        ELSE 'Inactive'
    END AS agent_status,
    datediff('month', hire_date, coalesce(termination_date, current_date)) as tenure_months,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'policy_management' AS _dbt_source_project
FROM source
