{{
    config(
        materialized='view',
        tags=['intermediate', 'policies', 'daily']
    )
}}

WITH policies AS (
    SELECT * FROM {{ ref('stg_policies') }}
),

agents AS (
    SELECT * FROM {{ ref('stg_agents') }}
)

SELECT
    p.policy_id,
    p.customer_id,
    p.policy_type,
    p.start_date,
    p.end_date,
    p.premium_amount,
    p.coverage_amount,
    p.status,
    p.agent_id,
    p.policy_number,
    p.policy_term_days,
    p.effective_status,
    p.coverage_premium_ratio,
    -- Agent information
    a.agent_name,
    a.office_location,
    a.specialization AS agent_specialization,
    a.experience_level AS agent_experience,
    -- Policy-agent alignment
    CASE
        WHEN a.specialization = p.policy_type THEN 'ALIGNED'
        ELSE 'MISALIGNED'
    END AS specialization_alignment,
    -- Metadata fields
    p.dbt_updated_at,
    p._dbt_source_project
FROM policies p
LEFT JOIN agents a ON p.agent_id = a.agent_id
