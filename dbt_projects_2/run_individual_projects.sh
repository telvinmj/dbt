#!/bin/bash

# Script to run all insurance dbt projects individually
# This will load data and run all dbt models in the correct order to establish cross-project dependencies
# Each project will be run from its own directory to ensure target files are created in the right place

set -e

echo "======= Insurance Analytics Projects - Individual Mode ======="
echo "Starting comprehensive run process..."

# Set working directory
cd "$(dirname "$0")"
BASE_DIR=$(pwd)

echo "Working directory: $BASE_DIR"
echo "Database will be created at: $BASE_DIR/insurance_data.db"

# Load data into DuckDB first
echo "Step 1: Loading seed data into DuckDB..."
python $BASE_DIR/load_data.py

# Install the project dependencies 
echo "Step 2: Installing project dependencies for each project..."

# Define the projects
PROJECTS=("claims_processing" "policy_management" "customer_risk")

for PROJECT in "${PROJECTS[@]}"; do
  echo "Installing dependencies for $PROJECT..."
  cd $BASE_DIR/$PROJECT
  dbt deps --profiles-dir=$BASE_DIR
done

# Run dbt seed for each project individually
echo "Step 3: Running dbt seed for all projects individually..."
for PROJECT in "${PROJECTS[@]}"; do
  echo "Running seed for $PROJECT..."
  cd $BASE_DIR/$PROJECT
  dbt seed --profiles-dir=$BASE_DIR
done

# Run staging and intermediate models for all projects individually
echo "Step 4: Running staging and intermediate models for all projects individually..."
for PROJECT in "${PROJECTS[@]}"; do
  echo "Running staging and intermediate models for $PROJECT..."
  cd $BASE_DIR/$PROJECT
  dbt run --profiles-dir=$BASE_DIR --select "staging intermediate"
done

# Run the mart models for each project in the correct order
echo "Step 5: Running mart models with cross-project dependencies..."

# First run customer_risk marts as they don't have external dependencies
echo "Running mart models for customer_risk..."
cd $BASE_DIR/customer_risk
dbt run --profiles-dir=$BASE_DIR --select "mart"

# Then run policy_management marts which depend on customer_risk
echo "Running mart models for policy_management..."
cd $BASE_DIR/policy_management
dbt run --profiles-dir=$BASE_DIR --select "mart"

# Finally run claims_processing marts which depend on policy_management
echo "Running mart models for claims_processing..."
cd $BASE_DIR/claims_processing
dbt run --profiles-dir=$BASE_DIR --select "mart"

# Generate documentation for each project
echo "Step 6: Generating documentation for each project..."
for PROJECT in "${PROJECTS[@]}"; do
  echo "Generating documentation for $PROJECT..."
  cd $BASE_DIR/$PROJECT
  dbt docs generate --profiles-dir=$BASE_DIR
done

echo "======= Run Complete ======="
echo "All projects have been successfully executed."
echo "Manifests and catalogs are now available in each project's target directory."

# Verify the target directories
echo ""
echo "Verifying target directories:"
for PROJECT in "${PROJECTS[@]}"; do
  if [ -d "$BASE_DIR/$PROJECT/target" ]; then
    MANIFEST="$BASE_DIR/$PROJECT/target/manifest.json"
    if [ -f "$MANIFEST" ]; then
      echo "✅ $PROJECT: target directory and manifest.json exist"
    else
      echo "❌ $PROJECT: target directory exists but manifest.json not found"
    fi
  else
    echo "❌ $PROJECT: target directory not found"
  fi
done 