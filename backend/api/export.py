# backend/api/export.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import os
import json

from ..services.metadata_service import MetadataService

router = APIRouter(prefix="/api/export", tags=["export"])

@router.get("/combined-data")
async def export_combined_data(output_file: Optional[str] = None):
    """
    Export all combined metadata from dbt projects
    
    Args:
        output_file: Optional file path to save the JSON. If None, only returns the data.
    
    Returns:
        JSON object with projects, models, and lineage data
    """
    metadata_service = MetadataService()
    
    # Get the data
    export_data = {
        "projects": metadata_service.get_projects(),
        "models": metadata_service.get_models(),
        "lineage": metadata_service.get_lineage()
    }
    
    # Save to file if requested
    file_path = None
    if output_file:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            file_path = os.path.abspath(output_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Return response
    response = {
        "data": export_data,
        "message": "Data exported successfully"
    }
    
    if file_path:
        response["file_path"] = file_path
    
    return response