{{
  config(
    materialized = 'table',
    schema = 'marts'
  )
}}

WITH stg_customer AS (
    SELECT * FROM {{ ref('stg_customer', 'customer_project') }}
),

customer_dim AS (
    SELECT
        customer_id,
        first_name,
        last_name,
        CONCAT(first_name, ' ', last_name) AS full_name,
        email,
        phone_number,
        address,
        city,
        state,
        zip_code,
        date_of_birth,
        gender,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) AS age,
        created_at,
        updated_at
    FROM stg_customer
)

SELECT * FROM customer_dim 