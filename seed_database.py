#!/usr/bin/env python

from backend.db.seed_data import seed_database

if __name__ == "__main__":
    print("Seeding database with sample dbt project data...")
    seed_database()
    print("Database seeding complete. You can now run the application.") 