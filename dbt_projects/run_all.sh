#!/bin/bash

# Set the base directory
BASE_DIR="/Users/telvin/Desktop/dbt/dbt_projects"

# Run retail_ops
echo "Running retail_ops..."
cd $BASE_DIR/retail_ops
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt docs generate --profiles-dir .

# Run customer_360
echo "Running customer_360..."
cd $BASE_DIR/customer_360
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt docs generate --profiles-dir .

# Run finance_metrics
echo "Running finance_metrics models..."
cd $BASE_DIR/finance_metrics
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt docs generate --profiles-dir .

echo "All projects completed!" 