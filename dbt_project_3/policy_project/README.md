# Policy Project

This DBT project contains models for insurance policy data in the insurance domain. It depends on the Customer Project for customer information.

## Overview

The Policy Project includes:

- Staging models for transforming raw policy data
- Fact models for business reporting with customer attributes
- Source definitions and seed data for testing
- Cross-project references to the Customer Project

## Data Flow

```
raw_insurance.policies (source/seed)    customer_project.dim_customer
         ↓                                        ↓
  stg_policy (staging)                            |
         ↓                                        |
  fct_policy (marts) <---------------------------->
```

## Models

### Staging

- `stg_policy.sql` - Transforms raw policy data and applies basic formatting

### Marts

- `fct_policy.sql` - Creates a fact table with policy attributes and joined customer data

## Dependencies

The Policy Project depends on:

- Customer Project (for customer dimension data)

And is used by:

- Claims Project

## Usage

### Running the project

```bash
# From the policy_project directory
dbt run --profiles-dir=.

# Or using the project scripts
../scripts/run_policy.sh
```

### Loading seed data

```bash
dbt seed --profiles-dir=.
```

### Testing

```bash
dbt test --profiles-dir=.
```

### Documentation

```bash
dbt docs generate --profiles-dir=.
dbt docs serve --profiles-dir=.
```

## Profile Configuration

This project uses the `policy_profile` profile, which can be configured either in:

- `./profiles.yml` (local to the project)
- `../.dbt/profiles.yml` (central configuration)

## Cross-Project References

This project references models from the Customer Project using the following syntax:

```sql
-- Example from fct_policy.sql
SELECT * FROM {{ ref('dim_customer', 'customer_project') }}
```