#!/usr/bin/env python3
import json
import os
import re
import glob

def find_explicit_references(dbt_project_dir):
    """
    Scan SQL files for explicit cross-project references in the form: ref('model', 'project')
    Returns a list of tuples: (source_project, source_model, target_project, target_model)
    """
    explicit_refs = []
    
    # Regular expression to find ref('model', 'project') patterns
    ref_pattern = r"{{\s*ref\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)\s*}}"
    
    # Find all SQL files in the project
    sql_files = glob.glob(f"{dbt_project_dir}/**/models/**/*.sql", recursive=True)
    
    for sql_file in sql_files:
        # Determine which project this SQL file belongs to
        parts = sql_file.split('/')
            project_idx = parts.index(next(p for p in parts if p.endswith('_project')))
            source_project = parts[project_idx]
        
        # Extract model name from file path
        model_name = os.path.basename(sql_file).replace('.sql', '')
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
            
            # Find all explicit ref calls
            matches = re.findall(ref_pattern, sql_content)
            for target_model, target_project in matches:
                explicit_refs.append((
                        source_project, 
                        model_name,
                        target_project,
                    target_model
                    ))
                print(f"Found explicit reference: {source_project}.{model_name} -> {target_project}.{target_model}")
    
    return explicit_refs

def fix_cross_project_lineage():
    """
    Add explicit cross-project lineage connections based on known project dependencies.
    This is a direct approach to ensure cross-project connections appear in the UI.
    """
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "uni_metadata.json")
    dbt_project_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbt_project_3")
    
    print(f"Reading metadata from: {metadata_path}")
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        return
    
    # Create model lookup for easy reference
    models = metadata.get("models", [])
    lineage = metadata.get("lineage", [])
    
    model_lookup = {}
    model_by_project_and_name = {}
    
    for model in models:
        model_id = model.get("id")
        model_name = model.get("name")
        project_id = model.get("project")
        
        if model_id and model_name and project_id:
            if project_id not in model_lookup:
                model_lookup[project_id] = {}
                model_by_project_and_name[project_id] = {}
            model_lookup[project_id][model_name] = model_id
            model_by_project_and_name[project_id][model_name] = model
            
    # Find explicit cross-project references in SQL files
    explicit_refs = find_explicit_references(dbt_project_dir)
            
    # Add connections from explicit references
    cross_project_connections = []
    for source_project, source_model, target_project, target_model in explicit_refs:
        cross_project_connections.append({
            "source_project": target_project,
            "source_model": target_model,
            "target_project": source_project,
            "target_model": source_model,
            "explicit": True
            })
            
    # Define additional cross-project connections if needed
    hard_coded_connections = [
        # claims_project stg_customer references customer_project stg_customer
        {"source_project": "customer_project", "source_model": "stg_customer", 
         "target_project": "claims_project", "target_model": "stg_customer"},
                    
        # claims_project stg_policy references policy_project stg_policy
        {"source_project": "policy_project", "source_model": "stg_policy", 
         "target_project": "claims_project", "target_model": "stg_policy"},
                        
        # policy_project stg_customer references customer_project stg_customer
        {"source_project": "customer_project", "source_model": "stg_customer", 
         "target_project": "policy_project", "target_model": "stg_customer"},
                            
        # Add explicit dim_customer connections
        # customer_project dim_customer references stg_customer
        {"source_project": "customer_project", "source_model": "stg_customer", 
         "target_project": "customer_project", "target_model": "dim_customer"},
                                
        # claims_project references customer_project dim_customer
        {"source_project": "customer_project", "source_model": "dim_customer", 
         "target_project": "claims_project", "target_model": "dim_customer"},
    
        # policy_project references customer_project dim_customer
        {"source_project": "customer_project", "source_model": "dim_customer", 
         "target_project": "policy_project", "target_model": "dim_customer"},
    ]
        
    # Add the hard-coded connections that aren't already in the explicit list
    for conn in hard_coded_connections:
        source_project = conn["source_project"]
        source_model = conn["source_model"]
        target_project = conn["target_project"]
        target_model = conn["target_model"]
            
        # Check if this connection already exists in explicit refs
        exists = False
        for explicit_conn in cross_project_connections:
            if (explicit_conn["source_project"] == source_project and
                explicit_conn["source_model"] == source_model and
                explicit_conn["target_project"] == target_project and
                explicit_conn["target_model"] == target_model):
                exists = True
                break
            
        if not exists:
            conn["explicit"] = False
            cross_project_connections.append(conn)
                
    # Add these connections to the lineage data
    new_connections = []
    for conn in cross_project_connections:
        source_project = conn["source_project"]
        source_model = conn["source_model"]
        target_project = conn["target_project"]
        target_model = conn["target_model"]
        is_explicit = conn.get("explicit", False)
                
        # Skip if we can't find the models
        if (source_project not in model_lookup or 
            source_model not in model_lookup[source_project] or
            target_project not in model_lookup or
            target_model not in model_lookup[target_project]):
            print(f"Skipping {source_model} ({source_project}) -> {target_model} ({target_project}): Models not found")
            continue
    
        source_id = model_lookup[source_project][source_model]
        target_id = model_lookup[target_project][target_model]
        
        # Check if this connection already exists
        connection_exists = False
        for existing_conn in lineage:
            if existing_conn.get("source") == source_id and existing_conn.get("target") == target_id:
                connection_exists = True
                break
        
        # Add the connection if it doesn't exist
        if not connection_exists:
            new_connection = {
                "source": source_id,
                "target": target_id,
                "cross_project": True  # Mark as cross-project for clarity
            }
            new_connections.append(new_connection)
            lineage.append(new_connection)
            explicit_tag = "explicit" if is_explicit else "implicit"
            print(f"Added {explicit_tag} connection: {source_model} ({source_project}) -> {target_model} ({target_project})")
    
    # Save the updated metadata
    if new_connections:
        try:
            print(f"Saving {len(new_connections)} new connections to metadata file")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            print("Successfully updated metadata file")
        except Exception as e:
            print(f"Error saving metadata file: {e}")
    else:
        print("No new connections to add")

if __name__ == "__main__":
    fix_cross_project_lineage() 