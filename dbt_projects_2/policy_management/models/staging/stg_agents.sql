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
    agent_email,
    office_location,
    years_experience,
    specialization,
    active,
    -- Derived fields
    CASE 
        WHEN years_experience >= 10 THEN 'SENIOR'
        WHEN years_experience >= 5 THEN 'MID'
        ELSE 'JUNIOR'
    END AS experience_level,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'policy_management' AS _dbt_source_project
FROM source
