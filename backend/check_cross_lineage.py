import json
import os

# Load the metadata file
metadata_file = os.path.join('exports', 'uni_metadata.json')
with open(metadata_file, 'r') as f:
    data = json.load(f)

# Count total lineage connections
total_lineage = len(data.get('lineage', []))
print(f"Total lineage connections: {total_lineage}")

# Find cross-project lineage connections
cross_project_lineage = []
for link in data.get('lineage', []):
    source_id = link.get('source', '')
    target_id = link.get('target', '')
    
    # Extract project names from model IDs
    source_parts = source_id.split('_')
    target_parts = target_id.split('_')
    
    if len(source_parts) > 1 and len(target_parts) > 1:
        source_project = source_parts[0]
        target_project = target_parts[0]
        
        if source_project != target_project:
            cross_project_lineage.append((source_id, target_id))

print(f"Cross-project lineage connections: {len(cross_project_lineage)}")

# Print some examples
print("\nExamples of cross-project connections:")
for i, (source, target) in enumerate(cross_project_lineage[:5]):
    print(f"{i+1}. {source} -> {target}")

# Print by source project
cross_by_project = {}
for source, target in cross_project_lineage:
    source_project = source.split('_')[0]
    target_project = target.split('_')[0]
    key = f"{source_project} -> {target_project}"
    
    if key not in cross_by_project:
        cross_by_project[key] = 0
    cross_by_project[key] += 1

print("\nBreakdown by project connections:")
for connection, count in cross_by_project.items():
    print(f"{connection}: {count} connections") 