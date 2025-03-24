#!/bin/bash

# Set root directory
ROOT_DIR=$(dirname $(dirname $(realpath $0)))
echo "Root directory: $ROOT_DIR"

# Function to clean dbt packages and install dependencies
install_dependencies() {
    local project_name=$1
    local project_dir="$ROOT_DIR/$project_name"
    
    echo "----------------------------------------"
    echo "Installing dependencies for: $project_name"
    echo "Project directory: $project_dir"
    echo "----------------------------------------"
    
    # Change to the project directory
    cd "$project_dir"
    
    # Use either local profile or the central one
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
    
    # Run dbt deps
    echo "Running dbt deps..."
    dbt deps --profiles-dir $(dirname $PROFILE_PATH)
    
    echo "Dependencies installed for $project_name successfully!"
    echo ""
}

# Function to load seed data for a project
load_seed_data() {
    local project_name=$1
    local project_dir="$ROOT_DIR/$project_name"
    
    echo "----------------------------------------"
    echo "Loading seed data for: $project_name"
    echo "Project directory: $project_dir"
    echo "----------------------------------------"
    
    # Change to the project directory
    cd "$project_dir"
    
    # Use either local profile or the central one
    if [ -f "./profiles.yml" ]; then
        echo "Using local profiles.yml"
        PROFILE_PATH="./profiles.yml"
    else
        echo "Using global profiles.yml"
        PROFILE_PATH="$ROOT_DIR/.dbt/profiles.yml"
    fi
    
    # Run dbt seed
    echo "Running dbt seed..."
    dbt seed --profiles-dir $(dirname $PROFILE_PATH)
    
    echo "Seed data loaded for $project_name successfully!"
    echo ""
}

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
    
    # Use either local profile or the central one
    if [ -f "./profiles.yml" ]; then
        echo "Using local profiles.yml"
        PROFILE_PATH="./profiles.yml"
    else
        echo "Using global profiles.yml"
        PROFILE_PATH="$ROOT_DIR/.dbt/profiles.yml"
    fi
    
    # Run dbt commands
    echo "Running dbt run..."
    dbt run --profiles-dir $(dirname $PROFILE_PATH)
    
    echo "Running dbt test..."
    dbt test --profiles-dir $(dirname $PROFILE_PATH)
    
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

echo "=== Starting DBT Project 3 Setup and Run ==="

# Step 1: Install dependencies for all projects in dependency order
echo "STEP 1: Installing dependencies for all projects"
install_dependencies "customer_project"
install_dependencies "policy_project"
install_dependencies "claims_project"

# Step 2: Load seed data in dependency order
echo "STEP 2: Loading seed data for all projects"
load_seed_data "customer_project"
load_seed_data "policy_project"
load_seed_data "claims_project"

# Step 3: Run projects in dependency order
echo "STEP 3: Running projects in dependency order: customer_project -> policy_project -> claims_project"
run_dbt_project "customer_project"
run_dbt_project "policy_project"
run_dbt_project "claims_project"

echo "=== All DBT Projects Completed Successfully ==="
echo "Manifest and catalog files have been generated in each project's target directory"
echo "You can view documentation by running: dbt docs serve --project-dir=customer_project" 