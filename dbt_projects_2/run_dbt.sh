#!/bin/bash

# Usage: ./run_dbt.sh <project_dir> <dbt_command>
# Example: ./run_dbt.sh claims_processing run
# Example: ./run_dbt.sh policy_management docs generate

if [ $# -lt 2 ]; then
  echo "Usage: ./run_dbt.sh <project_dir> <dbt_command> [additional_args]"
  echo "Example: ./run_dbt.sh claims_processing run"
  echo "Example: ./run_dbt.sh policy_management docs generate"
  exit 1
fi

PROJECT_DIR=$1
shift
DBT_COMMAND=$1
shift
ADDITIONAL_ARGS=$@

# Get the absolute path to the profiles.yml directory
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROFILES_DIR=$SCRIPT_DIR

echo "Running dbt for project: $PROJECT_DIR"
echo "Command: $DBT_COMMAND"
echo "Using profiles from: $PROFILES_DIR"

# Change to the project directory and run the dbt command
cd "$SCRIPT_DIR/$PROJECT_DIR" && dbt "$DBT_COMMAND" --profiles-dir "$PROFILES_DIR" $ADDITIONAL_ARGS

exit_status=$?
if [ $exit_status -eq 0 ]; then
  echo "Command completed successfully!"
else
  echo "Command failed with exit code $exit_status"
fi 