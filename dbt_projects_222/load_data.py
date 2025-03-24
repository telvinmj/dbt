#!/usr/bin/env python3
import os
import pandas as pd
import duckdb

def create_duckdb_database():
    """Create a new DuckDB database for insurance data."""
    print("Creating DuckDB database...")
    # Fix the path to use absolute path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'insurance_data.db')
    print(f"Database will be created at: {db_path}")
    conn = duckdb.connect(db_path)
    
    # Create schemas for all projects and raw data
    schemas = [
        'raw_data',
        'staging',
        'intermediate',
        'mart'
    ]
    
    for schema in schemas:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    
    print("Database and schemas created successfully.")
    return conn

def load_seed_files(conn):
    """Load all seed CSV files into the DuckDB database."""
    print("Loading seed data...")
    
    projects = [
        'claims_processing',
        'policy_management',
        'customer_risk'
    ]
    
    # Get the absolute path to the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for project in projects:
        seed_dir = os.path.join(base_dir, project, 'seeds')
        if not os.path.exists(seed_dir):
            print(f"No seeds directory found for {project}")
            continue
        
        for seed_file in os.listdir(seed_dir):
            if seed_file.endswith('.csv'):
                table_name = os.path.splitext(seed_file)[0]
                file_path = os.path.join(seed_dir, seed_file)
                
                print(f"Loading {file_path} into raw_data.{table_name}...")
                try:
                    # Read the CSV file using pandas
                    df = pd.read_csv(file_path)
                    
                    # Create or replace the table in DuckDB
                    conn.execute(f"CREATE OR REPLACE TABLE raw_data.{table_name} AS SELECT * FROM df")
                    print(f"Successfully loaded {len(df)} rows into raw_data.{table_name}")
                except Exception as e:
                    print(f"Error loading {file_path}: {str(e)}")

def main():
    """Main function to create database and load data."""
    print("Starting data load process...")
    conn = create_duckdb_database()
    load_seed_files(conn)
    conn.close()
    print("Data loading completed successfully.")

if __name__ == "__main__":
    main() 