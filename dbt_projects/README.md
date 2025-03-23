# dbt Projects

This folder contains three separate dbt projects that all use the same data source:

## Project Structure
```
dbt_projects/
├── data/                  # Contains shared source data
├── retail_ops/            # Retail operations dbt project
├── finance_metrics/       # Finance metrics dbt project
├── customer_360/          # Customer 360 dbt project
└── run_all.sh             # Script to run all dbt projects
```

## Running Projects
To run all projects, simply execute:
```
./run_all.sh
```

Each project has its own configuration but shares the same data source. 