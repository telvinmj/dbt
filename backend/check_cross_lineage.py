#!/usr/bin/env python3
import json
import os
import glob
import re

def check_cross_project_lineage():
    """
    Check for cross-project references in SQL models and compare with metadata lineage.
    Helps identify missing lineage connections between projects.
    """
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "uni_metadata.json")
    dbt_project_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbt_project_3")
    
    print(f"Reading metadata from: {metadata_path}")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Extract models and lineage data
    models = metadata.get("models", [])
    lineage = metadata.get("lineage", [])
    
    # Create lookup dictionaries for easier reference
    model_lookup = {}
    for model in models:
        model_id = model.get("id")
        if model_id:
            model_lookup[model_id] = model
    
    # Regular expression to find both explicit and implicit cross-project references
    ref_patterns = [
        # Explicit cross-project ref: ref('model_name', 'project_name')
        r"{{\s*ref\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)\s*}}",
        # Source references: source('project_name', 'model_name')
        r"{{\s*source\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)\s*}}"
    ]
    
    # Track found references
    explicit_refs = []
    source_refs = []
    
    # Find SQL files in the project
    sql_files = glob.glob(f"{dbt_project_dir}/**/models/**/*.sql", recursive=True)
    for sql_file in sql_files:
        # Extract project name from path
        parts = sql_file.split('/')
        try:
            project_idx = parts.index(next(p for p in parts if p.endswith('_project')))
            source_project = parts[project_idx]
        except (StopIteration, ValueError):
            continue
        
        model_name = os.path.basename(sql_file).replace('.sql', '')
        
        # Skip if it's not a model of interest
        if not model_name:
            continue
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
            
            # Check for explicit ref calls
            for match in re.finditer(ref_patterns[0], sql_content):
                target_model, target_project = match.groups()
                if target_project != source_project:
                    explicit_refs.append((source_project, model_name, target_project, target_model))
            
            # Check for source references
            for match in re.finditer(ref_patterns[1], sql_content):
                target_project, target_model = match.groups()
                if target_project != source_project:
                    source_refs.append((source_project, model_name, target_project, target_model))
    
    # Report findings
    print("\n=== Explicit Cross-Project References ===")
    if explicit_refs:
        for source_project, source_model, target_project, target_model in explicit_refs:
            print(f"{source_project}.{source_model} -> {target_project}.{target_model}")
    else:
        print("No explicit cross-project references found")
    
    print("\n=== Source References ===")
    if source_refs:
        for source_project, source_model, target_project, target_model in source_refs:
            print(f"{source_project}.{source_model} -> {target_project}.{target_model}")
    else:
        print("No source references found")
    
    # Check for dimension models referenced across projects
    dim_models = [m for m in models if m.get("name", "").startswith("dim_")]
    dim_model_names = set(m.get("name") for m in dim_models)
    
    print("\n=== Dimension Models Referenced Across Projects ===")
    for dim_name in dim_model_names:
        projects_with_dim = set(m.get("project") for m in models if m.get("name") == dim_name)
        if len(projects_with_dim) > 1:
            print(f"{dim_name} appears in projects: {', '.join(sorted(projects_with_dim))}")
            
            # Find the home project (where it should be defined)
            entity = dim_name.split('_', 1)[1] if '_' in dim_name else ""
            home_project = next((p for p in projects_with_dim if entity in p), None)
            
            if home_project:
                print(f"  Home project should be: {home_project}")
    
    print("\nRun fix_cross_lineage.py to add missing connections.")

if __name__ == "__main__":
    check_cross_project_lineage() 