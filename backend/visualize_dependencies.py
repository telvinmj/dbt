#!/usr/bin/env python3
import json
import os
from collections import defaultdict

def visualize_dependencies():
    """
    Visualize cross-project dependencies to make them easier to understand.
    This generates a text-based visualization showing connections between models in different projects.
    """
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "uni_metadata.json")
    
    print(f"Reading metadata from: {metadata_path}")
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        return
    
    # Extract models and lineage
    models = metadata.get("models", [])
    lineage = metadata.get("lineage", [])
    
    # Create model lookup
    model_lookup = {}
    for model in models:
        model_id = model.get("id")
        if model_id:
            model_lookup[model_id] = model
    
    # Group connections by project
    project_connections = defaultdict(list)
    cross_project_connections = []
    
    for connection in lineage:
        source_id = connection.get("source")
        target_id = connection.get("target")
        
        if not source_id or not target_id:
            continue
            
        source_model = model_lookup.get(source_id)
        target_model = model_lookup.get(target_id)
        
        if not source_model or not target_model:
            continue
            
        source_project = source_model.get("project")
        target_project = target_model.get("project")
        
        if source_project == target_project:
            project_connections[source_project].append((source_model, target_model))
        else:
            cross_project_connections.append((source_model, target_model))
    
    # Print project summary
    print("\n=== Project Summary ===")
    projects = set(model.get("project") for model in models if model.get("project"))
    for project in sorted(projects):
        project_models = [m for m in models if m.get("project") == project]
        print(f"{project}: {len(project_models)} models")
    
    # Print cross-project dependencies
    print("\n=== Cross-Project Dependencies ===")
    for source_model, target_model in cross_project_connections:
        source_project = source_model.get("project")
        source_name = source_model.get("name")
        target_project = target_model.get("project")
        target_name = target_model.get("name")
        
        print(f"{source_project}.{source_name} → {target_project}.{target_name}")
    
    # Generate a dependency graph
    print("\n=== Project Dependency Graph ===")
    project_deps = defaultdict(set)
    for source_model, target_model in cross_project_connections:
        source_project = source_model.get("project")
        target_project = target_model.get("project")
        project_deps[source_project].add(target_project)
    
    # Visualize the project dependencies
    for source_project in sorted(project_deps.keys()):
        print(f"{source_project} depends on:")
        for target_project in sorted(project_deps[source_project]):
            print(f"  └─ {target_project}")
    
    # Generate an ASCII dependency tree
    print("\n=== Cross-Project Dependency Tree ===")
    
    def print_tree(project, indent="", visited=None):
        if visited is None:
            visited = set()
        
        if project in visited:
            print(f"{indent}└─ {project} (circular dependency)")
            return
        
        visited.add(project)
        
        # Get models in this project
        project_models = [m for m in models if m.get("project") == project]
        model_names = sorted([m.get("name") for m in project_models if m.get("name")])
        
        print(f"{indent}└─ {project}")
        indent += "   "
        
        # Print a few sample models (not all to avoid clutter)
        if model_names:
            print(f"{indent}└─ Models ({len(model_names)} total):")
            for name in model_names[:3]:  # Show only first 3 models
                print(f"{indent}   └─ {name}")
            if len(model_names) > 3:
                print(f"{indent}   └─ ... {len(model_names) - 3} more")
        
        # Print dependencies
        deps = [p for p in project_deps.get(project, set())]
        if deps:
            print(f"{indent}└─ Dependencies:")
            for i, dep in enumerate(sorted(deps)):
                is_last = i == len(deps) - 1
                if is_last:
                    print(f"{indent}   └─ {dep}")
                else:
                    print(f"{indent}   ├─ {dep}")
    
    # Find root projects (those not depended on by others)
    all_projects = set(model.get("project") for model in models if model.get("project"))
    dependent_projects = set()
    for deps in project_deps.values():
        dependent_projects.update(deps)
    
    root_projects = all_projects - dependent_projects
    
    # Print the dependency tree starting from root projects
    for project in sorted(root_projects):
        print_tree(project)

if __name__ == "__main__":
    visualize_dependencies() 