#!/usr/bin/env python3
import json
import os

def check_cross_project_references():
    """Check for cross-project references in the metadata file"""
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "uni_metadata.json")
    
    print(f"Reading metadata from: {metadata_path}")
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        return
    
    # Check cross-project references in lineage data
    lineage = metadata.get("lineage", [])
    
    # Create model lookup for easy reference
    model_lookup = {}
    for model in metadata.get("models", []):
        model_id = model.get("id")
        if model_id:
            model_lookup[model_id] = {
                "name": model.get("name", "Unknown"),
                "project": model.get("project", "Unknown")
            }
    
    # Count cross-project references
    cross_project_references = []
    inter_project_counts = {}
    
    for conn in lineage:
        source_id = conn.get("source")
        target_id = conn.get("target")
        
        source_info = model_lookup.get(source_id, {"name": "Unknown", "project": "Unknown"})
        target_info = model_lookup.get(target_id, {"name": "Unknown", "project": "Unknown"})
        
        source_project = source_info["project"]
        target_project = target_info["project"]
        
        # Check if this is a cross-project reference
        if source_project != target_project:
            reference = {
                "source_id": source_id,
                "source_name": source_info["name"],
                "source_project": source_project,
                "target_id": target_id,
                "target_name": target_info["name"],
                "target_project": target_project
            }
            cross_project_references.append(reference)
            
            # Track inter-project dependency counts
            key = f"{source_project} -> {target_project}"
            inter_project_counts[key] = inter_project_counts.get(key, 0) + 1
    
    # Print results
    print(f"\nFound {len(cross_project_references)} cross-project references")
    
    if cross_project_references:
        print("\nCross-project references:")
        for ref in cross_project_references:
            print(f"- {ref['source_name']} ({ref['source_project']}) -> {ref['target_name']} ({ref['target_project']})")
        
        print("\nInter-project dependency counts:")
        for conn, count in inter_project_counts.items():
            print(f"- {conn}: {count} references")
    else:
        print("No cross-project references found.")
    
    # Check for direct references in the model SQL (a more thorough check)
    print("\nChecking for project references in SQL code...")
    
    ref_pattern_counts = {}
    
    for model in metadata.get("models", []):
        model_id = model.get("id")
        model_name = model.get("name")
        project = model.get("project")
        sql = model.get("sql", "")
        
        # Analyze SQL for ref() calls with project specifications
        if "ref(" in sql:
            # Count references to other projects
            for other_project in [p["id"] for p in metadata.get("projects", []) if p["id"] != project]:
                if f"ref('{other_project}" in sql or f'ref("{other_project}' in sql:
                    key = f"{project} -> {other_project}"
                    ref_pattern_counts[key] = ref_pattern_counts.get(key, 0) + 1
    
    if ref_pattern_counts:
        print("\nProject references found in SQL code:")
        for reference, count in ref_pattern_counts.items():
            print(f"- {reference}: {count} references")
    else:
        print("No direct project references found in SQL code.")
        
    # Check for package references in dbt_project.yml files
    print("\nChecking for dependencies in dbt_project.yml files...")
    projects_dir = os.environ.get("DBT_PROJECTS_DIR", "/Users/telvin/Desktop/dbt/dbt_project_3")
    
    for project_dir in os.listdir(projects_dir):
        packages_path = os.path.join(projects_dir, project_dir, "packages.yml")
        
        if os.path.exists(packages_path):
            try:
                print(f"\nFound packages.yml for {project_dir}:")
                with open(packages_path, "r") as f:
                    for line in f:
                        if "local:" in line:
                            print(f"  {line.strip()}")
            except Exception as e:
                print(f"Error reading packages.yml for {project_dir}: {e}")

if __name__ == "__main__":
    check_cross_project_references() 