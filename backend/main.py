from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import uuid
import time
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.models import ProcessingResult, DocumentCategory
from document_processor import DocumentProcessor
from config import settings

app = FastAPI(title="Document Processing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = DocumentProcessor()

@app.get("/")
async def root():
    return {"message": "Document Processing API"}

@app.post("/process-document/", response_model=ProcessingResult)
async def process_document(file: UploadFile = File(...)):
    start_time = time.time()
    file_id = str(uuid.uuid4())
    
    try:
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File type not detected")
        
        if not file.content_type.startswith(('image/', 'application/pdf')):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and image files are supported"
            )
        
        file_content = await file.read()
        
        result = await processor.process_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
            file_id=file_id
        )
        
        processing_time = time.time() - start_time
        result.processing_time = processing_time
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ProcessingResult(
            file_id=file_id,
            filename=file.filename or "unknown",
            category=DocumentCategory.OTHER,
            confidence=0.0,
            extracted_content={},
            processing_time=processing_time,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)