import duckdb
import os

# Connect to DuckDB
conn = duckdb.connect('retail_warehouse.duckdb')

# Load retail data
conn.sql("""
CREATE SCHEMA IF NOT EXISTS retail;
CREATE TABLE IF NOT EXISTS retail.raw_products AS 
    SELECT * FROM read_csv_auto('retail/raw_products.csv');
CREATE TABLE IF NOT EXISTS retail.raw_sales AS 
    SELECT * FROM read_csv_auto('retail/raw_sales.csv');
CREATE TABLE IF NOT EXISTS retail.raw_inventory AS 
    SELECT * FROM read_csv_auto('retail/raw_inventory.csv');
CREATE TABLE IF NOT EXISTS retail.raw_promotions AS 
    SELECT * FROM read_csv_auto('retail/raw_promotions.csv');
""")

# Load customer data
conn.sql("""
CREATE SCHEMA IF NOT EXISTS customer;
CREATE TABLE IF NOT EXISTS customer.raw_customers AS 
    SELECT * FROM read_csv_auto('customer/raw_customers.csv');
CREATE TABLE IF NOT EXISTS customer.raw_customer_preferences AS 
    SELECT * FROM read_csv_auto('customer/raw_customer_preferences.csv');
CREATE TABLE IF NOT EXISTS customer.raw_customer_feedback AS 
    SELECT * FROM read_csv_auto('customer/raw_customer_feedback.csv');
""")

# Load finance data
conn.sql("""
CREATE SCHEMA IF NOT EXISTS finance;
CREATE TABLE IF NOT EXISTS finance.raw_product_costs AS 
    SELECT * FROM read_csv_auto('finance/raw_product_costs.csv');
CREATE TABLE IF NOT EXISTS finance.raw_marketing_costs AS 
    SELECT * FROM read_csv_auto('finance/raw_marketing_costs.csv');
CREATE TABLE IF NOT EXISTS finance.raw_operational_costs AS 
    SELECT * FROM read_csv_auto('finance/raw_operational_costs.csv');
""")

conn.close() 