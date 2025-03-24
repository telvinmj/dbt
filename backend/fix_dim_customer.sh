#!/bin/bash

# Script to fix dim_customer lineage issues
# This addresses the problem where dim_customer appears in multiple projects

echo "===== Starting dim_customer lineage fix ====="

# Step 1: Check current cross-project lineage
echo "Checking current cross-project lineage..."
python3 check_cross_lineage.py

# Step 2: Fix model IDs to ensure consistent cross-project references
echo -e "\nFixing model IDs..."
python3 fix_model_ids.py

# Step 3: Add missing cross-project connections for dim_customer
echo -e "\nFixing cross-project lineage connections..."
python3 fix_cross_lineage.py

# Step 4: Run the special dim_customer lineage fix
echo -e "\nRunning dim_customer-specific fixes..."
python3 update_dim_customer_lineage.py

# Step 5: Update the metadata file
echo -e "\nUpdating metadata file..."
cp exports/updated_metadata.json exports/uni_metadata.json

echo -e "\n===== All fixes applied! ====="
echo "To see the changes, restart the backend server and refresh the frontend."
echo "Run: python3 run.py to restart the backend" 