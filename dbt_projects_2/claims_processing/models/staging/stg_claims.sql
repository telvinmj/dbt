with source as (
    select * from {{ ref('claims') }}
)

select
    claim_id,
    policy_id,
    customer_id,
    adjuster_id,
    claim_date::date as claim_date,
    incident_date::date as incident_date,
    settlement_date::date as settlement_date,
    claim_amount::float as claim_amount,
    settlement_amount::float as settlement_amount,
    claim_status,
    claim_type,
    -- Add derived fields
    case 
        when settlement_amount is not null 
        then settlement_amount - claim_amount 
        else 0 
    end as claim_adjustment,
    case 
        when settlement_date is not null 
        then datediff('day', claim_date, settlement_date)
        else datediff('day', claim_date, current_date) 
    end as days_to_close
from source
