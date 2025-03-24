{{
    config(
        materialized='view',
        tags=['staging', 'customers', 'daily']
    )
}}

WITH source AS (
    SELECT * FROM {{ ref('customers') }}
)

SELECT
    customer_id,
    first_name,
    last_name,
    first_name || ' ' || last_name as full_name,
    email,
    phone,
    address,
    city,
    state,
    zip_code,
    date_of_birth::date as date_of_birth,
    gender,
    joining_date::date as joining_date,
    -- Add derived fields
    datediff('year', date_of_birth, current_date) as age,
    datediff('month', joining_date, current_date) as months_as_customer,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'customer_risk' AS _dbt_source_project
FROM source
