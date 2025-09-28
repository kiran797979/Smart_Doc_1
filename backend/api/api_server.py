"""
FastAPI Backend for Smart Doc Checker
Provides REST API endpoints for document analysis and contradiction detection
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add backend to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import SmartDocChecker


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Doc Checker API",
    description="API for detecting contradictions across multiple documents",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "https://*.vercel.app",  # Vercel deployment
        "https://*.netlify.app", # Netlify deployment (optional)
        "https://smart-doc-checker.vercel.app",  # Your custom domain
        "https://frontend-amber-alpha-10.vercel.app",  # Current frontend URL
        "https://frontend-22at20ato-kirans-projects-abcb66a1.vercel.app",  # Alternative frontend URL
        "https://smart-doc-checker-kirans-projects-abcb66a1.vercel.app",  # Previous URLs
        "https://smart-doc-checker-lmxrywr5m-kirans-projects-abcb66a1.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the smart doc checker
doc_checker = SmartDocChecker()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models for request/response
class DocumentInfo(BaseModel):
    id: Optional[int] = None
    filename: str
    file_path: str
    clauses: Dict[str, Any]
    status: str = "success"
    created_at: Optional[str] = None

class ContradictionInfo(BaseModel):
    id: int
    clause_type: str
    severity: str
    summary: str
    documents: List[Dict[str, Any]]
    details: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

class AnalysisResult(BaseModel):
    documents: List[DocumentInfo]
    contradictions: List[ContradictionInfo]
    summary: Dict[str, Any]

class AnalysisRequest(BaseModel):
    document_ids: List[int]


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Smart Doc Checker API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload - Upload documents",
            "analyze": "POST /analyze - Analyze uploaded documents",
            "check": "GET /check - Get contradiction analysis results",
            "documents": "GET /documents - List all documents",
            "results": "GET /results/{doc_id} - Get results for specific document"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": str(datetime.now())}

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload multiple documents for processing
    
    Args:
        files: List of uploaded files (PDF/DOCX)
        
    Returns:
        Information about uploaded files
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    failed_uploads = []
    
    for file in files:
        try:
            # Validate file type
            if not file.filename:
                failed_uploads.append({"filename": "unknown", "error": "No filename provided"})
                continue
                
            file_extension = Path(file.filename).suffix.lower()
            allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
            
            if file_extension not in allowed_extensions:
                failed_uploads.append({
                    "filename": file.filename,
                    "error": f"Unsupported file type: {file_extension}"
                })
                continue
            
            # Save file to uploads directory
            file_path = UPLOAD_DIR / file.filename
            
            # Handle duplicate filenames
            counter = 1
            original_path = file_path
            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                file_path = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
                counter += 1
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "saved_as": file_path.name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "status": "success"
            })
            
            logger.info(f"Uploaded file: {file.filename} -> {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to upload {file.filename}: {str(e)}")
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "message": f"Processed {len(files)} file(s)",
        "successful_uploads": len(uploaded_files),
        "failed_uploads": len(failed_uploads),
        "files": uploaded_files,
        "errors": failed_uploads
    }

class AnalyzeRequest(BaseModel):
    file_paths: Optional[List[str]] = None

@app.options("/analyze")
async def analyze_options():
    """Handle OPTIONS preflight request for analyze endpoint"""
    return JSONResponse(content={"message": "OK"})

@app.post("/analyze")
async def analyze_documents(request: Optional[AnalyzeRequest] = None):
    """
    Analyze uploaded documents for contradictions
    
    Args:
        request: Request body containing optional file_paths list
        
    Returns:
        Analysis results with detected contradictions
    """
    try:
        logger.info(f"Analyze request received: {request}")
        
        # Extract file_paths from request body if provided
        file_paths = request.file_paths if request else None
        
        # If no specific files provided, analyze all files in uploads directory
        if not file_paths:
            file_paths = []
            for file_path in UPLOAD_DIR.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx', '.doc', '.txt']:
                    file_paths.append(str(file_path))
        
        if not file_paths:
            raise HTTPException(status_code=400, detail="No documents found to analyze")
        
        logger.info(f"Starting analysis of {len(file_paths)} documents")
        
        # Process documents using the main controller
        results = doc_checker.process_documents(file_paths)
        
        logger.info(f"Analysis completed. Found {results['summary']['total_contradictions']} contradictions")
        
        return results
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/check")
async def get_contradiction_results():
    """
    Get all contradiction analysis results from database
    
    Returns:
        All stored documents and contradictions
    """
    try:
        results = doc_checker.get_all_results()
        
        return {
            "documents": results["documents"],
            "contradictions": results["contradictions"],
            "summary": {
                "total_documents": len(results["documents"]),
                "total_contradictions": len(results["contradictions"])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

@app.get("/documents")
async def list_documents():
    """
    List all processed documents
    
    Returns:
        List of all documents in database
    """
    try:
        documents = doc_checker.db.get_all_documents()
        
        return {
            "documents": documents,
            "total_count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.get("/results/{doc_id}")
async def get_document_results(doc_id: int):
    """
    Get results for a specific document
    
    Args:
        doc_id: Document ID
        
    Returns:
        Document details and related contradictions
    """
    try:
        document = doc_checker.get_document_results(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
        
        # Get contradictions involving this document
        all_contradictions = doc_checker.db.get_all_contradictions()
        related_contradictions = []
        
        for contradiction in all_contradictions:
            for doc_info in contradiction["documents"]:
                if doc_info.get("doc_id") == doc_id:
                    related_contradictions.append(contradiction)
                    break
        
        return {
            "document": document,
            "related_contradictions": related_contradictions,
            "contradiction_count": len(related_contradictions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document results: {str(e)}")

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    """
    Delete a document from the database
    
    Args:
        doc_id: Document ID to delete
        
    Returns:
        Deletion status
    """
    try:
        success = doc_checker.db.delete_document(doc_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
        
        return {"message": f"Document {doc_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/statistics")
async def get_statistics():
    """
    Get database and analysis statistics
    
    Returns:
        Statistics about processed documents and contradictions
    """
    try:
        stats = doc_checker.db.get_statistics()
        
        # Add upload directory stats
        upload_files = list(UPLOAD_DIR.glob("*"))
        upload_stats = {
            "total_files": len([f for f in upload_files if f.is_file()]),
            "pdf_files": len(list(UPLOAD_DIR.glob("*.pdf"))),
            "docx_files": len(list(UPLOAD_DIR.glob("*.docx"))),
            "txt_files": len(list(UPLOAD_DIR.glob("*.txt")))
        }
        
        return {
            "database_stats": stats,
            "upload_directory_stats": upload_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.post("/clear-data")
async def clear_all_data():
    """
    Clear all data from database and uploads directory (use with caution!)
    
    Returns:
        Confirmation message
    """
    try:
        # Clear database
        doc_checker.db.clear_all_data()
        
        # Clear uploads directory
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        
        logger.info("All data cleared")
        
        return {"message": "All data cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")

@app.get("/uploads")
async def list_uploaded_files():
    """
    List all files in the uploads directory
    
    Returns:
        List of uploaded files with metadata
    """
    try:
        files = []
        
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "file_size": stat.st_size,
                    "file_extension": file_path.suffix.lower(),
                    "last_modified": stat.st_mtime,
                    "is_supported": file_path.suffix.lower() in ['.pdf', '.docx', '.doc', '.txt']
                })
        
        return {
            "files": files,
            "total_count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Failed to list uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list uploads: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Smart Doc Checker API Server")
    print("=" * 50)
    print(f"Port: {port}")
    print("API Documentation: /docs")
    print("Health Check: /health")
    print("=" * 50)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )