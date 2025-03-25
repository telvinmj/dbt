
  create view "dbt_sample"."my_test"."my_second_dbt_model__dbt_tmp"
    
    
  as (
    -- Use the `ref` function to select from other models

select *
from "dbt_sample"."my_test_my_test"."my_first_dbt_model"
where id = 1
  );