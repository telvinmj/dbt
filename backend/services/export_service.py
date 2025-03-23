import json
import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.db.models import Model, Project, Lineage, ColumnModel

class ExportService:
    def __init__(self, db: Session):
        self.db = db
    
    def export_combined_data(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export all combined data including models, projects, lineage, and columns
        to a structured JSON format.
        
        Args:
            output_path: Optional file path to save the JSON. If None, only returns the data.
            
        Returns:
            Dictionary containing all the combined data
        """
        # Get all data from database
        projects = self.db.query(Project).all()
        models = self.db.query(Model).all()
        lineage_relationships = self.db.query(Lineage).all()
        columns = self.db.query(ColumnModel).all()
        
        # Create serializable data structures
        projects_data = []
        for project in projects:
            projects_data.append({
                "id": project.id,
                "name": project.name,
                "models": [model.id for model in project.models]
            })
        
        models_data = []
        for model in models:
            models_data.append({
                "id": model.id,
                "name": model.name,
                "project_id": model.project_id,
                "description": model.description,
                "schema_name": model.schema_name,
                "materialized": model.materialized,
                "sql": model.sql,
                "created_at": model.created_at.isoformat() if model.created_at else None,
                "updated_at": model.updated_at.isoformat() if model.updated_at else None,
                "columns": [column.id for column in model.columns] if hasattr(model, "columns") else []
            })
        
        columns_data = []
        for column in columns:
            columns_data.append({
                "id": column.id,
                "name": column.name,
                "model_id": column.model_id,
                "description": column.description,
                "data_type": column.data_type,
                "is_primary_key": column.is_primary_key if hasattr(column, "is_primary_key") else False,
                "is_foreign_key": column.is_foreign_key if hasattr(column, "is_foreign_key") else False
            })
        
        lineage_data = []
        for lineage in lineage_relationships:
            lineage_data.append({
                "id": lineage.id,
                "source_model_id": lineage.source_model_id,
                "target_model_id": lineage.target_model_id,
                "source_is_source": lineage.source_is_source if hasattr(lineage, "source_is_source") else False,
                "relationship_type": lineage.relationship_type if hasattr(lineage, "relationship_type") else "ref"
            })
        
        # Combine all data
        combined_data = {
            "projects": projects_data,
            "models": models_data,
            "columns": columns_data,
            "lineage": lineage_data
        }
        
        # Save to file if path is provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(combined_data, f, indent=2)
            
        return combined_data 