#!/usr/bin/env python3
import json
import os

def fix_model_ids():
    """Fix model IDs in the metadata file to ensure uniqueness across projects"""
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "uni_metadata.json")
    
    print(f"Reading metadata from: {metadata_path}")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Dictionary to store the mapping from old IDs to new IDs
    id_mapping = {}
    
    # Create new model IDs (project_id_model_name)
    print("Creating new model IDs...")
    new_models = []
    for model in metadata.get("models", []):
        old_id = model["id"]
        project_id = model["project"]
        model_name = model["name"]
        
        # Generate a new unique ID
        new_id = f"{project_id}_{model_name}"
        id_mapping[old_id] = new_id
        
        # Update the model's ID
        model["id"] = new_id
        new_models.append(model)
        
        print(f"Mapped: {old_id} -> {new_id}")
    
    # Update the metadata with the new models
    metadata["models"] = new_models
    
    # Update lineage data with the new IDs
    new_lineage = []
    for lineage in metadata.get("lineage", []):
        source_id = lineage["source"]
        target_id = lineage["target"]
        
        if source_id in id_mapping and target_id in id_mapping:
            new_lineage.append({
                "source": id_mapping[source_id],
                "target": id_mapping[target_id]
            })
            print(f"Updated lineage: {source_id} -> {target_id} to {id_mapping[source_id]} -> {id_mapping[target_id]}")
    
    # Update the metadata with the new lineage
    metadata["lineage"] = new_lineage
    
    # Save the updated metadata
    print(f"Saving updated metadata to: {metadata_path}")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Done! Updated {len(new_models)} models and {len(new_lineage)} lineage relationships.")
    print("Restart the backend service to apply these changes.")

if __name__ == "__main__":
    fix_model_ids() 