import json

# Load the metadata file
with open('./exports/uni_metadata.json', 'r') as f:
    data = json.load(f)

# Get models and lineage
models = data['models']
lineage = data['lineage']

# Print model information
print("\n=== Models by ID ===")
for model in models:
    print(f"ID: {model['id']}, Name: {model['name']}, Project: {model['project']}")

# Print lineage information
print("\n=== Lineage Connections ===")
model_lookup = {model['id']: f"{model['name']} ({model['project']})" for model in models}

for link in lineage:
    source_id = link['source']
    target_id = link['target']
    source_name = model_lookup.get(source_id, f"Unknown ({source_id})")
    target_name = model_lookup.get(target_id, f"Unknown ({target_id})")
    print(f"{source_name} --> {target_name}")

# Check for the stg_claim model specifically
print("\n=== stg_claim Connections ===")
stg_claim_ids = [model['id'] for model in models if model['name'] == 'stg_claim']
for stg_id in stg_claim_ids:
    # Upstream connections (models that stg_claim depends on)
    upstream = []
    for link in lineage:
        if link['target'] == stg_id:
            source_id = link['source']
            upstream.append(model_lookup.get(source_id, f"Unknown ({source_id})"))
    
    # Downstream connections (models that depend on stg_claim)
    downstream = []
    for link in lineage:
        if link['source'] == stg_id:
            target_id = link['target']
            downstream.append(model_lookup.get(target_id, f"Unknown ({target_id})"))
            
    print(f"stg_claim ID: {stg_id}")
    print(f"  Upstream (depends on): {', '.join(upstream) if upstream else 'None'}")
    print(f"  Downstream (depended on by): {', '.join(downstream) if downstream else 'None'}") 