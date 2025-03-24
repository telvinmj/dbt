#!/bin/bash

# Set root directory
ROOT_DIR=$(dirname $(dirname $(realpath $0)))
PROJECT_NAME="claims_project"
PROJECT_DIR="$ROOT_DIR/$PROJECT_NAME"

echo "----------------------------------------"
echo "Running DBT project: $PROJECT_NAME"
echo "Project directory: $PROJECT_DIR"
echo "----------------------------------------"

# Change to the project directory
cd "$PROJECT_DIR"

# Run DBT using the specific profile
if [ -f "./profiles.yml" ]; then
    echo "Using local profiles.yml"
    PROFILE_PATH="./profiles.yml"
else
    echo "Using global profiles.yml"
    PROFILE_PATH="$ROOT_DIR/.dbt/profiles.yml"
fi

# Clean dbt_packages directory if it exists
if [ -d "dbt_packages" ]; then
    echo "Cleaning existing dbt_packages directory..."
    rm -rf dbt_packages
fi

# Run dbt commands
echo "Running dbt deps..."
dbt deps --profiles-dir $(dirname $PROFILE_PATH)

echo "Running dbt seed..."
dbt seed --profiles-dir $(dirname $PROFILE_PATH)

echo "Running dbt run..."
dbt run --profiles-dir $(dirname $PROFILE_PATH)

echo "Generating docs..."
dbt docs generate --profiles-dir $(dirname $PROFILE_PATH)

echo "$PROJECT_NAME completed successfully!" 