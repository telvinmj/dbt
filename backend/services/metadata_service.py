# backend/services/metadata_service.py

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from .dbt_metadata_parser import parse_dbt_projects, save_metadata
from .ai_description_service import AIDescriptionService

class MetadataService:
    """Service for combining and processing dbt project metadata"""
    
    def __init__(self, dbt_projects_dir: str = "dbt_projects_2", output_dir: str = None, use_ai_descriptions: bool = True):
        # Get the base directory (parent of backend)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Set default output_dir if not provided
        if output_dir is None:
            output_dir = os.path.join(base_dir, "exports")
        
        # Make sure we're using absolute paths
        self.dbt_projects_dir = os.path.abspath(os.path.join(base_dir, "..", dbt_projects_dir))
        self.output_dir = os.path.abspath(output_dir)
        self.unified_metadata_path = os.path.join(self.output_dir, "uni_metadata.json")
        self.metadata = {}
        self.use_ai_descriptions = use_ai_descriptions
        
        # Initialize AI description service if enabled
        self.ai_service = AIDescriptionService() if use_ai_descriptions else None
        
        print(f"Initializing MetadataService:")
        print(f"- Base dir: {base_dir}")
        print(f"- Projects dir: {self.dbt_projects_dir}")
        print(f"- Output dir: {self.output_dir}")
        print(f"- Metadata path: {self.unified_metadata_path}")
        print(f"- AI descriptions: {'enabled' if use_ai_descriptions else 'disabled'}")
        
        # Create exports directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize or load the unified metadata
        self._initialize_metadata()
    
    def _initialize_metadata(self):
        """Initialize or load the unified metadata"""
        if os.path.exists(self.unified_metadata_path):
            try:
                with open(self.unified_metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                    print(f"Loaded metadata from {self.unified_metadata_path}")
                    print(f"Projects: {len(self.metadata.get('projects', []))}")
                    print(f"Models: {len(self.metadata.get('models', []))}")
                    print(f"Lineage: {len(self.metadata.get('lineage', []))}")
                    
                    # Print a sample project if available
                    if self.metadata.get('projects'):
                        print("\nSample Project:")
                        print(json.dumps(self.metadata['projects'][0], indent=2))
                    
                    # Print sample lineage if available
                    if self.metadata.get('lineage'):
                        print("\nSample Lineage Relationships:")
                        for i, lineage in enumerate(self.metadata['lineage'][:2]):
                            print(f"Lineage {i+1}: {json.dumps(lineage)}")
            except Exception as e:
                print(f"Error loading metadata: {e}")
                self.refresh()
        else:
            print(f"Metadata file not found at {self.unified_metadata_path}, creating new...")
            self.refresh()
    
    def get_project_dirs(self) -> List[str]:
        """Get all dbt project directories"""
        if not os.path.exists(self.dbt_projects_dir):
            print(f"Projects directory not found: {self.dbt_projects_dir}")
            return []
            
        return [d for d in os.listdir(self.dbt_projects_dir) 
                if os.path.isdir(os.path.join(self.dbt_projects_dir, d)) 
                and not d.startswith('.')]
    
    def _parse_dbt_projects(self) -> Dict[str, Any]:
        """Parse dbt project files and generate structured metadata"""
        projects = []
        models = []
        lineage_data = []
        model_id_map = {}  # Maps node_id to our model_id
        
        project_dirs = self.get_project_dirs()
        print(f"\nFound {len(project_dirs)} project directories: {project_dirs}")
        
        for project_dir in project_dirs:
            project_path = os.path.join(self.dbt_projects_dir, project_dir)
            
            # Look for manifest.json and catalog.json in the target directory
            manifest_path = os.path.join(project_path, "target", "manifest.json")
            catalog_path = os.path.join(project_path, "target", "catalog.json")
            
            # Skip if manifest doesn't exist
            if not os.path.exists(manifest_path):
                print(f"Skipping {project_dir}: No manifest.json found")
                continue
            
            print(f"\nProcessing project: {project_dir}")
            print(f"  Manifest path: {manifest_path}")
            print(f"  Catalog path: {catalog_path} (exists: {os.path.exists(catalog_path)})")
            
            try:
                # Load manifest.json
                with open(manifest_path, 'r') as f:
                    manifest_data = json.load(f)
                
                # Load catalog.json if it exists
                catalog_data = {}
                if os.path.exists(catalog_path):
                    with open(catalog_path, 'r') as f:
                        catalog_data = json.load(f)
                
                # Extract project name from manifest
                project_name = project_dir
                if 'metadata' in manifest_data and 'project_name' in manifest_data['metadata']:
                    project_name = manifest_data['metadata']['project_name']
                
                # Add project to projects list
                project_id = project_name.lower().replace(' ', '_')
                projects.append({
                    "id": project_id,
                    "name": project_name,
                    "description": f"{project_name} dbt project"
                })
                
                print(f"  Added project: {project_name} (id: {project_id})")
                
                # Process models
                model_count = 0
                for node_id, node in manifest_data.get('nodes', {}).items():
                    if node.get('resource_type') == 'model':
                        model_name = node.get('name', '')
                        
                        # Generate a unique ID for the model
                        model_id = f"{project_id[0]}{model_count + 1}"
                        model_id_map[node_id] = model_id
                        model_count += 1
                        
                        # Get SQL code
                        sql = ""
                        if 'compiled_sql' in node:
                            sql = node['compiled_sql']
                        elif 'raw_sql' in node:
                            sql = node['raw_sql']
                        elif 'raw_code' in node:
                            sql = node['raw_code']
                        
                        # Extract columns
                        columns = []
                        
                        # Try to get columns from catalog
                        catalog_node = None
                        if catalog_data and 'nodes' in catalog_data:
                            catalog_node = catalog_data['nodes'].get(node_id)
                        
                        if catalog_node and 'columns' in catalog_node:
                            for col_name, col_data in catalog_node['columns'].items():
                                column = {
                                    "name": col_name,
                                    "type": col_data.get('type', 'unknown'),
                                    "description": col_data.get('description', ''),
                                    "isPrimaryKey": 'primary' in col_name.lower() or col_name.lower().endswith('_id'),
                                    "isForeignKey": 'foreign' in col_name.lower() or col_name.lower().endswith('_id')
                                }
                                columns.append(column)
                        else:
                            # If no catalog, try to extract columns from SQL
                            extracted_columns = self._extract_columns_from_sql(sql)
                            for col_name in extracted_columns:
                                column = {
                                    "name": col_name,
                                    "type": "unknown",
                                    "description": "",
                                    "isPrimaryKey": 'primary' in col_name.lower() or col_name.lower().endswith('_id'),
                                    "isForeignKey": 'foreign' in col_name.lower() or col_name.lower().endswith('_id')
                                }
                                columns.append(column)
                        
                        # Create model object
                        model = {
                            "id": model_id,
                            "name": model_name,
                            "project": project_id,
                            "description": node.get('description', ''),
                            "columns": columns,
                            "sql": sql
                        }
                        
                        # Add additional model metadata from manifest
                        if 'config' in node:
                            config = node.get('config', {})
                            model["materialized"] = config.get('materialized', 'view')
                            model["schema"] = config.get('schema', node.get('schema'))
                        
                        # Add file path
                        model["file_path"] = node.get('original_file_path', 'N/A')
                        
                        # Extract database and schema if available
                        if 'database' in node:
                            model["database"] = node.get('database')
                            
                        if 'schema' in node and not model.get('schema'):
                            model["schema"] = node.get('schema')
                            
                        # Ensure we have a schema value by using the default schema if needed
                        if not model.get('schema') and 'config' in manifest_data.get('metadata', {}):
                            model["schema"] = manifest_data.get('metadata', {}).get('config', {}).get('schema')
                            
                        # Extract tags if available
                        if 'tags' in node and node.get('tags'):
                            model["tags"] = node.get('tags')
                            
                        # Extract additional catalog information if available
                        if catalog_node:
                            model["catalog_metadata"] = {
                                "unique_id": catalog_node.get('unique_id'),
                                "metadata": catalog_node.get('metadata', {})
                            }
                            
                            # Get stats if available
                            if 'stats' in catalog_node:
                                model["stats"] = catalog_node.get('stats')
                                
                        # Make sure description is complete and not truncated
                        full_description = node.get('description', '')
                        if isinstance(full_description, str) and len(full_description) > 0:
                            model["description"] = full_description
                            
                        models.append(model)
                        
                        if model_count <= 2:
                            print(f"  Added model: {model_name} (id: {model_id})")
                            if columns:
                                print(f"    First column: {columns[0]['name']} ({columns[0]['type']})")
                
                print(f"  Processed {model_count} models for project {project_name}")
                
                # Process lineage
                for node_id, node in manifest_data.get('nodes', {}).items():
                    if node.get('resource_type') == 'model' and node_id in model_id_map:
                        target_id = model_id_map[node_id]
                        
                        # Get dependencies
                        for dep_node_id in node.get('depends_on', {}).get('nodes', []):
                            if dep_node_id in model_id_map:
                                source_id = model_id_map[dep_node_id]
                                lineage_data.append({
                                    "source": source_id,
                                    "target": target_id
                                })
                
                # Print sample lineage
                if lineage_data:
                    print("\n  Sample Lineage Relationships:")
                    for i, lineage in enumerate(lineage_data[:3]):
                        source_model = next((m for m in models if m["id"] == lineage["source"]), None)
                        target_model = next((m for m in models if m["id"] == lineage["target"]), None)
                        source_name = source_model["name"] if source_model else "unknown"
                        target_name = target_model["name"] if target_model else "unknown"
                        print(f"    {source_name} ({lineage['source']}) -> {target_name} ({lineage['target']})")
                        if i >= 2:
                            break
            
            except Exception as e:
                print(f"Error processing project {project_dir}: {str(e)}")
        
        # Create the final metadata object
        metadata = {
            "projects": projects,
            "models": models,
            "lineage": lineage_data
        }
        
        print(f"\nParsing complete:")
        print(f"  Projects: {len(projects)}")
        print(f"  Models: {len(models)}")
        print(f"  Lineage relationships: {len(lineage_data)}")
        
        return metadata
    
    def _extract_columns_from_sql(self, sql: str) -> List[str]:
        """Extract column names from SQL query"""
        if not sql:
            return []
        
        # Try to find the SELECT statement
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return []
        
        select_clause = select_match.group(1)
        
        # Split by commas, but ignore commas inside functions
        columns = []
        bracket_level = 0
        current_column = ""
        
        for char in select_clause:
            if char == '(':
                bracket_level += 1
                current_column += char
            elif char == ')':
                bracket_level -= 1
                current_column += char
            elif char == ',' and bracket_level == 0:
                columns.append(current_column.strip())
                current_column = ""
            else:
                current_column += char
        
        if current_column:
            columns.append(current_column.strip())
        
        # Process each column expression
        result = []
        for col_expr in columns:
            # Check for AS keyword
            as_match = re.search(r'(?:AS|as)\s+([a-zA-Z0-9_]+)$', col_expr)
            if as_match:
                result.append(as_match.group(1))
            else:
                # If no AS keyword, use the last part after a dot or the whole expression
                col_parts = col_expr.split('.')
                col_name = col_parts[-1].strip()
                
                # Remove any functions
                if '(' not in col_name:
                    result.append(col_name)
        
        return result
    
    def refresh(self) -> bool:
        """Refresh metadata from dbt projects"""
        try:
            # Parse projects
            metadata = self._parse_dbt_projects()
            
            # Enrich with AI descriptions if enabled
            if self.use_ai_descriptions and self.ai_service:
                print("Enriching metadata with AI-generated descriptions...")
                metadata = self.ai_service.enrich_metadata(metadata)
            
            # Save to file
            with open(self.unified_metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update in-memory metadata
            self.metadata = metadata
            
            print(f"Metadata refreshed successfully and saved to {self.unified_metadata_path}")
            print(f"Projects: {len(self.metadata.get('projects', []))}")
            print(f"Models: {len(self.metadata.get('models', []))}")
            print(f"Lineage: {len(self.metadata.get('lineage', []))}")
            
            return True
        except Exception as e:
            print(f"Error refreshing metadata: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        projects = self.metadata.get("projects", [])
        print(f"Returning {len(projects)} projects")
        return projects
    
    def get_models(self, project_id: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all models, optionally filtered by project and search term"""
        models = self.metadata.get("models", [])
        
        # Filter by project if specified
        if project_id:
            models = [m for m in models if m["project"] == project_id]
        
        # Filter by search term if specified
        if search and search.strip():  # Ensure search is not empty or just whitespace
            search = search.lower().strip()
            print(f"Searching for exact match on model name: '{search}'")
            
            # Track matching models for debug logging
            name_matches = []
            desc_matches = []
            
            # Use exact matching for names, but still allow partial matching in descriptions
            filtered_models = []
            for model in models:
                model_name = model["name"].lower()
                if model_name == search:
                    name_matches.append(model["name"])
                    filtered_models.append(model)
                elif model.get("description") and search in model.get("description", "").lower():
                    desc_matches.append(model["name"])
                    filtered_models.append(model)
            
            # Debug logging
            print(f"Models matching by name ({len(name_matches)}): {', '.join(name_matches)}")
            print(f"Models matching by description ({len(desc_matches)}): {', '.join(desc_matches)}")
            
            models = filtered_models
        
        print(f"Returning {len(models)} models" + 
              (f" for project {project_id}" if project_id else "") +
              (f" matching search '{search}'" if search else ""))
        return models
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific model by ID"""
        for model in self.metadata.get("models", []):
            if model["id"] == model_id:
                print(f"Found model with ID {model_id}: {model['name']}")
                
                # Ensure all necessary fields have default values
                result = model.copy()
                
                # Add default values for any missing fields
                defaults = {
                    "description": "",
                    "schema": "default",
                    "materialized": "view",
                    "file_path": "N/A",
                    "columns": [],
                    "sql": "",
                    "tags": []
                }
                
                for key, default_value in defaults.items():
                    if key not in result or result[key] is None:
                        result[key] = default_value
                
                return result
                
        print(f"Model with ID {model_id} not found")
        return None
    
    def get_model_with_lineage(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get a model with its upstream and downstream lineage"""
        # Validate model_id to prevent NaN values
        if model_id == "NaN" or not model_id:
            print(f"Invalid model ID: {model_id}")
            return None
            
        model = self.get_model(model_id)
        if not model:
            return None
        
        print(f"Getting lineage for model {model_id} ({model['name']})")
        
        # Helper function to apply default values
        def apply_defaults(model_data):
            defaults = {
                "description": "",
                "schema": "default",
                "materialized": "view",
                "file_path": "N/A",
                "columns": [],
                "sql": "",
                "tags": []
            }
            
            for key, default_value in defaults.items():
                if key not in model_data or model_data[key] is None:
                    model_data[key] = default_value
            
            return model_data
        
        # Get upstream models (models that this model depends on)
        upstream = []
        for lineage in self.metadata.get("lineage", []):
            if lineage["target"] == model_id:
                source_id = lineage["source"]
                # Skip invalid source IDs
                if source_id == "NaN" or not source_id:
                    continue
                    
                source_model = self.get_model(source_id)
                if source_model:
                    # Include all required fields from the source model
                    upstream_model = {
                        "id": source_id,
                        "name": source_model["name"],
                        "project": source_model["project"],
                        "description": source_model.get("description", ""),
                        "columns": source_model.get("columns", []),
                        "sql": source_model.get("sql", ""),
                        "schema": source_model.get("schema", "default"),
                        "materialized": source_model.get("materialized", "view"),
                        "file_path": source_model.get("file_path", "N/A"),
                        "tags": source_model.get("tags", [])
                    }
                    
                    # Apply defaults to ensure all fields have values
                    upstream.append(apply_defaults(upstream_model))
        
        # Get downstream models (models that depend on this model)
        downstream = []
        for lineage in self.metadata.get("lineage", []):
            if lineage["source"] == model_id:
                target_id = lineage["target"]
                # Skip invalid target IDs
                if target_id == "NaN" or not target_id:
                    continue
                    
                target_model = self.get_model(target_id)
                if target_model:
                    # Include all required fields from the target model
                    downstream_model = {
                        "id": target_id,
                        "name": target_model["name"],
                        "project": target_model["project"],
                        "description": target_model.get("description", ""),
                        "columns": target_model.get("columns", []),
                        "sql": target_model.get("sql", ""),
                        "schema": target_model.get("schema", "default"),
                        "materialized": target_model.get("materialized", "view"),
                        "file_path": target_model.get("file_path", "N/A"),
                        "tags": target_model.get("tags", [])
                    }
                    
                    # Apply defaults to ensure all fields have values
                    downstream.append(apply_defaults(downstream_model))
        
        print(f"Found {len(upstream)} upstream and {len(downstream)} downstream models")
        if upstream:
            print("Upstream models:")
            for up in upstream[:3]:  # Print first 3
                print(f"  - {up['name']} ({up['id']})")
            if len(upstream) > 3:
                print(f"  - ... and {len(upstream) - 3} more")
                
        if downstream:
            print("Downstream models:")
            for down in downstream[:3]:  # Print first 3
                print(f"  - {down['name']} ({down['id']})")
            if len(downstream) > 3:
                print(f"  - ... and {len(downstream) - 3} more")
        
        # Add lineage to model
        model_with_lineage = model.copy()
        model_with_lineage["upstream"] = upstream
        model_with_lineage["downstream"] = downstream
        
        return model_with_lineage
    
    def _get_project_name(self, project_id: str) -> str:
        """Get project name from project ID"""
        for project in self.metadata.get("projects", []):
            if project["id"] == project_id:
                return project["name"]
        return "Unknown Project"
    
    def get_lineage(self) -> List[Dict[str, str]]:
        """Get all lineage relationships"""
        lineage = self.metadata.get("lineage", [])
        print(f"Returning {len(lineage)} lineage relationships")
        if lineage:
            print("Sample lineage relationships:")
            for i, l in enumerate(lineage[:3]):
                print(f"  {i+1}. Source: {l['source']}, Target: {l['target']}")
        return lineage

    def update_description(self, entity_type: str, entity_id: str, description: str) -> bool:
        """Update description for a model or column"""
        try:
            if entity_type == "model":
                # Update model description
                for model in self.metadata.get("models", []):
                    if model.get("id") == entity_id:
                        model["description"] = description
                        # Mark as user-edited
                        model["user_edited"] = True
                        
                        # Save updated metadata
                        with open(self.unified_metadata_path, 'w') as f:
                            json.dump(self.metadata, f, indent=2)
                        
                        print(f"Updated description for model {entity_id}")
                        return True
                
                print(f"Model {entity_id} not found")
                return False
                
            elif entity_type == "column":
                # Format for column ID is "model_id:column_name"
                if ":" not in entity_id:
                    print(f"Invalid column ID format: {entity_id}")
                    return False
                    
                model_id, column_name = entity_id.split(":", 1)
                
                # Find the model
                for model in self.metadata.get("models", []):
                    if model.get("id") == model_id:
                        # Find the column
                        for column in model.get("columns", []):
                            if column.get("name") == column_name:
                                column["description"] = description
                                # Mark as user-edited
                                column["user_edited"] = True
                                
                                # Save updated metadata
                                with open(self.unified_metadata_path, 'w') as f:
                                    json.dump(self.metadata, f, indent=2)
                                
                                print(f"Updated description for column {entity_id}")
                                return True
                        
                        print(f"Column {column_name} not found in model {model_id}")
                        return False
                
                print(f"Model {model_id} not found")
                return False
            
            else:
                print(f"Invalid entity type: {entity_type}")
                return False
                
        except Exception as e:
            print(f"Error updating description: {str(e)}")
            return False
            
    def refresh_model_metadata(self, model_id: str) -> bool:
        """Refresh metadata for a specific model, focusing on AI descriptions"""
        try:
            # Get the current model
            model = None
            for m in self.metadata.get("models", []):
                if m["id"] == model_id:
                    model = m
                    break
            
            if not model:
                print(f"Model with ID {model_id} not found for refreshing")
                return False
                
            print(f"Refreshing metadata for model {model_id} ({model.get('name', 'Unknown')})")
            
            # Initialize AI service if enabled
            if self.use_ai_descriptions and self.ai_service:
                # Generate model description if missing or flagged for refresh
                if not model.get("description") or model.get("refresh_description"):
                    print(f"Generating AI description for model {model['name']}")
                    model_desc = self.ai_service.generate_model_description(
                        model["name"],
                        model.get("project", ""),
                        model.get("sql", ""),
                        model.get("columns", [])
                    )
                    
                    if model_desc:
                        # Store AI description
                        model["ai_description"] = model_desc
                        
                        # If no description exists at all, use the AI one as default
                        if not model.get("description"):
                            model["description"] = model_desc
                            model["user_edited"] = False
                        
                        print(f"Updated model description for {model['name']}")
                    
                # Process columns for this model
                columns_to_process = []
                
                # Find columns without descriptions
                for j, column in enumerate(model.get("columns", [])):
                    # Skip if the column already has a description and isn't flagged for refresh
                    if column.get("description") and not column.get("refresh_description"):
                        continue
                    
                    # Add to processing list with priority info
                    column_name = column.get("name", "")
                    priority = 0
                    
                    # Give higher priority to important columns
                    if column.get("isPrimaryKey"):
                        priority += 3
                    if column.get("isForeignKey"):
                        priority += 2
                    if "id" in column_name.lower() or "key" in column_name.lower():
                        priority += 1
                        
                    columns_to_process.append((j, column, priority))
                
                # Sort by priority
                columns_to_process.sort(key=lambda x: x[2], reverse=True)
                
                # Process the columns (all of them since this is a targeted refresh)
                for idx, (j, column, _) in enumerate(columns_to_process):
                    column_name = column.get("name", "")
                    print(f"Processing column {idx+1}/{len(columns_to_process)}: {column_name}")
                    
                    # Generate column description
                    column_desc = self.ai_service.generate_column_description(
                        column_name,
                        model["name"],
                        model.get("sql", ""),
                        column.get("type", ""),
                        model.get("description", "")
                    )
                    
                    if column_desc:
                        # Store AI description
                        column["ai_description"] = column_desc
                        
                        # If no description exists or refresh was requested, use the AI one
                        if not column.get("description") or column.get("refresh_description"):
                            column["description"] = column_desc
                            column["user_edited"] = False
                        
                        # Clear refresh flag
                        if "refresh_description" in column:
                            del column["refresh_description"]
                
                # Save updated metadata
                with open(self.unified_metadata_path, 'w') as f:
                    json.dump(self.metadata, f, indent=2)
                
                print(f"Successfully refreshed metadata for model {model['name']}")
                return True
            else:
                print("AI description generation is disabled or AI service is not initialized")
                return False
                
        except Exception as e:
            print(f"Error refreshing model metadata: {str(e)}")
            import traceback
            traceback.print_exc()
            return False