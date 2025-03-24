# Claims Project

This DBT project contains models for insurance claims data in the insurance domain. It depends on both the Customer Project and Policy Project for data.

## Overview

The Claims Project includes:

- Staging models for transforming raw claims data
- Fact models for business reporting with customer and policy attributes
- Source definitions and seed data for testing
- Cross-project references to both Customer and Policy projects

## Data Flow

```
raw_insurance.claims (source/seed)    customer_project.dim_customer    policy_project.fct_policy
         ↓                                        ↓                            ↓
  stg_claim (staging)                             |                            |
         ↓                                        |                            |
  fct_claim (marts) <------------------------------------------------------>
```

## Models

### Staging

- `stg_claim.sql` - Transforms raw claims data and applies basic formatting

### Marts

- `fct_claim.sql` - Creates a fact table with claims attributes and joined customer and policy data

## Dependencies

The Claims Project depends on:

- Customer Project (for customer dimension data)
- Policy Project (for policy fact data)

## Usage

### Running the project

```bash
# From the claims_project directory
dbt run --profiles-dir=.

# Or using the project scripts
../scripts/run_claims.sh
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

This project uses the `claims_profile` profile, which can be configured either in:

- `./profiles.yml` (local to the project)
- `../.dbt/profiles.yml` (central configuration)

## Cross-Project References

This project references models from both the Customer and Policy projects using the following syntax:

```sql
-- Examples from fct_claim.sql
SELECT * FROM {{ ref('dim_customer', 'customer_project') }}
SELECT * FROM {{ ref('fct_policy', 'policy_project') }}
```