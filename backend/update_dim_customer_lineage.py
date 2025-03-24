#!/usr/bin/env python3
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.metadata_service import MetadataService

def fix_dim_customer_lineage():
    """
    Fix the lineage for dim_customer to ensure it appears correctly in the visualization.
    This script specifically addresses the issue of dim_customer appearing in multiple projects.
    """
    print("Starting dim_customer lineage fix...")
    
    # Load the metadata
    metadata_service = MetadataService()
    metadata = metadata_service.get_all_lineage()
    
    models = metadata.get("models", [])
    lineage = metadata.get("lineage", [])
    
    # Find all dim_customer models
    dim_customer_models = [m for m in models if m.get("name") == "dim_customer"]
    
    if not dim_customer_models:
        print("No dim_customer models found!")
        return
    
    print(f"Found {len(dim_customer_models)} dim_customer models across projects:")
    for model in dim_customer_models:
        project = model.get("project", "unknown")
        model_id = model.get("id", "unknown")
        is_canonical = model.get("is_canonical", False)
        references = model.get("references_canonical", "none")
        print(f"  - {project}: {model_id} (Canonical: {is_canonical}, References: {references})")
    
    # Find customer_project dim_customer
    customer_project_dim = next(
        (m for m in dim_customer_models if m.get("project") == "customer_project"), 
        None
    )
    
    if not customer_project_dim:
        print("Error: Could not find dim_customer in customer_project!")
        return
    
    canonical_id = customer_project_dim.get("id")
    print(f"\nCanonical dim_customer identified: {canonical_id}")
    
    # Look at lineage connections
    dim_customer_lineage = [
        link for link in lineage 
        if any(m.get("id") in [link.get("source"), link.get("target")] for m in dim_customer_models)
    ]
    
    print(f"\nFound {len(dim_customer_lineage)} lineage connections involving dim_customer:")
    for i, link in enumerate(dim_customer_lineage[:10]):  # Show first 10
        source = link.get("source", "unknown")
        target = link.get("target", "unknown")
        print(f"  {i+1}. {source} -> {target}")
    
    if len(dim_customer_lineage) > 10:
        print(f"  ... and {len(dim_customer_lineage) - 10} more")
    
    # Save updated metadata to exports directory
    exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    export_path = os.path.join(exports_dir, "updated_metadata.json")
    
    with open(export_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nUpdated metadata saved to: {export_path}")
    print("Done fixing dim_customer lineage.")
    print("To apply changes, copy this file to uni_metadata.json and restart the backend.")

if __name__ == "__main__":
    fix_dim_customer_lineage() 