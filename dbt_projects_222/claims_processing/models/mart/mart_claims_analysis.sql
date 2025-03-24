with claims_enriched as (
    select * from {{ ref('int_claims_enriched') }}
),

-- Reference cross-project models
policies as (
    select * from {{ ref('policy_management', 'stg_policies') }}
),

-- Group claims by adjusters for performance metrics
adjuster_performance as (
    select
        adjuster_id,
        adjuster_name,
        adjuster_department,
        adjuster_specialty,
        count(*) as claims_handled,
        avg(days_to_close) as avg_days_to_close,
        sum(case when claim_status = 'SETTLED' then 1 else 0 end) as claims_settled,
        sum(case when claim_status = 'PENDING' then 1 else 0 end) as claims_pending,
        sum(case when claim_status = 'DENIED' then 1 else 0 end) as claims_denied,
        sum(claim_amount) as total_claim_amount,
        sum(settlement_amount) as total_settlement_amount,
        avg(settlement_amount / nullif(claim_amount, 0)) as avg_settlement_ratio
    from claims_enriched
    group by 1, 2, 3, 4
),

-- Calculate claim statistics by policy type
policy_claims as (
    select
        p.policy_type,
        count(*) as claim_count,
        avg(c.claim_amount) as avg_claim_amount,
        sum(c.claim_amount) as total_claim_amount,
        sum(c.settlement_amount) as total_settlement_amount,
        avg(c.days_to_close) as avg_resolution_time
    from claims_enriched c
    join policies p on c.policy_id = p.policy_id
    group by 1
)

select
    c.*,
    
    -- Include adjuster performance metrics
    ap.claims_handled as adjuster_claims_handled,
    ap.avg_days_to_close as adjuster_avg_days_to_close,
    ap.claims_settled as adjuster_claims_settled,
    ap.claims_pending as adjuster_claims_pending,
    ap.claims_denied as adjuster_claims_denied,
    ap.total_claim_amount as adjuster_total_claim_amount,
    ap.total_settlement_amount as adjuster_total_settlement_amount,
    ap.avg_settlement_ratio as adjuster_avg_settlement_ratio,
    
    -- Performance metrics
    case
        when ap.avg_days_to_close < 15 then 'Excellent'
        when ap.avg_days_to_close < 30 then 'Good'
        when ap.avg_days_to_close < 60 then 'Average'
        else 'Poor'
    end as adjuster_performance_rating,
    
    -- Compare claim to average for policy type
    pc.avg_claim_amount as policy_type_avg_claim,
    round(c.claim_amount / nullif(pc.avg_claim_amount, 0), 2) as claim_to_avg_ratio,
    
    -- Claim cost analysis
    case
        when c.claim_amount > (pc.avg_claim_amount * 1.5) then 'High Cost'
        when c.claim_amount < (pc.avg_claim_amount * 0.5) then 'Low Cost'
        else 'Average Cost'
    end as claim_cost_category
from claims_enriched c
left join adjuster_performance ap on c.adjuster_id = ap.adjuster_id
left join policies p on c.policy_id = p.policy_id
left join policy_claims pc on p.policy_type = pc.policy_type
