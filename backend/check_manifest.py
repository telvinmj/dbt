import json
import sys
import os

def check_model_deps(manifest_path, model_name):
    """Check dependencies for a specific model by name in a manifest file"""
    
    if not os.path.exists(manifest_path):
        print(f"Manifest file not found at {manifest_path}")
        return
    
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', {})
        
        # Find all models with the given name
        matching_models = {}
        
        for node_id, node in nodes.items():
            if node.get('resource_type') == 'model' and node.get('name') == model_name:
                matching_models[node_id] = node
        
        if not matching_models:
            print(f"Model '{model_name}' not found in manifest")
            return
        
        print(f"Found {len(matching_models)} instances of '{model_name}':")
        
        # Check dependencies for each instance of the model
        for node_id, node in matching_models.items():
            print(f"\n=== {model_name} (ID: {node_id}) ===")
            
            # Get depends_on relationships
            if 'depends_on' in node and 'nodes' in node['depends_on']:
                depends_on = node['depends_on']['nodes']
                print(f"Depends on ({len(depends_on)} nodes):")
                
                for dependency in depends_on:
                    dep_node = nodes.get(dependency)
                    if dep_node:
                        print(f"  - {dep_node.get('name', 'Unknown')} ({dependency}), type: {dep_node.get('resource_type', 'Unknown')}")
                    else:
                        print(f"  - Unknown ({dependency})")
            else:
                print("No dependencies found")
            
            # Find models that depend on this model
            dependent_models = []
            for other_id, other_node in nodes.items():
                if 'depends_on' in other_node and 'nodes' in other_node['depends_on']:
                    if node_id in other_node['depends_on']['nodes']:
                        dependent_models.append((other_id, other_node))
            
            if dependent_models:
                print(f"\nDepended on by ({len(dependent_models)} nodes):")
                for dep_id, dep_node in dependent_models:
                    print(f"  - {dep_node.get('name', 'Unknown')} ({dep_id}), type: {dep_node.get('resource_type', 'Unknown')}")
            else:
                print("\nNo models depend on this model")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python check_manifest.py <manifest_path> <model_name>")
        sys.exit(1)
    
    manifest_path = sys.argv[1]
    model_name = sys.argv[2]
    check_model_deps(manifest_path, model_name) 