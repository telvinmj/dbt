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