# Customer Project

This DBT project contains models for customer data in the insurance domain. It serves as the foundation for the policy and claims projects.

## Overview

The Customer Project includes:

- Staging models for transforming raw customer data
- Dimension models for business reporting
- Source definitions and seed data for testing

## Data Flow

```
raw_insurance.customers (source/seed)
         ↓
  stg_customer (staging)
         ↓
  dim_customer (marts)
```

## Models

### Staging

- `stg_customer.sql` - Transforms raw customer data and applies basic formatting

### Marts

- `dim_customer.sql` - Creates a dimension table with customer attributes and derived fields

## Dependencies

The Customer Project is a foundational project that doesn't depend on other projects. However, it is used by:

- Policy Project
- Claims Project

## Usage

### Running the project

```bash
# From the customer_project directory
dbt run --profiles-dir=.

# Or using the project scripts
../scripts/run_customer.sh
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

This project uses the `customer_profile` profile, which can be configured either in:

- `./profiles.yml` (local to the project)
- `../.dbt/profiles.yml` (central configuration) 