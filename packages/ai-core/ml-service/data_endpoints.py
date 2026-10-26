"""
Data Management Endpoint

Handle data upload and management for custom training datasets.
"""

from fastapi import HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import shutil
import json
from datetime import datetime


class DatasetInfo(BaseModel):
    name: str = Field(..., description="Dataset name")
    sample_count: int = Field(..., description="Number of samples")
    created_at: str = Field(..., description="Creation timestamp")
    language: str = Field(..., description="Primary language")


class DataUploadResponse(BaseModel):
    success: bool
    message: str
    dataset_info: Optional[DatasetInfo] = None


# Data storage directory
import sys
service_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.dirname(service_dir)
DATA_DIR = os.path.join(ai_core_dir, "data", "user_data")
os.makedirs(DATA_DIR, exist_ok=True)


def add_upload_endpoints(app):
    """Add data management endpoints to FastAPI app"""
    
    @app.post("/data/upload")
    async def upload_data(
        file: UploadFile = File(..., description="Data file to upload"),
        dataset_name: str = None,
        language: str = "mixed"
    ):
        """
        Upload training data file
        Supported formats: .json, .csv, .txt
        """
        try:
            # Validate file type
            if not file.filename.endswith(('.json', '.csv', '.txt')):
                raise HTTPException(status_code=400, detail="Unsupported file type. Use .json, .csv, or .txt")
            
            # Create dataset directory
            if dataset_name:
                dataset_dir = os.path.join(DATA_DIR, dataset_name)
            else:
                dataset_dir = os.path.join(DATA_DIR, f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            os.makedirs(dataset_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(dataset_dir, file.filename)
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Count samples
            sample_count = 0
            if file.filename.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        sample_count = len(data)
            elif file.filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample_count = sum(1 for line in f if line.strip())
            elif file.filename.endswith('.csv'):
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    sample_count = sum(1 for row in reader if row)
            
            dataset_info = DatasetInfo(
                name=os.path.basename(dataset_dir),
                sample_count=sample_count,
                created_at=datetime.now().isoformat(),
                language=language
            )
            
            return DataUploadResponse(
                success=True,
                message=f"Successfully uploaded {file.filename} with {sample_count} samples",
                dataset_info=dataset_info
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    @app.get("/data/datasets")
    async def list_datasets():
        """List all available datasets"""
        datasets = []
        
        if os.path.exists(DATA_DIR):
            for dirname in os.listdir(DATA_DIR):
                dataset_path = os.path.join(DATA_DIR, dirname)
                if os.path.isdir(dataset_path):
                    # Find data files
                    files = [f for f in os.listdir(dataset_path) if f.endswith(('.json', '.csv', '.txt'))]
                    if files:
                        datasets.append({
                            "name": dirname,
                            "files": files,
                            "created": datetime.fromtimestamp(os.path.getmtime(dataset_path)).isoformat()
                        })
        
        return {"datasets": datasets}
    
    @app.delete("/data/datasets/{dataset_name}")
    async def delete_dataset(dataset_name: str):
        """Delete a dataset"""
        dataset_path = os.path.join(DATA_DIR, dataset_name)
        
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        if not os.path.isdir(dataset_path):
            raise HTTPException(status_code=400, detail="Not a dataset directory")
        
        shutil.rmtree(dataset_path)
        
        return {"success": True, "message": f"Dataset {dataset_name} deleted"}
