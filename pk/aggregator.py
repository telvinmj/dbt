import os
import json
import yaml
import networkx as nx
import re

# Define parent directory where all dbt projects are stored
DBT_PARENT_DIR = "C:/Users/karak/dbt_cursor"

def find_dbt_projects(parent_dir):
    """Find all subdirectories containing a dbt project (with a target/manifest.json file)."""
    projects = {}
    
    # List all items in the parent directory
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        
        # Check if it's a directory
        if os.path.isdir(item_path):
            # Check if it contains a target directory with manifest.json
            target_dir = os.path.join(item_path, "target")
            manifest_path = os.path.join(target_dir, "manifest.json")
            
            if os.path.isdir(target_dir) and os.path.exists(manifest_path):
                projects[item] = target_dir
                print(f"Found dbt project: {item}")
    
    print(f"Found {len(projects)} dbt projects: {', '.join(projects.keys())}")
    return projects

def extract_column_names(columns_data):
    """Extract just the column names without any descriptions."""
    simplified_columns = {}
    if columns_data:
        for col_name in columns_data.keys():
            simplified_columns[col_name] = {"name": col_name}
    return simplified_columns

def load_metadata(project_name, project_path, metadata):
    """Loads manifest.json from a dbt project and extracts metadata."""
    manifest_path = os.path.join(project_path, "manifest.json")

    if not os.path.exists(manifest_path):
        print(f"Warning: No manifest.json found for {project_name}")
        return
    
    try:
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

        # Store raw depends_on for later cross-project resolution
        if "depends_on" not in metadata:
            metadata["depends_on"] = {}
        
        # Process models
        for node_name, node_data in manifest.get("nodes", {}).items():
            try:
                if node_data.get("resource_type") == "model":
                    model_name = node_data.get("name", "")
                    # Store with qualified name including project
                    qualified_name = f"{project_name}.{model_name}"
                    metadata["models"][model_name] = {
                        "schema": node_data.get("schema", ""),
                        "database": node_data.get("database", ""),
                        "columns": extract_column_names(node_data.get("columns", {})),
                        "original_id": node_name,  # Store the original node id for later reference
                        "project": project_name,  # Keep track of which project this came from
                        "qualified_name": qualified_name  # Store qualified name for reference resolution
                    }

                    # Store dependencies for later resolution
                    if "depends_on" in node_data and "nodes" in node_data["depends_on"]:
                        metadata["depends_on"][qualified_name] = node_data["depends_on"]["nodes"]
                        
                    # Add immediate lineage within the same project
                    if "depends_on" in node_data and "nodes" in node_data["depends_on"]:
            for dep in node_data["depends_on"]["nodes"]:
                            # For now, just add to lineage graph - we'll resolve cross-project later
                            metadata["lineage"].add_edge(dep, qualified_name)
            except Exception as e:
                print(f"Error processing node {node_name}: {e}")

        # Process sources - need different approach depending on manifest structure
        try:
            # Process source definitions
            for source_id, source_data in manifest.get("sources", {}).items():
                try:
                    source_name = source_data.get("name", "")
                    
                    # Check if tables is a dict (newer format) or list (older format)
                    tables_data = source_data.get("tables", {})
                    
                    if isinstance(tables_data, dict):
                        # Format: {"table_name": {table_details}}
                        for table_name, table_info in tables_data.items():
                            qualified_name = f"{project_name}.{table_name}"
                            metadata["sources"][qualified_name] = {
                                "schema": source_data.get("schema", ""),
                                "database": source_data.get("database", ""),
                                "columns": extract_column_names(table_info.get("columns", {})),
                                "source_name": source_name,
                                "original_id": f"source.{project_name}.{source_name}.{table_name}",
                                "project": project_name,
                                "qualified_name": qualified_name
                            }
                    elif isinstance(tables_data, list):
                        # Format: [{"name": "table_name", ...}, {...}]
                        for table in tables_data:
                            table_name = table.get("name", "")
                            if table_name:
                                qualified_name = f"{project_name}.{table_name}"
                                metadata["sources"][qualified_name] = {
                                    "schema": source_data.get("schema", ""),
                                    "database": source_data.get("database", ""),
                                    "columns": extract_column_names(table.get("columns", {})),
                                    "source_name": source_name,
                                    "original_id": f"source.{project_name}.{source_name}.{table_name}",
                                    "project": project_name,
                                    "qualified_name": qualified_name
                                }
                except Exception as e:
                    print(f"Error processing source {source_id}: {e}")
            
            # Process parent/child relationships to get source references
            if "parent_map" in manifest:
                for node_id, parent_nodes in manifest.get("parent_map", {}).items():
                    if node_id.startswith("model."):
                        # Extract model name
                        parts = node_id.split(".")
                        if len(parts) >= 3:
                            model_project = parts[1]
                            model_name = parts[2]
                            qualified_model = f"{project_name}.{model_name}"
                            
                            for parent in parent_nodes:
                                if parent.startswith("source."):
                                    # Parent is a source reference
                                    source_parts = parent.split(".")
                                    if len(source_parts) >= 4:
                                        source_project = source_parts[1]
                                        source_name = source_parts[2]
                                        table_name = source_parts[3]
                                        
                                        # Don't assume which project this source actually comes from yet
                                        # Store the reference for resolution later
                                        source_ref = f"source.{source_project}.{source_name}.{table_name}"
                                        
                                        # Add to external refs to resolve later
                                        if "external_refs" not in metadata:
                                            metadata["external_refs"] = {}
                                        if qualified_model not in metadata["external_refs"]:
                                            metadata["external_refs"][qualified_model] = []
                                        metadata["external_refs"][qualified_model].append({
                                            "ref_type": "source",
                                            "source_project": source_project,
                                            "source_name": source_name,
                                            "table_name": table_name,
                                            "original_ref": source_ref
                                        })
                                        
                                        # Add to lineage with source ref for now
                                        metadata["lineage"].add_edge(source_ref, qualified_model)
                                
                                elif parent.startswith("model."):
                                    # Parent is a model reference
                                    parent_parts = parent.split(".")
                                    if len(parent_parts) >= 3:
                                        parent_project = parent_parts[1]
                                        parent_name = parent_parts[2]
                                        
                                        # Store as external ref if from a different project
                                        if parent_project != project_name:
                                            if "external_refs" not in metadata:
                                                metadata["external_refs"] = {}
                                            if qualified_model not in metadata["external_refs"]:
                                                metadata["external_refs"][qualified_model] = []
                                            metadata["external_refs"][qualified_model].append({
                                                "ref_type": "model",
                                                "project": parent_project,
                                                "model_name": parent_name,
                                                "original_ref": parent
                                            })
                                        
                                        # Add to lineage
                                        parent_qualified = f"{parent_project}.{parent_name}"
                                        metadata["lineage"].add_edge(parent_qualified, qualified_model)
                                
            # Look for source references in models
            if "child_map" in manifest:
                for source_id, child_nodes in manifest.get("child_map", {}).items():
                    if source_id.startswith("source."):
                        source_parts = source_id.split(".")
                        if len(source_parts) >= 4:
                            source_project = source_parts[1]
                            source_name = source_parts[2]
                            table_name = source_parts[3]
                            
                            qualified_source = f"{source_project}.{table_name}"
                            
                            for child in child_nodes:
                                if child.startswith("model."):
                                    child_parts = child.split(".")
                                    if len(child_parts) >= 3:
                                        child_project = child_parts[1]
                                        child_name = child_parts[2]
                                        
                                        # Add to lineage
                                        child_qualified = f"{child_project}.{child_name}"
                                        metadata["lineage"].add_edge(qualified_source, child_qualified)
                                
                        
        except Exception as e:
            print(f"Error processing sources or relationships: {e}")
                
    except Exception as e:
        print(f"Error loading manifest for {project_name}: {e}")

def resolve_cross_project_refs(metadata):
    """Resolve cross-project references and update lineage."""
    print("Resolving cross-project references...")
    
    # Create a mapping of original node IDs to qualified names
    node_mapping = {}
    
    # Map models
    for model_name, model_data in metadata["models"].items():
        if "original_id" in model_data:
            node_mapping[model_data["original_id"]] = model_data.get("qualified_name")
    
    # Map sources
    for source_name, source_data in metadata["sources"].items():
        if "original_id" in source_data:
            node_mapping[source_data["original_id"]] = source_data.get("qualified_name")
    
    # Build a map of source references by pattern
    source_ref_map = {}
    for source_qual_name, source_data in metadata["sources"].items():
        if "source_name" in source_data and "project" in source_data:
            # Create patterns that might match this source
            project = source_data["project"]
            source_name = source_data["source_name"]
            table_name = source_qual_name.split(".")[-1]
            
            # Pattern for exact source reference
            exact_pattern = f"source.{project}.{source_name}.{table_name}"
            source_ref_map[exact_pattern] = source_qual_name
            
            # Pattern for any project referencing this source name/table
            generic_pattern = f"source.*.{source_name}.{table_name}"
            source_ref_map[generic_pattern] = source_qual_name
    
    # Process external refs
    if "external_refs" in metadata:
        for model, refs in metadata["external_refs"].items():
            for ref in refs:
                if ref["ref_type"] == "source":
                    source_ref = f"source.{ref['source_project']}.{ref['source_name']}.{ref['table_name']}"
                    # Try to find matching source
                    found = False
                    
                    # Look for exact match first
                    if source_ref in source_ref_map:
                        target_source = source_ref_map[source_ref]
                        # Add to lineage
                        metadata["lineage"].add_edge(target_source, model)
                        found = True
                    else:
                        # Try with wildcard matching
                        generic_ref = f"source.*.{ref['source_name']}.{ref['table_name']}"
                        if generic_ref in source_ref_map:
                            target_source = source_ref_map[generic_ref]
                            # Add to lineage
                            metadata["lineage"].add_edge(target_source, model)
                            found = True
                    
                    if not found:
                        print(f"Warning: Could not resolve source reference {source_ref} for model {model}")
                
                elif ref["ref_type"] == "model":
                    # Try to find the referenced model
                    ref_project = ref["project"] 
                    ref_model = ref["model_name"]
                    ref_qualified = f"{ref_project}.{ref_model}"
                    
                    # Check if model exists
                    found = False
                    for model_name, model_data in metadata["models"].items():
                        if model_data.get("qualified_name") == ref_qualified:
                            # Add to lineage
                            metadata["lineage"].add_edge(ref_qualified, model)
                            found = True
                            break
                    
                    if not found:
                        print(f"Warning: Could not resolve model reference {ref_qualified} for model {model}")

def simplify_graph(metadata):
    """Simplify the graph to use unqualified names for improved readability."""
    original_lineage = metadata["lineage"]
    simplified_lineage = nx.DiGraph()
    
    # Create mappings
    node_to_simple = {}
    simple_to_node = {}
    
    # Process models
    for model_name, model_data in metadata["models"].items():
        qualified_name = model_data.get("qualified_name")
        if qualified_name:
            node_to_simple[qualified_name] = model_name
            simple_to_node[model_name] = qualified_name
    
    # Process sources
    for source_qualified, source_data in metadata["sources"].items():
        simple_name = source_qualified.split(".")[-1]  # Just the table name
        node_to_simple[source_qualified] = simple_name
        # Note: There might be duplicate simple names for sources - that's OK for visualization
        simple_to_node[simple_name] = source_qualified
    
    # Process each edge in the original lineage
    for source, target in original_lineage.edges():
        source_simple = node_to_simple.get(source, source)
        target_simple = node_to_simple.get(target, target)
        
        # Add the edge to the simplified lineage
        if source_simple and target_simple:
            simplified_lineage.add_edge(source_simple, target_simple)
    
    return simplified_lineage

def unify_metadata():
    """Scans all dbt projects and aggregates metadata into a unified format."""
    dbt_projects = find_dbt_projects(DBT_PARENT_DIR)

    unified_metadata = {
        "models": {},
        "sources": {},
        "lineage": nx.DiGraph()
    }

    for project, path in dbt_projects.items():
        print(f"Processing project: {project}")
        load_metadata(project, path, unified_metadata)

    # Resolve cross-project references
    resolve_cross_project_refs(unified_metadata)
    
    # Create a unified lineage graph that resolves cross-project references
    print("Creating unified lineage...")
    simplified_lineage = simplify_graph(unified_metadata)
    
    # Convert lineage graph to a serializable format
    try:
        lineage_edges = list(simplified_lineage.edges())
        # Create a simple lineage representation without labels
        unified_metadata["lineage"] = []
        for src, dst in lineage_edges:
            unified_metadata["lineage"].append({
                "from": src,
                "to": dst
            })
         
        # Simplify model structures to remove internal tracking fields
        for model_name in list(unified_metadata["models"].keys()):
            model_data = unified_metadata["models"][model_name]
            # Remove internal tracking fields
            if "original_id" in model_data:
                del model_data["original_id"]
            if "qualified_name" in model_data:
                del model_data["qualified_name"]
                
        # Simplify source references to remove tracking
        simplified_sources = {}
        for source_qualified, source_data in unified_metadata["sources"].items():
            simple_name = source_qualified.split(".")[-1]
            simplified_source = {k: v for k, v in source_data.items() if k not in ["original_id", "qualified_name"]}
            simplified_sources[simple_name] = simplified_source
        
        unified_metadata["sources"] = simplified_sources
        
        # Remove internal tracking data
        for key in ["depends_on", "external_refs"]:
            if key in unified_metadata:
                del unified_metadata[key]
                
    except Exception as e:
        print(f"Error converting lineage graph: {e}")
        unified_metadata["lineage"] = []

    # Save unified metadata directly in the parent directory
    # Save as JSON
    json_path = os.path.join(DBT_PARENT_DIR, "unified_metadata.json")
    with open(json_path, "w") as f:
        json.dump(unified_metadata, f, indent=4)

    # Save as YAML
    yaml_path = os.path.join(DBT_PARENT_DIR, "unified_metadata.yml") 
    with open(yaml_path, "w") as f:
        yaml.dump(unified_metadata, f, default_flow_style=False)

    print(f"Unified metadata successfully generated in {DBT_PARENT_DIR}")

if __name__ == "__main__":
    unify_metadata()
