import json
import os
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import glob

from backend.models.database import (
    Project, 
    Model, 
    ColumnModel as Column,  # Updated import to use ColumnModel but alias as Column
    Lineage, 
    Tag
)
# from backend.services.ai_service import generate_description  # Comment out AI import

def extract_columns_from_sql(sql: str) -> List[str]:
    """Extract column names from SQL using regex"""
    # Simple regex to find column names in SELECT statements
    select_pattern = r"SELECT\s+(.+?)\s+FROM"
    match = re.search(select_pattern, sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    
    select_clause = match.group(1)
    # Split by commas, but ignore commas inside functions
    columns_raw = re.findall(r'([^,]+(?:\([^)]*\)[^,]*)*)', select_clause)
    
    columns = []
    for col in columns_raw:
        # Extract column name or alias
        alias_match = re.search(r'(?:AS\s+)?([a-zA-Z0-9_]+)$', col.strip(), re.IGNORECASE)
        if alias_match:
            columns.append(alias_match.group(1))
        else:
            # Try to get the last part of expression
            parts = col.strip().split('.')
            if parts:
                last_part = parts[-1].strip()
                # Remove any function calls
                clean_name = re.sub(r'\([^)]*\)', '', last_part).strip()
                if clean_name and not clean_name.startswith('('):
                    columns.append(clean_name)
    
    return columns

def parse_dbt_manifest(project_path: str, db: Session) -> Project:
    """Parse a dbt project's manifest.json file and populate the database"""
    manifest_path = os.path.join(project_path, 'target', 'manifest.json')
    
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file not found at {manifest_path}")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Get project name from dbt_project.yml
    project_config_path = os.path.join(project_path, 'dbt_project.yml')
    project_name = os.path.basename(project_path)  # Default to directory name
    
    if os.path.exists(project_config_path):
        with open(project_config_path, 'r') as f:
            for line in f:
                if line.strip().startswith('name:'):
                    project_name = line.split(':', 1)[1].strip().strip("'\"")
                    break
    
    # Create or update project
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        project = Project(name=project_name, path=project_path)
        db.add(project)
        db.flush()
    
    # Process nodes (models)
    processed_models = set()
    
    for node_id, node in manifest.get('nodes', {}).items():
        if node.get('resource_type') == 'model':
            model_name = node.get('name')
            if not model_name:
                continue
            
            # Skip if not in this project
            if node.get('package_name') != project_name:
                continue
            
            processed_models.add(model_name)
            
            # Create or update model
            model = db.query(Model).filter(
                Model.name == model_name,
                Model.project_id == project.id
            ).first()
            
            file_path = node.get('original_file_path', '')
            schema = node.get('schema', '')
            materialized = node.get('config', {}).get('materialized', '')
            description = node.get('description', '')
            raw_sql = node.get('raw_sql', '')
            compiled_sql = node.get('compiled_sql', '')
            
            if not model:
                model = Model(
                    name=model_name,
                    project_id=project.id,
                    schema_name=schema,
                    materialized=materialized,
                    description=description,
                    sql=raw_sql,
                    file_path=file_path,
                )
                db.add(model)
                db.flush()
                
                # Comment out AI description generation
                # if raw_sql:
                #     try:
                #         ai_description = generate_description('model', model_name, raw_sql)
                #         model.ai_description = ai_description
                #     except Exception as e:
                #         print(f"Error generating AI description for model {model_name}: {e}")
            else:
                model.schema_name = schema
                model.materialized = materialized
                model.description = description
                model.sql = raw_sql
                model.file_path = file_path
                db.flush()
            
            # Process columns
            columns_dict = node.get('columns', {})
            extracted_columns = extract_columns_from_sql(raw_sql) if raw_sql else []
            
            # Combine discovered columns with those in manifest
            all_column_names = set(columns_dict.keys())
            all_column_names.update(extracted_columns)
            
            for column_name in all_column_names:
                column_info = columns_dict.get(column_name, {})
                description = column_info.get('description', '')
                
                column = db.query(Column).filter(
                    Column.name == column_name,
                    Column.model_id == model.id
                ).first()
                
                if not column:
                    column = Column(
                        name=column_name,
                        model_id=model.id,
                        description=description
                    )
                    db.add(column)
                    db.flush()
                    
                    # Comment out AI description generation
                    # try:
                    #     data_for_ai = f"Column: {column_name} in model {model_name}"
                    #     if raw_sql:
                    #         data_for_ai += f"\nContext from SQL: {raw_sql}"
                    #     
                    #     ai_description = generate_description('column', column_name, data_for_ai)
                    #     column.ai_description = ai_description
                    # except Exception as e:
                    #     print(f"Error generating AI description for column {column_name}: {e}")
                else:
                    column.description = description
                    db.flush()
    
    # Process lineage information
    for child_id, parent_nodes in manifest.get('child_map', {}).items():
        # Only process if this is a model and in our project
        child_node = manifest.get('nodes', {}).get(child_id)
        if not child_node or child_node.get('resource_type') != 'model' or child_node.get('package_name') != project_name:
            continue
        
        child_model = db.query(Model).filter(
            Model.name == child_node.get('name'),
            Model.project_id == project.id
        ).first()
        
        if not child_model:
            continue
        
        for parent_id in parent_nodes:
            parent_node = manifest.get('nodes', {}).get(parent_id)
            if not parent_node or parent_node.get('resource_type') != 'model':
                continue
            
            parent_package = parent_node.get('package_name')
            parent_model_name = parent_node.get('name')
            
            # Find parent model in our database
            parent_project = db.query(Project).filter(Project.name == parent_package).first()
            if not parent_project:
                continue
                
            parent_model = db.query(Model).filter(
                Model.name == parent_model_name,
                Model.project_id == parent_project.id
            ).first()
            
            if not parent_model:
                continue
            
            # Create lineage record
            lineage = db.query(Lineage).filter(
                Lineage.upstream_id == parent_model.id,
                Lineage.downstream_id == child_model.id
            ).first()
            
            if not lineage:
                lineage = Lineage(
                    upstream_id=parent_model.id,
                    downstream_id=child_model.id
                )
                db.add(lineage)
    
    db.commit()
    return project

def parse_all_projects(project_paths: List[str], db: Session) -> List[Project]:
    """Parse multiple dbt projects and update the database"""
    projects = []
    
    for path in project_paths:
        try:
            project = parse_dbt_manifest(path, db)
            projects.append(project)
        except Exception as e:
            print(f"Error parsing project at {path}: {e}")
    
    return projects

def parse_dbt_projects(projects_dir: str = "dbt_projects_2") -> Dict[str, Any]:
    """
    Parse dbt project files (manifest.json and catalog.json) and generate a structured metadata object
    (Alternative implementation)
    """
    # Initialize data structures
    projects = []
    models = []
    lineage_data = []
    model_id_map = {}  # Maps node_id to our model_id
    
    # Get all project directories
    project_dirs = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d)) 
                   and not d.startswith('.')]
    
    # Process each project
    for project_idx, project_dir in enumerate(project_dirs):
        project_path = os.path.join(projects_dir, project_dir)
        project_id = project_dir.lower()  # Use directory name as project ID
        
        # Add project to projects list
        projects.append({
            "id": project_id,
            "name": project_dir,
            "description": f"{project_dir} dbt project"
        })
        
        # Look for manifest.json and catalog.json
        manifest_path = os.path.join(project_path, "target", "manifest.json")
        catalog_path = os.path.join(project_path, "target", "catalog.json")
        
        manifest_data = {}
        catalog_data = {}
        
        # Load manifest.json if it exists
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
        
        # Load catalog.json if it exists
        if os.path.exists(catalog_path):
            with open(catalog_path, 'r') as f:
                catalog_data = json.load(f)
        
        # Process models from manifest
        if manifest_data and 'nodes' in manifest_data:
            model_prefix = f"{project_id[0]}"  # Use first letter of project as prefix
            model_counter = 1
            
            # First pass: create models
            for node_id, node in manifest_data['nodes'].items():
                # Only process model nodes
                if node['resource_type'] == 'model':
                    model_name = node['name']
                    model_id = f"{model_prefix}{model_counter}"
                    model_counter += 1
                    
                    # Store mapping for lineage
                    model_id_map[node_id] = model_id
                    
                    # Get SQL content
                    sql_content = node.get('raw_sql', '')
                    
                    # Get description
                    description = node.get('description', model_name)
                    if not description:
                        description = model_name
                    
                    # Get columns from catalog if available
                    columns = []
                    catalog_node = None
                    
                    if catalog_data and 'nodes' in catalog_data:
                        catalog_node = catalog_data['nodes'].get(node_id)
                    
                    if catalog_node and 'columns' in catalog_node:
                        for col_name, col_data in catalog_node['columns'].items():
                            # Determine if column is primary key (simple heuristic)
                            is_primary_key = col_name.lower() in ['id', f"{model_name}_id", 'key', 'primary_key']
                            
                            # Determine if column is foreign key (simple heuristic)
                            is_foreign_key = '_id' in col_name.lower() and not is_primary_key
                            
                            column = {
                                "name": col_name,
                                "type": col_data.get('type', 'string'),
                                "description": col_data.get('description', f"{col_name} column"),
                                "isPrimaryKey": is_primary_key,
                                "isForeignKey": is_foreign_key
                            }
                            columns.append(column)
                    
                    # If no columns from catalog, try to extract from manifest
                    if not columns and 'columns' in node:
                        for col_name, col_data in node['columns'].items():
                            # Determine if column is primary key (simple heuristic)
                            is_primary_key = col_name.lower() in ['id', f"{model_name}_id", 'key', 'primary_key']
                            
                            # Determine if column is foreign key (simple heuristic)
                            is_foreign_key = '_id' in col_name.lower() and not is_primary_key
                            
                            column = {
                                "name": col_name,
                                "type": col_data.get('data_type', 'string'),
                                "description": col_data.get('description', f"{col_name} column"),
                                "isPrimaryKey": is_primary_key,
                                "isForeignKey": is_foreign_key
                            }
                            columns.append(column)
                    
                    # If still no columns, try to extract from SQL
                    if not columns and sql_content:
                        # Simple regex to extract column names from SQL
                        # This is a basic implementation and might not work for all SQL variants
                        select_pattern = re.compile(r'SELECT\s+(.*?)\s+FROM', re.IGNORECASE | re.DOTALL)
                        select_match = select_pattern.search(sql_content)
                        
                        if select_match:
                            select_clause = select_match.group(1)
                            # Split by commas, but ignore commas inside functions
                            # This is a simplified approach and might not work for complex SQL
                            in_function = 0
                            current_col = ""
                            extracted_cols = []
                            
                            for char in select_clause:
                                if char == '(':
                                    in_function += 1
                                    current_col += char
                                elif char == ')':
                                    in_function -= 1
                                    current_col += char
                                elif char == ',' and in_function == 0:
                                    extracted_cols.append(current_col.strip())
                                    current_col = ""
                                else:
                                    current_col += char
                            
                            if current_col:
                                extracted_cols.append(current_col.strip())
                            
                            for col_expr in extracted_cols:
                                # Extract column name (handle aliases with AS keyword)
                                as_match = re.search(r'(?:AS|as)\s+([a-zA-Z0-9_]+)$', col_expr)
                                if as_match:
                                    col_name = as_match.group(1)
                                else:
                                    # If no AS keyword, use the last part after a dot or the whole expression
                                    col_parts = col_expr.split('.')
                                    col_name = col_parts[-1].strip()
                                
                                # Determine if column is primary key (simple heuristic)
                                is_primary_key = col_name.lower() in ['id', f"{model_name}_id", 'key', 'primary_key']
                                
                                # Determine if column is foreign key (simple heuristic)
                                is_foreign_key = '_id' in col_name.lower() and not is_primary_key
                                
                                column = {
                                    "name": col_name,
                                    "type": "string",  # Default type
                                    "description": f"{col_name} column",
                                    "isPrimaryKey": is_primary_key,
                                    "isForeignKey": is_foreign_key
                                }
                                columns.append(column)
                    
                    # Create model object
                    model = {
                        "id": model_id,
                        "name": model_name,
                        "project": project_id,
                        "description": description,
                        "columns": columns,
                        "sql": sql_content
                    }
                    
                    models.append(model)
            
            # Second pass: create lineage relationships
            for node_id, node in manifest_data['nodes'].items():
                if node['resource_type'] == 'model' and node_id in model_id_map:
                    target_id = model_id_map[node_id]
                    
                    # Get dependencies
                    if 'depends_on' in node and 'nodes' in node['depends_on']:
                        for source_node_id in node['depends_on']['nodes']:
                            if source_node_id in model_id_map:
                                source_id = model_id_map[source_node_id]
                                
                                # Add lineage relationship
                                lineage_data.append({
                                    "source": source_id,
                                    "target": target_id
                                })
    
    return {
        "projects": projects,
        "models": models,
        "lineage": lineage_data
    }

def save_metadata(metadata: Dict[str, Any], output_file: str = "dbt_metadata.json"):
    """Save the parsed metadata to a JSON file"""
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_or_create_metadata(output_file: str = "dbt_metadata.json") -> Dict[str, Any]:
    """Load metadata from a JSON file or create it if it doesn't exist"""
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata file: {e}")
            # If there's an error loading, create a new one
            metadata = parse_dbt_projects()
            save_metadata(metadata, output_file)
            return metadata
    else:
        # File doesn't exist, create it
        metadata = parse_dbt_projects()
        save_metadata(metadata, output_file)
        return metadata

if __name__ == "__main__":
    metadata = parse_dbt_projects()
    save_metadata(metadata)
    print(f"Parsed {len(metadata['projects'])} projects, {len(metadata['models'])} models, and {len(metadata['lineage'])} lineage relationships") 