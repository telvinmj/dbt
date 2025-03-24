#!/bin/bash

# Script to restart the backend service with updated metadata
echo "=== Restarting Backend Service with Updated Cross-Project Lineage ==="

# Navigate to project directory
cd "$(dirname "$0")"

# Kill any existing backend service
echo "Stopping existing backend service..."
pkill -f run.py || true

# Re-run metadata parser to parse with improved cross-project reference handling
echo "Re-parsing DBT projects to capture cross-project references..."
python services/refresh_metadata.py dbt_project_3

# Run the cross-project lineage fix
echo "Adding explicit cross-project lineage connections..."
python fix_cross_lineage.py

# Start the backend service
echo "Starting backend service..."
python run.py --projects-dir ../dbt_project_3

echo "Backend service restarted successfully!" 