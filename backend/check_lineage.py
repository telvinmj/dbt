#!/usr/bin/env python
# check_lineage.py

import json
import os

def check_lineage():
    """Check the lineage connections in the metadata file"""
    metadata_path = os.path.join('exports', 'uni_metadata.json')
    
    if not os.path.exists(metadata_path):
        print(f"Metadata file not found at {metadata_path}")
        return
    
    try:
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        projects = data.get('projects', [])
        models = data.get('models', [])
        lineage = data.get('lineage', [])
        
        print(f"Projects: {len(projects)}")
        print(f"Models: {len(models)}")
        print(f"Lineage connections: {len(lineage)}")
        
        # Create model lookup dictionary for easy reference
        model_lookup = {}
        for model in models:
            model_id = model.get('id')
            if model_id:
                model_lookup[model_id] = {
                    'name': model.get('name', 'Unknown'),
                    'project': model.get('project', 'Unknown')
                }
        
        print("\nLineage connections:")
        for i, connection in enumerate(lineage):
            source_id = connection.get('source')
            target_id = connection.get('target')
            source_info = model_lookup.get(source_id, {'name': 'Unknown', 'project': 'Unknown'})
            target_info = model_lookup.get(target_id, {'name': 'Unknown', 'project': 'Unknown'})
            
            print(f"{i+1}. {source_info['name']} ({source_id}) -> {target_info['name']} ({target_id})")
            print(f"   Project: {source_info['project']} -> {target_info['project']}")
        
        print("\nModels without upstream connections:")
        models_without_upstream = set(model.get('id') for model in models) - set(conn.get('target') for conn in lineage)
        for model_id in models_without_upstream:
            if model_id in model_lookup:
                print(f"- {model_lookup[model_id]['name']} ({model_id})")
        
        print("\nModels without downstream connections:")
        models_without_downstream = set(model.get('id') for model in models) - set(conn.get('source') for conn in lineage)
        for model_id in models_without_downstream:
            if model_id in model_lookup:
                print(f"- {model_lookup[model_id]['name']} ({model_id})")
                
    except Exception as e:
        print(f"Error reading metadata: {str(e)}")

if __name__ == "__main__":
    check_lineage() 