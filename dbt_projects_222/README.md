# Insurance Analytics dbt Projects

This folder contains three interconnected dbt projects in the insurance domain, designed to demonstrate cross-project dependencies and data lineage for a unified data schema UI visualization.

## Projects Overview

1. **Claims Processing**
   - Analyzes insurance claims data
   - Tracks adjusters' performance
   - Links with policy information
   - Models follow claims lifecycle from inception to settlement

2. **Policy Management**
   - Manages insurance policies
   - Tracks agent performance
   - Integrates customer risk data
   - Adjusts premiums based on risk factors

3. **Customer Risk**
   - Evaluates customer risk profiles
   - Combines demographic and historical data
   - Incorporates claims history
   - Provides risk scoring for policy management

## Cross-Project Dependencies

The projects demonstrate several cross-project dependencies:

- **Customer Risk → Policy Management**: Risk scores inform policy premium adjustments
- **Policy Management → Claims Processing**: Policy details enrich claims analysis
- **Claims Processing → Customer Risk**: Claims history informs risk assessment

## Project Structure

Each project follows a modern dbt project structure:

```
project_name/
├── models/
│   ├── staging/       # Clean, typed data from source
│   ├── intermediate/  # Business logic transformations
│   └── mart/          # Final presentation layer with cross-project joins
├── seeds/             # Static CSV data
├── dbt_project.yml    # Project configuration
```

## Getting Started

### Prerequisites

- dbt-core
- Python 3.7+
- DuckDB
- pandas

### Setup and Execution

1. **Load Seed Data**:
   ```
   python dbt_projects_2/load_data.py
   ```

2. **Run All Projects**:
   ```
   ./dbt_projects_2/run_all_projects.sh
   ```

This will execute all three projects in the correct order to establish dependencies and generate documentation.

## Using for UI Development

After running the projects, you'll find:
- Manifest files in each project's target directory
- Catalog files with schema information
- Documentation sites for each project

These files are the foundation for building a UI that visualizes the unified data schema across projects.

# DBT Projects Configuration

This directory contains multiple dbt projects (claims_processing, policy_management, and customer_risk) that share a common `profiles.yml` file and SQLite database.

## Project Structure

- `claims_processing/` - DBT project for claims processing models
- `policy_management/` - DBT project for policy management models
- `customer_risk/` - DBT project for customer risk assessment models
- `profiles.yml` - Contains connection profiles for all projects
- `run_dbt.sh` - Helper script to run dbt commands

## Profiles

The `profiles.yml` file in this directory contains profiles for all three projects:

- `claims_processing`
- `policy_management`
- `customer_risk`

Each profile points to the same SQLite database (`insurance_data.db`).

## Running DBT Commands

### Option 1: Using the helper script

The easiest way to run dbt commands is using the `run_dbt.sh` script:

```bash
# Run models in the claims_processing project
./run_dbt.sh claims_processing run

# Generate docs for the policy_management project
./run_dbt.sh policy_management docs generate

# Test models in the customer_risk project
./run_dbt.sh customer_risk test
```

### Option 2: Running dbt directly

You can also run dbt commands directly by specifying the profiles directory:

```bash
# Change to the project directory
cd claims_processing

# Run dbt with the profiles directory
dbt run --profiles-dir ..

# Or for docs
dbt docs generate --profiles-dir ..
dbt docs serve --profiles-dir ..
```

## Working with Multiple Projects

Each project has its own profile specified in its `dbt_project.yml` file. This allows you to:

1. Run each project independently using its correct profile
2. Keep all connection settings in one central `profiles.yml` file
3. Share common database connections between projects

## Metadata Explorer Integration

If you're using the dbt Metadata Explorer, it will automatically parse all projects' metadata and combine them into a unified view.