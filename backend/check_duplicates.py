import json
import os

def check_duplicates():
    """Check for duplicate model IDs in the metadata"""
    metadata_path = os.path.join('exports', 'uni_metadata.json')
    
    if not os.path.exists(metadata_path):
        print(f"Metadata file not found at {metadata_path}")
        return
    
    try:
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        models = data.get('models', [])
        
        # Check for duplicate model IDs
        model_ids = [m.get('id') for m in models]
        unique_ids = set(model_ids)
        
        print(f"Total models: {len(model_ids)}")
        print(f"Unique model IDs: {len(unique_ids)}")
        
        # Find duplicate IDs
        duplicate_ids = set()
        for id in model_ids:
            if model_ids.count(id) > 1:
                duplicate_ids.add(id)
        
        print(f"Duplicate IDs: {duplicate_ids}")
        
        # Print all models by ID
        print("\nModels by ID:")
        for model in models:
            model_id = model.get('id')
            model_name = model.get('name', 'Unknown')
            project = model.get('project', 'Unknown')
            print(f"{model_id}: {model_name} ({project})")
        
        # Check for models with the same name but different IDs
        model_names = {}
        for model in models:
            name = model.get('name')
            if name not in model_names:
                model_names[name] = []
            model_names[name].append({
                'id': model.get('id'),
                'project': model.get('project')
            })
        
        print("\nModels with the same name in different projects:")
        for name, instances in model_names.items():
            if len(instances) > 1:
                print(f"{name}:")
                for instance in instances:
                    print(f"  - ID: {instance['id']}, Project: {instance['project']}")
            
    except Exception as e:
        print(f"Error reading metadata: {str(e)}")

if __name__ == "__main__":
    check_duplicates() 