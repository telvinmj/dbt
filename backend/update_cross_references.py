#!/usr/bin/env python3
import os
import re
import glob
from collections import defaultdict

def get_projects_and_models():
    """Build a mapping of projects, their models, and which project owns each model originally."""
    projects_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbt_project_3")
    
    # Map of model name to originating project
    model_to_project = {}
    project_models = defaultdict(list)
    
    # Find all SQL model files
    for project_dir in glob.glob(f"{projects_dir}/*_project"):
        if not os.path.isdir(project_dir):
            continue
            
        project_name = os.path.basename(project_dir)
        
        # Find all SQL files in this project's models directory
        sql_files = glob.glob(f"{project_dir}/models/**/*.sql", recursive=True)
        for sql_file in sql_files:
            model_name = os.path.basename(sql_file).replace('.sql', '')
            
            # Add to mappings
            model_to_project[model_name] = project_name
            project_models[project_name].append(model_name)
    
    return model_to_project, project_models

def update_cross_references():
    """
    Update SQL models to use explicit cross-project references for shared models.
    This scans SQL files for ref() calls and updates them to ref('model', 'project') 
    format when referencing models from another project.
    """
    projects_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dbt_project_3")
    print(f"Scanning projects in: {projects_dir}")
    
    # Get model-to-project mappings
    model_to_project, project_models = get_projects_and_models()
    
    # Print summary
    print("\nProjects and models:")
    for project, models in project_models.items():
        print(f"{project}: {', '.join(models)}")
    
    # Regular expressions for finding and updating ref() calls
    ref_pattern = r"({{\s*ref\s*\(\s*'([^']+)'\s*\)\s*}})"
    
    # Track what we've modified
    modified_files = []
    skipped_files = []
    
    # Find all SQL files
    sql_files = glob.glob(f"{projects_dir}/**/*.sql", recursive=True)
    print(f"\nFound {len(sql_files)} SQL files")
    
    for sql_file in sql_files:
        # Determine which project this SQL file belongs to
        file_path_parts = sql_file.split('/')
        project_idx = next((i for i, part in enumerate(file_path_parts) if part.endswith('_project')), None)
        
        if project_idx is None:
            print(f"Skipping file not in a project: {sql_file}")
            skipped_files.append(sql_file)
            continue
            
        current_project = file_path_parts[project_idx]
        model_name = os.path.basename(sql_file).replace('.sql', '')
        
        # Read the file
        with open(sql_file, 'r') as f:
            content = f.read()
        
        # Find all ref() calls
        matches = re.findall(ref_pattern, content)
        
        # Track if we need to modify this file
        file_modified = False
        
        for full_match, referenced_model in matches:
            # Skip if this is already a cross-project reference
            if "', '" in full_match:
                continue
                
            # Determine if this is a cross-project reference
            if referenced_model in model_to_project:
                referenced_project = model_to_project[referenced_model]
                
                # If referencing a model from another project, update the reference
                if referenced_project != current_project:
                    replacement = f"{{{{ ref('{referenced_model}', '{referenced_project}') }}}}"
                    content = content.replace(full_match, replacement)
                    print(f"In {model_name} ({current_project}): {full_match} -> {replacement}")
                    file_modified = True
        
        # Write back the modified file
        if file_modified:
            with open(sql_file, 'w') as f:
                f.write(content)
            modified_files.append(sql_file)
    
    # Print summary
    print(f"\nModified {len(modified_files)} files")
    print(f"Skipped {len(skipped_files)} files")
    
    if modified_files:
        print("\nModified files:")
        for file in modified_files:
            print(f"- {os.path.relpath(file, projects_dir)}")

if __name__ == "__main__":
    update_cross_references() 