with source as (
    select * from {{ ref('adjusters') }}
)

select
    adjuster_id,
    adjuster_name,
    adjuster_email,
    department,
    specialty,
    years_experience::int as years_experience,
    active::boolean as is_active,
    -- Add derived fields
    case 
        when years_experience >= 5 then 'Senior'
        when years_experience >= 2 then 'Mid-level'
        else 'Junior'
    end as experience_level
from source
