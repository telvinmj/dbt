#!/bin/bash

# System test script for DBT Metadata Explorer
# This script verifies that all components are working correctly

echo "=== DBT Metadata Explorer System Test ==="
echo "Testing all components and features"
echo

# 1. Check prerequisites
echo "Checking prerequisites..."
if ! command -v dbt &>/dev/null; then
  echo "❌ DBT is not installed. Please install dbt-core."
  exit 1
else
  echo "✅ DBT is installed: $(dbt --version | head -n 1)"
fi

if ! command -v python3 &>/dev/null; then
  echo "❌ Python is not installed. Please install Python 3.7+."
  exit 1
else
  echo "✅ Python is installed: $(python3 --version)"
fi

if ! command -v node &>/dev/null; then
  echo "❌ Node.js is not installed. Please install Node.js."
  exit 1
else
  echo "✅ Node.js is installed: $(node --version)"
fi

echo

# 2. Check dbt projects
echo "Checking dbt projects..."
if [ ! -d "dbt_projects_2" ]; then
  echo "❌ dbt_projects_2 directory not found."
  exit 1
else
  echo "✅ dbt_projects_2 directory exists"
  
  # Check for specific projects
  for project in claims_processing policy_management customer_risk; do
    if [ ! -d "dbt_projects_2/$project" ]; then
      echo "❌ $project project not found."
    else
      echo "✅ $project project exists"
    fi
  done
fi

echo

# 3. Check for profiles.yml
echo "Checking dbt profiles..."
if [ ! -f "dbt_projects_2/profiles.yml" ]; then
  echo "❌ profiles.yml not found in dbt_projects_2."
  exit 1
else
  echo "✅ profiles.yml exists"
fi

echo

# 4. Check backend components
echo "Checking backend components..."
if [ ! -d "backend" ]; then
  echo "❌ backend directory not found."
  exit 1
else
  echo "✅ backend directory exists"
  
  # Check for key files
  for file in main.py run.py requirements.txt; do
    if [ ! -f "backend/$file" ]; then
      echo "❌ backend/$file not found."
    else
      echo "✅ backend/$file exists"
    fi
  done
  
  # Check for services
  for service in metadata_service.py ai_description_service.py file_watcher_service.py; do
    if [ ! -f "backend/services/$service" ]; then
      echo "❌ backend/services/$service not found."
    else
      echo "✅ backend/services/$service exists"
    fi
  done
fi

echo

# 5. Check frontend components
echo "Checking frontend components..."
if [ ! -d "frontend" ]; then
  echo "❌ frontend directory not found."
  exit 1
else
  echo "✅ frontend directory exists"
  
  # Check for key files
  for file in package.json tsconfig.json; do
    if [ ! -f "frontend/$file" ]; then
      echo "❌ frontend/$file not found."
    else
      echo "✅ frontend/$file exists"
    fi
  done
fi

echo

# 6. Check for API key
echo "Checking Gemini API key..."
if [ -f "backend/.env" ]; then
  if grep -q "GEMINI_API_KEY" "backend/.env"; then
    echo "✅ GEMINI_API_KEY found in .env file"
    # Check if key is empty
    KEY=$(grep "GEMINI_API_KEY" "backend/.env" | cut -d= -f2 | tr -d '"')
    if [ -z "$KEY" ]; then
      echo "⚠️  Warning: GEMINI_API_KEY appears to be empty!"
    else
      echo "✅ GEMINI_API_KEY appears to be set"
    fi
  else
    echo "❌ GEMINI_API_KEY not found in .env file."
  fi
else
  echo "❌ backend/.env file not found."
fi

echo

# 7. Check dbt project manifests
echo "Checking for dbt manifest files..."
manifest_exists=false
for project in claims_processing policy_management customer_risk; do
  if [ -f "dbt_projects_2/$project/target/manifest.json" ]; then
    echo "✅ $project has a manifest.json file"
    manifest_exists=true
  else
    echo "❌ $project is missing manifest.json"
  fi
done

if [ "$manifest_exists" = false ]; then
  echo
  echo "⚠️  No manifest files found. Would you like to generate them? (y/n)"
  read -r generate_manifests
  if [ "$generate_manifests" = "y" ]; then
    echo "Generating manifests..."
    cd dbt_projects_2
    for project in claims_processing policy_management customer_risk; do
      echo "Generating manifest for $project..."
      ./run_dbt.sh "$project" docs generate
    done
    cd ..
  fi
fi

echo

# 8. Verify backend can start
echo "Testing backend startup (will exit after 5 seconds)..."
cd backend
timeout 5 python run.py &
backend_pid=$!
sleep 5
if ps -p $backend_pid > /dev/null; then
  echo "✅ Backend started successfully"
  kill $backend_pid 2>/dev/null
else
  echo "❌ Backend failed to start properly"
fi
cd ..

echo

# 9. Summary
echo "=== Test Summary ==="
echo "The system check has completed."
echo 
echo "To run the full system:"
echo "1. Start the backend:   cd backend && python run.py"
echo "2. Start the frontend:  cd frontend && npm start"
echo "3. Open browser at:     http://localhost:3000"
echo
echo "Note: If you're missing manifest files, run:"
echo "cd dbt_projects_2 && ./run_dbt.sh <project_name> docs generate"
echo
echo "For more details, see the README.md file." 