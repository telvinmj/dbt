
  create view "dbt_sample"."my_test"."stg_campaigns__dbt_tmp"
    
    
  as (
    -- models/example/stg_campaigns.sql
SELECT
    campaign_id,
    campaign_name,
    start_date,
    end_date,
    budget
FROM public.raw_campaigns
  );