# DBT Project 3: Multi-Project Insurance Data Warehouse

This repository contains a set of DBT projects for an insurance data warehouse with cross-project references and dependencies. The projects model insurance data including customers, policies, and claims.

## Project Structure

The repository consists of three interconnected DBT projects:

1. **Customer Project** - Core customer data models
2. **Policy Project** - Insurance policy data (depends on Customer Project)
3. **Claims Project** - Insurance claims data (depends on both Customer and Policy Projects)

Each project has its own DBT project configuration, profile, and models, but they are designed to work together with cross-project references.

## Dependencies

The projects have the following dependency hierarchy:

```
customer_project <-- policy_project <-- claims_project
```

This means:
- Customer Project is standalone
- Policy Project references models from Customer Project
- Claims Project references models from both Customer Project and Policy Project

## Getting Started

### Prerequisites

- DBT Core installed (v1.0.0 or later)
- DuckDB (no separate installation needed as it's embedded)
- Python 3.8+ (for DBT Core)
- dbt-duckdb adapter installed (`pip install dbt-duckdb`)

### Setup

1. Configure the database connection in the profiles for each project:
   - `.dbt/profiles.yml` (central configuration)
   - Or individual `profiles.yml` in each project directory

2. Install dependencies for each project:
   ```bash
   cd customer_project
   dbt deps
   
   cd ../policy_project
   dbt deps
   
   cd ../claims_project
   dbt deps
   ```

### Running the Projects

Run the projects in the correct dependency order:

```bash
# Run all projects in sequence
./scripts/run_all.sh

# Or run individual projects
./scripts/run_customer.sh
./scripts/run_policy.sh
./scripts/run_claims.sh
```

## Project Details

### Customer Project

Contains models for customer data management:
- Staging models for raw customer data
- Customer dimension table with derived attributes

### Policy Project

Contains models for insurance policies:
- Staging models for raw policy data
- Policy fact table with customer attributes joined from Customer Project

### Claims Project

Contains models for insurance claims:
- Staging models for raw claims data
- Claims fact table with references to both customers and policies

## Cross-Project References

The projects use DBT's cross-project referencing capabilities:

```sql
-- Example: Policy project referencing Customer project
SELECT * FROM {{ ref('dim_customer', 'customer_project') }}

-- Example: Claims project referencing Policy project
SELECT * FROM {{ ref('fct_policy', 'policy_project') }}
```

## Artifacts

When the projects are run, they generate:
- `manifest.json` - Contains metadata about the models and their dependencies
- `catalog.json` - Contains information about the database objects created by the models
- Documentation site - Generated with `dbt docs generate` and viewable with `dbt docs serve`

## Customization

You can customize the database connection details in the profiles.yml files based on your environment. Each project uses DuckDB with separate database files stored in the `data` directory:

- `data/insurance_customers.duckdb` - For customer data
- `data/insurance_policies.duckdb` - For policy data
- `data/insurance_claims.duckdb` - For claims data

## Seed Data

Sample seed data is provided for testing purposes:
- `customer_project/seeds/raw_customers.csv`
- `policy_project/seeds/raw_policies.csv`
- `claims_project/seeds/raw_claims.csv`

Load the seed data with:
```bash
dbt seed --profiles-dir=.dbt --project-dir=customer_project
dbt seed --profiles-dir=.dbt --project-dir=policy_project
dbt seed --profiles-dir=.dbt --project-dir=claims_project
``` 