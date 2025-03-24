with claims as (
    select * from {{ ref('stg_claims') }}
),

adjusters as (
    select * from {{ ref('stg_adjusters') }}
),

-- Reference cross-project models using the full project path
customers as (
    select * from {{ ref('customer_risk', 'stg_customers') }}
)

select
    c.claim_id,
    c.policy_id,
    c.customer_id,
    c.adjuster_id,
    c.claim_date,
    c.incident_date,
    c.settlement_date,
    c.claim_amount,
    c.settlement_amount,
    c.claim_status,
    c.claim_type,
    c.claim_adjustment,
    c.days_to_close,
    -- Adjuster information
    a.adjuster_name,
    a.department as adjuster_department,
    a.specialty as adjuster_specialty,
    a.years_experience,
    a.experience_level,
    a.is_active as adjuster_active,
    -- Customer information
    cust.full_name as customer_name,
    cust.state as customer_state,
    cust.age as customer_age,
    
    -- Additional derived metrics
    case
        when c.settlement_amount > c.claim_amount then 'Over'
        when c.settlement_amount < c.claim_amount then 'Under'
        when c.settlement_amount = c.claim_amount then 'Exact'
        else 'Pending'
    end as settlement_classification,
    
    case
        when c.days_to_close <= 7 then 'Fast'
        when c.days_to_close <= 30 then 'Normal'
        when c.days_to_close <= 90 then 'Slow'
        else 'Very Slow'
    end as resolution_speed
from claims c
left join adjusters a on c.adjuster_id = a.adjuster_id
left join customers cust on c.customer_id = cust.customer_id
