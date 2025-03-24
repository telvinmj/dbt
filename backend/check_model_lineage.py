import json
import os
import sys

def check_model_lineage(model_name):
    """Check lineage for a specific model by name"""
    metadata_path = os.path.join('exports', 'uni_metadata.json')
    
    if not os.path.exists(metadata_path):
        print(f"Metadata file not found at {metadata_path}")
        return
    
    try:
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        models = data.get('models', [])
        lineage = data.get('lineage', [])
        
        # Find all models with the given name
        matching_models = [model for model in models if model.get('name') == model_name]
        
        if not matching_models:
            print(f"Model '{model_name}' not found in any project")
            return
        
        print(f"Found {len(matching_models)} instances of '{model_name}':")
        
        # Create a lookup for all models by ID
        model_lookup = {}
        for model in models:
            model_id = model.get('id')
            if model_id:
                model_lookup[model_id] = {
                    'name': model.get('name', 'Unknown'),
                    'project': model.get('project', 'Unknown')
                }
        
        # Check lineage for each instance of the model
        for model in matching_models:
            model_id = model.get('id')
            project = model.get('project', 'Unknown')
            
            print(f"\n=== {model_name} (ID: {model_id}) in project: {project} ===")
            
            # Find upstream models (models that this model depends on)
            upstream = []
            for link in lineage:
                if link.get('target') == model_id:
                    source_id = link.get('source')
                    source_info = model_lookup.get(source_id, {'name': 'Unknown', 'project': 'Unknown'})
                    upstream.append(f"{source_info['name']} ({source_id}) in {source_info['project']}")
            
            # Find downstream models (models that depend on this model)
            downstream = []
            for link in lineage:
                if link.get('source') == model_id:
                    target_id = link.get('target')
                    target_info = model_lookup.get(target_id, {'name': 'Unknown', 'project': 'Unknown'})
                    downstream.append(f"{target_info['name']} ({target_id}) in {target_info['project']}")
            
            # Print results
            if upstream:
                print("Upstream models (models that this model depends on):")
                for up in upstream:
                    print(f"  - {up}")
            else:
                print("No upstream models (this model doesn't depend on any other models)")
            
            if downstream:
                print("\nDownstream models (models that depend on this model):")
                for down in downstream:
                    print(f"  - {down}")
            else:
                print("\nNo downstream models (no other models depend on this model)")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Get model name from command line argument or use default
    model_name = sys.argv[1] if len(sys.argv) > 1 else "stg_claim"
    check_model_lineage(model_name) 