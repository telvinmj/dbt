# backend/services/dbt_metadata_parser.py

import os
import json
import glob
import re
from typing import Dict, List, Any, Optional, Tuple
import uuid
import yaml

def _extract_cross_project_sources(projects_dir, project_dirs):
    """Extract cross-project source references from source yaml files"""
    cross_project_sources = {}
    
    for project_dir in project_dirs:
        # Look for source definition files (typically in models/sources.yml or models/**/sources.yml)
        source_files = []
        models_dir = os.path.join(projects_dir, project_dir, 'models')
        
        # Skip if models directory doesn't exist
        if not os.path.exists(models_dir):
            continue
            
        # Find all YAML files that might contain source definitions
        for root, _, files in os.walk(models_dir):
            for file in files:
                if file.endswith(('.yml', '.yaml')) and os.path.basename(file) in ['sources.yml', 'src_insurance.yml']:
                    source_files.append(os.path.join(root, file))
        
        # Parse each source file
        for source_file in source_files:
            try:
                with open(source_file, 'r') as f:
                    source_data = yaml.safe_load(f)
                
                # Look for sources that reference other projects
                if source_data and 'sources' in source_data:
                    for source in source_data['sources']:
                        source_name = source.get('name', '')
                        
                        # Check if this source name matches another project
                        if source_name in project_dirs and source_name != project_dir:
                            # This is a cross-project reference
                            if 'tables' in source:
                                for table in source['tables']:
                                    table_name = table.get('name', '')
                                    if table_name:
                                        # Store this cross-project reference
                                        if project_dir not in cross_project_sources:
                                            cross_project_sources[project_dir] = []
                                        
                                        cross_project_sources[project_dir].append({
                                            'source_project': source_name,
                                            'table_name': table_name,
                                            'target_project': project_dir
                                        })
            except Exception as e:
                print(f"Error parsing source file {source_file}: {str(e)}")
    
    return cross_project_sources

def _extract_cross_project_refs_from_sql(projects_dir, project_dirs):
    """Extract cross-project references from SQL files by looking for ref() and source() functions"""
    cross_project_refs = {}
    
    for project_dir in project_dirs:
        models_dir = os.path.join(projects_dir, project_dir, 'models')
        
        # Skip if models directory doesn't exist
        if not os.path.exists(models_dir):
            continue
            
        # Find all SQL files
        sql_files = []
        for root, _, files in os.walk(models_dir):
            for file in files:
                if file.endswith('.sql'):
                    sql_files.append(os.path.join(root, file))
        
        # Process each SQL file
        if project_dir not in cross_project_refs:
            cross_project_refs[project_dir] = []
            
        for sql_file in sql_files:
            model_name = os.path.basename(sql_file).replace('.sql', '')
            
            try:
                with open(sql_file, 'r') as f:
                    sql_content = f.read()
                
                # Look for explicit ref patterns with project references: {{ ref('model_name', 'project_name') }}
                # The first parameter is the model name, the second is the project
                ref_pattern = r"{{\s*ref\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*}}"
                ref_matches = re.findall(ref_pattern, sql_content)
                
                for match in ref_matches:
                    ref_model, ref_project = match  # Note: Order is model_name, project_name
                    if ref_project in project_dirs and ref_project != project_dir:
                        cross_project_refs[project_dir].append({
                            'model': model_name,
                            'references': {
                                'type': 'ref',
                                'project': ref_project,
                                'model': ref_model
                            }
                        })
                        print(f"Found cross-project reference in {project_dir}.{model_name}: ref('{ref_model}', '{ref_project}')")
                
                # Also look for standard ref patterns that might reference models with same name in different projects
                standard_ref_pattern = r"{{\s*ref\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*}}"
                standard_ref_matches = re.findall(standard_ref_pattern, sql_content)
                
                for ref_model in standard_ref_matches:
                    # Check if this model exists in other projects 
                    for other_project in project_dirs:
                        if other_project != project_dir:
                            other_models_dir = os.path.join(projects_dir, other_project, 'models')
                            if os.path.exists(other_models_dir):
                                # Look for matching model in other project
                                for root, _, files in os.walk(other_models_dir):
                                    if f"{ref_model}.sql" in files:
                                        # Found matching model in other project, might be a cross-project reference
                                        print(f"Potential implicit cross-project reference in {project_dir}.{model_name}: ref('{ref_model}') -> {other_project}.{ref_model}")
                
                # Look for source patterns that reference other projects: {{ source('source_name', 'table_name') }}
                source_pattern = r"{{\s*source\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*}}"
                source_matches = re.findall(source_pattern, sql_content)
                
                for match in source_matches:
                    source_name, table_name = match
                    # Check if source name matches another project
                    if source_name in project_dirs and source_name != project_dir:
                        cross_project_refs[project_dir].append({
                            'model': model_name,
                            'references': {
                                'type': 'source',
                                'project': source_name,
                                'model': table_name
                            }
                        })
                        print(f"Found cross-project source in {project_dir}.{model_name}: source('{source_name}', '{table_name}')")
                        
            except Exception as e:
                print(f"Error processing SQL file {sql_file}: {str(e)}")
    
    return cross_project_refs

def parse_dbt_projects(projects_dir: str = "dbt_projects_2") -> Dict[str, Any]:
    """Parse dbt projects and extract metadata."""
    print(f"Parsing dbt projects from directory: {projects_dir}")
    
    # Find all dbt project directories
    project_dirs = []
    for item in os.listdir(projects_dir):
        if os.path.isdir(os.path.join(projects_dir, item)) and os.path.exists(os.path.join(projects_dir, item, "dbt_project.yml")):
            if not item.startswith('.'):  # Skip hidden dirs like .dbt
                project_dirs.append(item)
    
    if not project_dirs:
        print(f"No dbt projects found in {projects_dir}")
        return {"projects": [], "models": [], "lineage": []}
    
    print(f"Found {len(project_dirs)} dbt projects to parse: {', '.join(project_dirs)}")
    
    # Extract cross-project sources for later lineage connections
    cross_project_sources = _extract_cross_project_sources(projects_dir, project_dirs)
    
    # Extract direct SQL refs between projects
    cross_project_refs = _extract_cross_project_refs_from_sql(projects_dir, project_dirs)
    
    # Initialize data structures
    projects = []
    models = []
    lineage_data = []
    model_id_map = {}  # Maps node_id to our model_id
    
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
                    
                    # Generate a unique ID for the model using the project_id as prefix
                    # This ensures uniqueness across all projects
                    model_id = f"{project_id}_{model_name}"
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
                    for dep_node_id in node.get('depends_on', {}).get('nodes', []):
                        if dep_node_id in model_id_map:
                            source_id = model_id_map[dep_node_id]
                            lineage_data.append({
                                "source": source_id,
                                "target": target_id
                            })
                            lineage_count += 1
                    
                    # Check for references to models in other projects through the source() function
                    if 'refs' in node.get('depends_on', {}):
                        for ref in node.get('depends_on', {}).get('refs', []):
                            if len(ref) >= 2:
                                ref_model_name = ref[0]
                                ref_project_name = ref[1] if len(ref) > 1 else None
                                
                                # If a specific project is referenced, look for models with that name in that project
                                if ref_project_name:
                                    for other_node_id, other_node in manifest_data.get('nodes', {}).items():
                                        if other_node.get('resource_type') == 'model' and other_node.get('name') == ref_model_name:
                                            node_project_name = other_node.get('package_name')
                                            if node_project_name == ref_project_name and other_node_id in model_id_map:
                                                other_model_id = model_id_map[other_node_id]
                                                lineage_data.append({
                                                    "source": other_model_id,
                                                    "target": target_id
                                                })
                                                lineage_count += 1
                    
                    # Check for sources that reference other projects
                    if 'sources' in node.get('depends_on', {}):
                        for source_ref in node.get('depends_on', {}).get('sources', []):
                            if len(source_ref) >= 2:
                                source_name = source_ref[0]
                                table_name = source_ref[1]
                                
                                # Check if this source might be referencing another project's model
                                for project_dir_name in project_dirs:
                                    if project_dir_name != project_dir and source_name == project_dir_name:
                                        # Look for models in that project with the matching name
                                        for other_node_id, other_node in manifest_data.get('nodes', {}).items():
                                            if other_node.get('resource_type') == 'model' and other_node.get('name') == table_name:
                                                if other_node.get('package_name') == source_name and other_node_id in model_id_map:
                                                    other_model_id = model_id_map[other_node_id]
                                                    lineage_data.append({
                                                        "source": other_model_id,
                                                        "target": target_id
                                                    })
                                                    lineage_count += 1
            
            print(f"Added {lineage_count} lineage relationships for project {project_name}")
        
        except Exception as e:
            print(f"Error processing project {project_dir}: {str(e)}")
    
    # Combine the data
    all_projects_data = {"projects": projects, "models": models, "lineage": lineage_data}
    
    # Process cross-project sources to add additional lineage
    model_name_map = {}
    for model in models:
        model_name = model.get('name')
        project_id = model.get('project')
        if model_name and project_id:
            if project_id not in model_name_map:
                model_name_map[project_id] = {}
            model_name_map[project_id][model_name] = model.get('id')
    
    # Add cross-project lineage connections based on source definitions
    cross_lineage_count = 0
    for target_project, sources in cross_project_sources.items():
        for source_ref in sources:
            source_project = source_ref.get('source_project')
            table_name = source_ref.get('table_name')
            
            # Find the corresponding model in the source project
            if (source_project in model_name_map and 
                table_name in model_name_map[source_project] and
                target_project in model_name_map):
                
                # Add lineage for each model in the target project that might use this source
                source_model_id = model_name_map[source_project][table_name]
                
                # Check if any models in the target project have this in their name
                # This is a heuristic - models often follow naming like stg_<source>_<table>
                for target_model_name, target_model_id in model_name_map[target_project].items():
                    # Check if the target model potentially references the source
                    # This is a simplification - in reality we'd parse the SQL to know for sure
                    if table_name in target_model_name or target_model_name.startswith(f"stg_{table_name}"):
                        # Add a lineage connection
                        lineage_data.append({
                            "source": source_model_id,
                            "target": target_model_id
                        })
                        cross_lineage_count += 1
    
    print(f"Added {cross_lineage_count} cross-project lineage connections based on source definitions")
    
    # Add lineage based on direct SQL references
    sql_lineage_count = 0
    for target_project, refs in cross_project_refs.items():
        for ref_data in refs:
            target_model = ref_data.get('model')
            ref_info = ref_data.get('references', {})
            ref_type = ref_info.get('type')
            ref_project = ref_info.get('project')
            ref_model = ref_info.get('model')
            
            # Skip if we're missing needed information
            if not all([target_model, ref_project, ref_model]):
                continue
                
            # Look up IDs
            if target_project not in model_name_map or target_model not in model_name_map[target_project]:
                continue
                
            if ref_project not in model_name_map or ref_model not in model_name_map[ref_project]:
                continue
                
            target_id = model_name_map[target_project][target_model]
            source_id = model_name_map[ref_project][ref_model]
            
            # Add the lineage connection
            lineage_data.append({
                "source": source_id,
                "target": target_id
            })
            sql_lineage_count += 1
    
    print(f"Added {sql_lineage_count} cross-project lineage connections based on SQL references")
    
    print(f"=== Parsing Complete ===")
    print(f"Total projects: {len(projects)}")
    print(f"Total models: {len(models)}")
    print(f"Total lineage relationships: {len(lineage_data)}")
    
    return all_projects_data

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