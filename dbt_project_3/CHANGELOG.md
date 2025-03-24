# Changelog

## 2023-03-24

### Fixed

- **Dependency Conflict Resolution**: Updated package versions to be compatible
  - Updated dbt-labs/dbt_utils from 0.9.2 to 1.1.1 in all projects
  - Updated dbt-labs/audit_helper from 0.5.0 to 0.7.0 in all projects
  
- **Cross-Project References**: Improved references between projects
  - Updated seed references to include project names
  - Made raw_customers reference consistent across projects
  - Made raw_policies reference consistent across projects

- **Function Compatibility**: Updated SQL functions to use dbt_utils package
  - Changed native DATEDIFF function to dbt_utils.datediff
  - Updated parameters order for date difference calculations

- **Installation Scripts**: Enhanced dependency management
  - Added package cleanup before installation
  - Separated dependency installation from project run
  - Added seed data loading to individual project scripts
  - Improved logging and error reporting 