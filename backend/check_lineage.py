#!/usr/bin/env python
# check_lineage.py

from services.metadata_service import MetadataService

def main():
    # Initialize the metadata service
    m = MetadataService()
    
    # Check all models
    all_models = m.get_models()
    
    # Get staging models
    print('=== STAGING MODELS ===')
    staging_models = [model for model in all_models if model['name'].startswith('stg_')]
    for model in staging_models:
        model_id = model['id']
        model_name = model['name']
        project = model['project']
        
        try:
            model_with_lineage = m.get_model_with_lineage(model_id)
            upstream_count = len(model_with_lineage.get('upstream', []))
            downstream_count = len(model_with_lineage.get('downstream', []))
            
            print(f"{model_name} (Project: {project}) - ID: {model_id}")
            print(f"  Upstream: {upstream_count}")
            
            if downstream_count > 0:
                print(f"  Downstream: {downstream_count}")
                for down in model_with_lineage.get('downstream', []):
                    print(f"    - {down['name']} (Project: {down['project']})")
            else:
                print("  Downstream: None (No lineage connections)")
            print()
        except Exception as e:
            print(f"Error processing {model_name}: {str(e)}")
    
    # Get intermediate models
    print('\n=== INTERMEDIATE MODELS ===')
    int_models = [model for model in all_models if model['name'].startswith('int_')]
    for model in int_models:
        model_id = model['id']
        model_name = model['name']
        project = model['project']
        
        try:
            model_with_lineage = m.get_model_with_lineage(model_id)
            upstream_count = len(model_with_lineage.get('upstream', []))
            downstream_count = len(model_with_lineage.get('downstream', []))
            
            print(f"{model_name} (Project: {project}) - ID: {model_id}")
            
            if upstream_count > 0:
                print(f"  Upstream: {upstream_count}")
                for up in model_with_lineage.get('upstream', []):
                    print(f"    - {up['name']} (Project: {up['project']})")
            else:
                print("  Upstream: None (No lineage connections)")
                
            if downstream_count > 0:
                print(f"  Downstream: {downstream_count}")
                for down in model_with_lineage.get('downstream', []):
                    print(f"    - {down['name']} (Project: {down['project']})")
            else:
                print("  Downstream: None (No lineage connections)")
            print()
        except Exception as e:
            print(f"Error processing {model_name}: {str(e)}")
    
    # Get mart models
    print('\n=== MART MODELS ===')
    mart_models = [model for model in all_models if model['name'].startswith('mart_')]
    for model in mart_models:
        model_id = model['id']
        model_name = model['name']
        project = model['project']
        
        try:
            model_with_lineage = m.get_model_with_lineage(model_id)
            upstream_count = len(model_with_lineage.get('upstream', []))
            downstream_count = len(model_with_lineage.get('downstream', []))
            
            print(f"{model_name} (Project: {project}) - ID: {model_id}")
            
            if upstream_count > 0:
                print(f"  Upstream: {upstream_count}")
                for up in model_with_lineage.get('upstream', []):
                    print(f"    - {up['name']} (Project: {up['project']})")
            else:
                print("  Upstream: None (No lineage connections)")
                
            if downstream_count > 0:
                print(f"  Downstream: {downstream_count}")
                for down in model_with_lineage.get('downstream', []):
                    print(f"    - {down['name']} (Project: {down['project']})")
            else:
                print("  Downstream: None (No lineage connections)")
            print()
        except Exception as e:
            print(f"Error processing {model_name}: {str(e)}")
    
    # Check cross-project lineage
    print('\n=== CROSS-PROJECT LINEAGE ===')
    lineage = m.get_lineage()
    cross_project_links = []
    
    for link in lineage:
        source_id = link['source']
        target_id = link['target']
        
        source_model = next((m for m in all_models if m['id'] == source_id), None)
        target_model = next((m for m in all_models if m['id'] == target_id), None)
        
        if source_model and target_model and source_model['project'] != target_model['project']:
            cross_project_links.append({
                'source': source_model,
                'target': target_model
            })
    
    if cross_project_links:
        print(f"Found {len(cross_project_links)} cross-project lineage connections:")
        for link in cross_project_links:
            print(f"  {link['source']['name']} (Project: {link['source']['project']}) -> {link['target']['name']} (Project: {link['target']['project']})")
    else:
        print("No cross-project lineage connections found.")

if __name__ == "__main__":
    main() 