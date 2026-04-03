from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import ProcessResponse
from app.services.graph import process_claim
import os
import tempfile
import traceback

router = APIRouter(prefix="/api", tags=["process"])

@router.post("/process", response_model=ProcessResponse)
async def process_claim_endpoint(
    claim_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Process a claim PDF file.
    
    Steps:
    1. Accept file upload and claim_id
    2. Save file temporarily
    3. Call process_claim() workflow
    4. Return JSON response
    5. Clean up temporary file
    """
    temp_file_path = None
    
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Call process_claim workflow
        result = await process_claim(temp_file_path, claim_id)
        
        # Return JSON response
        return result
        
    except Exception as e:
        # Log the full error
        error_details = traceback.format_exc()
        print(f"Error processing claim: {error_details}")
        
        # Return detailed error to client
        raise HTTPException(
            status_code=500,
            detail=f"Error processing claim: {str(e)}"
        )
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
