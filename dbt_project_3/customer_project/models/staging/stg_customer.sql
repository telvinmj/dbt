{{
  config(
    materialized = 'view',
    schema = 'staging'
  )
}}

WITH source_data AS (
    SELECT 
        customer_id,
        first_name,
        last_name,
        email,
        phone_number,
        address,
        city,
        state,
        zip_code,
        date_of_birth,
        gender,
        created_at,
        updated_at
    FROM {{ ref('raw_customers') }}
)

SELECT 
    customer_id,
    first_name,
    last_name,
    email,
    phone_number,
    address,
    city,
    state,
    zip_code,
    date_of_birth,
    gender,
    created_at,
    updated_at
FROM source_data 