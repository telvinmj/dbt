#!/bin/bash

# Set root directory
ROOT_DIR=$(dirname $(dirname $(realpath $0)))
echo "Root directory: $ROOT_DIR"

# Function to run dbt project
run_dbt_project() {
    local project_name=$1
    local project_dir="$ROOT_DIR/$project_name"
    
    echo "----------------------------------------"
    echo "Running DBT project: $project_name"
    echo "Project directory: $project_dir"
    echo "----------------------------------------"
    
    # Change to the project directory
    cd "$project_dir"
    
    # Run DBT using the specific profile for this project
    # Use either local profile in project folder or the central one in .dbt directory
    if [ -f "./profiles.yml" ]; then
        echo "Using local profiles.yml"
        PROFILE_PATH="./profiles.yml"
    else
        echo "Using global profiles.yml"
        PROFILE_PATH="$ROOT_DIR/.dbt/profiles.yml"
    fi
    
    # Run dbt commands
    echo "Running dbt deps..."
    dbt deps --profiles-dir $(dirname $PROFILE_PATH)
    
    echo "Running dbt run..."
    dbt run --profiles-dir $(dirname $PROFILE_PATH)
    
    echo "Generating docs..."
    dbt docs generate --profiles-dir $(dirname $PROFILE_PATH)
    
    echo "$project_name completed successfully!"
    echo ""
}

# Make sure DBT is installed
if ! command -v dbt &> /dev/null; then
    echo "DBT is not installed. Please install it first."
    exit 1
fi

echo "=== Starting DBT Project 3 Run ==="
echo "Running projects in dependency order: customer_project -> policy_project -> claims_project"

# Run projects in dependency order
run_dbt_project "customer_project"
run_dbt_project "policy_project"
run_dbt_project "claims_project"

echo "=== All DBT Projects Completed Successfully ==="
echo "Manifest and catalog files have been generated in each project's target directory"