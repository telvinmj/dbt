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
    email,
    phone,
    address,
    city,
    state,
    zip_code,
    CAST(date_of_birth AS DATE) AS date_of_birth,
    gender,
    CAST(joining_date AS DATE) AS joining_date,
    -- Derived fields
    CONCAT(first_name, ' ', last_name) AS customer_name,
    DATEDIFF('year', date_of_birth, CURRENT_DATE()) AS age,
    DATEDIFF('month', joining_date, CURRENT_DATE()) AS months_as_customer,
    -- Metadata fields
    CURRENT_TIMESTAMP AS dbt_updated_at,
    'customer_risk' AS _dbt_source_project
FROM source
