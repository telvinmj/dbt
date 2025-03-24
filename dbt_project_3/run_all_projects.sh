#!/bin/bash
set -e  # Exit on error

echo "====== RUNNING INSURANCE PROJECTS ======"
echo "Loading seed data and running DBT projects in dependency order"

# Project base directory
BASE_DIR="/Users/telvin/Desktop/dbt/dbt_project_3"

# Step 1: Load Seed Data
echo "====== STEP 1: LOADING SEED DATA ======"

echo "Loading Customer Project seed data..."
cd "$BASE_DIR/customer_project"
dbt deps --profiles-dir=.
dbt seed --profiles-dir=.

echo "Loading Policy Project seed data..."
cd "$BASE_DIR/policy_project"
dbt deps --profiles-dir=.
dbt seed --profiles-dir=.

echo "Loading Claims Project seed data..."
cd "$BASE_DIR/claims_project"
dbt deps --profiles-dir=.
dbt seed --profiles-dir=.

# Step 2: Run Projects in dependency order
echo "====== STEP 2: RUNNING DBT MODELS ======"

echo "Running Customer Project models..."
cd "$BASE_DIR/customer_project"
dbt run --profiles-dir=.

echo "Running Policy Project models..."
cd "$BASE_DIR/policy_project"
dbt run --profiles-dir=.

echo "Running Claims Project models..."
cd "$BASE_DIR/claims_project"
dbt run --profiles-dir=.

echo "====== ALL PROJECTS COMPLETED ======"

# Optional: Generate docs for all projects
# echo "Generating documentation..."
# cd "$BASE_DIR/customer_project"
# dbt docs generate --profiles-dir=.
# cd "$BASE_DIR/policy_project"
# dbt docs generate --profiles-dir=.
# cd "$BASE_DIR/claims_project"
# dbt docs generate --profiles-dir=.
# dbt docs serve --profiles-dir=. 