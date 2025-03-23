#!/bin/bash

# Script to run all insurance dbt projects
# This will load data and run all dbt models in the correct order to establish cross-project dependencies

set -e

echo "======= Insurance Analytics Projects ======="
echo "Starting comprehensive run process..."

# Set working directory
cd "$(dirname "$0")"
BASE_DIR=$(pwd)
export DBT_PROJECT_DIR=$BASE_DIR

echo "Working directory: $BASE_DIR"
echo "Database will be created at: $BASE_DIR/insurance_data.db"

# Load data into DuckDB first
echo "Step 1: Loading seed data into DuckDB..."
python $BASE_DIR/load_data.py

# Install the project dependencies first
echo "Step 2: Installing project dependencies..."
cd $BASE_DIR
dbt deps --profiles-dir=$BASE_DIR

# Run dbt seed for all projects in one go from the root project
echo "Step 3: Running dbt seed for all projects..."
cd $BASE_DIR
dbt seed --profiles-dir=$BASE_DIR --select claims_processing policy_management customer_risk

# Run staging and intermediate models for all projects
echo "Step 4: Running staging and intermediate models for all projects..."
cd $BASE_DIR
dbt run --profiles-dir=$BASE_DIR --select "claims_processing.staging claims_processing.intermediate policy_management.staging policy_management.intermediate customer_risk.staging customer_risk.intermediate"

# Run the mart models for each project in the correct order
echo "Step 5: Running mart models with cross-project dependencies..."

# First run customer_risk marts as they don't have external dependencies
echo "Running mart models for customer_risk..."
cd $BASE_DIR
dbt run --profiles-dir=$BASE_DIR --select "customer_risk.mart"

# Then run policy_management marts which depend on customer_risk
echo "Running mart models for policy_management..."
cd $BASE_DIR
dbt run --profiles-dir=$BASE_DIR --select "policy_management.mart"

# Finally run claims_processing marts which depend on policy_management
echo "Running mart models for claims_processing..."
cd $BASE_DIR
dbt run --profiles-dir=$BASE_DIR --select "claims_processing.mart"

# Generate documentation
echo "Step 6: Generating documentation..."
cd $BASE_DIR
dbt docs generate --profiles-dir=$BASE_DIR

echo "======= Run Complete ======="
echo "All projects have been successfully executed."
echo "Manifests and catalogs are now available for UI exploration." 