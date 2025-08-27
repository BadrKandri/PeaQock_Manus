from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from pathlib import Path
import shutil, logging
from core.paths import repo_path, output_path

logger = logging.getLogger("peaqock_api")
router = APIRouter()

class UploadResponse(BaseModel):
    file_path: str

@router.post("/upload", response_model=UploadResponse)
def upload_excel(file: UploadFile = File(...), query: str = Form("")):
    """Upload Excel file for analysis and processing"""
    
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files allowed")
    
    repo_dir = Path(repo_path)
    repo_dir.mkdir(exist_ok=True)
    (repo_dir / "scripts").mkdir(exist_ok=True)
    
    if output_path.exists():
        shutil.rmtree(output_path)
    
    target_file = repo_dir / "data.xlsx"
    target_file.unlink(missing_ok=True)
    
    with open(target_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"File uploaded: {target_file}, Query: {query}")
    
    try:
        from services.main_flow import main_flow
        result = main_flow(query)
        logger.info("Main function executed successfully")
        
        response_data = {"file_path": str(target_file)}
        
        if result and result.strip():
            response_data["message"] = result
            response_data["has_custom_message"] = True
        else:
            response_data["message"] = "Query processed successfully. Results available for download."
            response_data["has_custom_message"] = False
            
        return response_data
    except Exception as e:
        logger.error(f"Error executing main function: {str(e)}")
        return {
            "file_path": str(target_file), 
            "message": f"Error processing query: {str(e)}", 
            "has_custom_message": True
        }
