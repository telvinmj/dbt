# backend/services/dbt_metadata_parser.py

import os
import json
import glob
import re
from typing import Dict, List, Any, Optional, Tuple
import uuid

def parse_dbt_projects(projects_dir: str = "dbt_projects_2") -> Dict[str, Any]:
    """
    Parse dbt project files (manifest.json and catalog.json) and generate a structured metadata object
    """
    # Initialize data structures
    projects = []
    models = []
    lineage_data = []
    model_id_map = {}  # Maps node_id to our model_id
    
    # Get all dbt project directories
    project_dirs = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d)) 
                   and os.path.exists(os.path.join(projects_dir, d, "dbt_project.yml"))
                   and not d.startswith('.')]
    
    print(f"Found {len(project_dirs)} dbt projects to parse: {', '.join(project_dirs)}")
    
    for project_dir in project_dirs:
        project_path = os.path.join(projects_dir, project_dir)
        
        # Look for manifest.json and catalog.json in the project's target directory
        manifest_path = os.path.join(project_path, "target", "manifest.json")
        catalog_path = os.path.join(project_path, "target", "catalog.json")
        
        # Skip if manifest doesn't exist (not a valid dbt project)
        if not os.path.exists(manifest_path):
            print(f"Skipping {project_dir}: No manifest.json found in {manifest_path}")
            continue
        
        # Load manifest.json
        try:
            print(f"Parsing project {project_dir} from {manifest_path}")
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
                
            # Load catalog.json if it exists
            catalog_data = {}
            if os.path.exists(catalog_path):
                with open(catalog_path, 'r') as f:
                    catalog_data = json.load(f)
                print(f"Found catalog.json for {project_dir}")
            else:
                print(f"No catalog.json found for {project_dir} (this is optional)")
            
            # Extract project name from manifest or use directory name
            project_name = project_dir
            if 'metadata' in manifest_data and 'project_name' in manifest_data['metadata']:
                project_name = manifest_data['metadata']['project_name']
            
            # Add project to projects list
            project_id = project_name.lower().replace(' ', '_')
            projects.append({
                "id": project_id,
                "name": project_name,
                "description": f"{project_name} dbt project",
                "path": project_path
            })
            
            print(f"Added project: {project_name} (id: {project_id})")
            
            # First pass: create models
            model_count = 0
            
            if 'nodes' not in manifest_data:
                print(f"Warning: No nodes found in {project_dir} manifest")
                continue
                
            for node_id, node in manifest_data['nodes'].items():
                if node.get('resource_type') == 'model':
                    model_name = node.get('name', '')
                    schema = node.get('schema', '')
                    description = node.get('description', '')
                    materialized = node.get('config', {}).get('materialized', 'view')
                    
                    # Generate a unique ID for the model
                    model_id = f"{project_id[0]}{model_count + 1}"
                    model_id_map[node_id] = model_id
                    model_count += 1
                    
                    # Get SQL code
                    raw_sql = ""
                    if 'raw_sql' in node:
                        raw_sql = node['raw_sql']
                    elif 'raw_code' in node:
                        raw_sql = node['raw_code']
                    
                    # Extract columns from catalog if available
                    columns = []
                    catalog_node = None
                    if catalog_data and 'nodes' in catalog_data:
                        catalog_node = catalog_data['nodes'].get(node_id)
                    
                    # Extract columns from SQL if not in catalog
                    extracted_columns = extract_columns_from_sql(raw_sql)
                    
                    if catalog_node and 'columns' in catalog_node:
                        for col_name, col_data in catalog_node['columns'].items():
                            # Determine if column is primary key (simple heuristic)
                            is_primary_key = col_name.lower() in ['id', f"{model_name}_id", 'key', 'primary_key']
                            
                            # Determine if column is foreign key (simple heuristic)
                            is_foreign_key = '_id' in col_name.lower() and not is_primary_key
                            
                            columns.append({
                                "name": col_name,
                                "type": col_data.get('type', 'unknown'),
                                "description": col_data.get('description', ''),
                                "isPrimaryKey": is_primary_key,
                                "isForeignKey": is_foreign_key
                            })
                    else:
                        # Use columns extracted from SQL
                        for col_name in extracted_columns:
                            # Simple heuristics for primary/foreign keys
                            is_primary_key = col_name.lower() in ['id', f"{model_name}_id", 'key', 'primary_key']
                            is_foreign_key = '_id' in col_name.lower() and not is_primary_key
                            
                            columns.append({
                                "name": col_name,
                                "type": "unknown",  # Can't determine type from SQL alone
                                "description": "",
                                "isPrimaryKey": is_primary_key,
                                "isForeignKey": is_foreign_key
                            })
                    
                    # Create model object
                    model = {
                        "id": model_id,
                        "name": model_name,
                        "project": project_id,
                        "description": description,
                        "columns": columns,
                        "sql": raw_sql
                    }
                    
                    models.append(model)
            
            print(f"Added {model_count} models for project {project_name}")
            
            # Second pass: create lineage relationships
            lineage_count = 0
            for node_id, node in manifest_data['nodes'].items():
                if node['resource_type'] == 'model' and node_id in model_id_map:
                    target_id = model_id_map[node_id]
                    
                    # Get dependencies
                    if 'depends_on' in node and 'nodes' in node['depends_on']:
                        for source_node_id in node['depends_on']['nodes']:
                            if source_node_id in model_id_map:
                                source_id = model_id_map[source_node_id]
                                lineage_data.append({
                                    "source": source_id,
                                    "target": target_id
                                })
                                lineage_count += 1
            
            print(f"Added {lineage_count} lineage relationships for project {project_name}")
        
        except Exception as e:
            print(f"Error processing project {project_dir}: {str(e)}")
    
    result = {
        "projects": projects,
        "models": models,
        "lineage": lineage_data
    }
    
    print(f"=== Parsing Complete ===")
    print(f"Total projects: {len(projects)}")
    print(f"Total models: {len(models)}")
    print(f"Total lineage relationships: {len(lineage_data)}")
    
    return result

def extract_columns_from_sql(sql: str) -> List[str]:
    """Extract column names from SQL query"""
    columns = []
    
    # Simple regex to find SELECT statements
    select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
    if select_match:
        select_clause = select_match.group(1)
        
        # Handle nested parentheses in SELECT clause
        current_expr = ""
        paren_level = 0
        col_expressions = []
        
        for char in select_clause:
            if char == '(' and paren_level == 0:
                paren_level += 1
                current_expr += char
            elif char == '(' and paren_level > 0:
                paren_level += 1
                current_expr += char
            elif char == ')' and paren_level > 0:
                paren_level -= 1
                current_expr += char
            elif char == ',' and paren_level == 0:
                col_expressions.append(current_expr.strip())
                current_expr = ""
            else:
                current_expr += char
        
        # Add the last expression
        if current_expr.strip():
            col_expressions.append(current_expr.strip())
        
        # Extract column names from expressions
        for col_expr in col_expressions:
            # Skip * wildcard
            if col_expr == '*':
                continue
                
            # Extract column name (handle aliases with AS keyword)
            as_match = re.search(r'(?:AS|as)\s+([a-zA-Z0-9_]+)$', col_expr)
            if as_match:
                col_name = as_match.group(1)
            else:
                # If no AS keyword, use the last part after a dot or the whole expression
                col_parts = col_expr.split('.')
                col_name = col_parts[-1].strip()
                
                # Remove any functions
                func_match = re.search(r'([a-zA-Z0-9_]+)\s*\(', col_name)
                if func_match:
                    # This is a function, skip it
                    continue
            
            columns.append(col_name)
    
    return columns

def save_metadata(metadata: Dict[str, Any], output_file: str = None):
    """Save the parsed metadata to a JSON file"""
    # Set default output file path if not provided
    if output_file is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(base_dir, "exports", "uni_metadata.json")
    
    # Ensure absolute path
    output_file = os.path.abspath(output_file)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"Saving metadata to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_metadata(input_file: str = None) -> Dict[str, Any]:
    """Load metadata from a JSON file"""
    # Set default input file path if not provided
    if input_file is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_file = os.path.join(base_dir, "exports", "uni_metadata.json")
    
    # Ensure absolute path
    input_file = os.path.abspath(input_file)
    
    print(f"Loading metadata from: {input_file}")
    try:
        with open(input_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Metadata file not found: {input_file}")
        # If file doesn't exist, parse projects and create it
        metadata = parse_dbt_projects()
        save_metadata(metadata, input_file)
        return metadata

if __name__ == "__main__":
    metadata = parse_dbt_projects()
    save_metadata(metadata)
    print(f"Parsed {len(metadata['projects'])} projects, {len(metadata['models'])} models, and {len(metadata['lineage'])} lineage relationships")