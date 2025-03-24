{{
    config(
        materialized='view',
        tags=['intermediate', 'customers', 'risk', 'daily']
    )
}}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

risk_factors AS (
    SELECT * FROM {{ ref('stg_risk_factors') }}
),

-- Get the most recent risk assessment for each customer
latest_risk AS (
    SELECT
        customer_id,
        max(assessment_date) as latest_assessment_date
    FROM risk_factors
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.phone,
    c.address,
    c.city,
    c.state,
    c.zip_code,
    c.date_of_birth,
    c.gender,
    c.joining_date,
    c.age,
    c.months_as_customer,
    -- Risk information
    r.risk_id,
    r.assessment_date,
    r.credit_score,
    r.claim_frequency,
    r.risk_score,
    r.previous_claims_count,
    r.risk_category,
    r.risk_level,
    r.last_assessment,
    r.assessment_source,
    -- Additional derived metrics
    CASE
        WHEN c.age < 25 THEN 'High'
        WHEN c.age BETWEEN 25 AND 65 THEN 'Medium'
        ELSE 'Low'
    END AS age_risk_category,
    
    CASE
        WHEN r.previous_claims_count = 0 THEN 'No Claims'
        WHEN r.previous_claims_count = 1 THEN 'Low'
        WHEN r.previous_claims_count BETWEEN 2 AND 3 THEN 'Medium'
        ELSE 'High'
    END AS claims_history_risk,
    
    CASE
        WHEN r.credit_score >= 750 THEN 'Excellent'
        WHEN r.credit_score >= 700 THEN 'Good'
        WHEN r.credit_score >= 650 THEN 'Fair'
        WHEN r.credit_score >= 600 THEN 'Poor'
        ELSE 'Very Poor'
    END AS credit_rating,
    
    -- Calculate overall risk score weighted by different factors
    (r.risk_score * 0.5) + 
    (CASE 
        WHEN c.age < 25 THEN 100
        WHEN c.age BETWEEN 25 AND 65 THEN 50
        ELSE 25
     END * 0.3) +
    (r.previous_claims_count * 50 * 0.2) AS weighted_risk_score
FROM customers c
LEFT JOIN latest_risk lr ON c.customer_id = lr.customer_id
LEFT JOIN risk_factors r ON c.customer_id = r.customer_id AND r.assessment_date = lr.latest_assessment_date
