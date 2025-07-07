import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import uvicorn

from src.models.data_models import ProcessClaimResponse
from src.services.claim_processor import ClaimProcessor
from src.services.pdf_generator import PDFGenerator
import io

app = FastAPI(title="Medical Claim Processor", version="1.0.0")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_folder_path = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_folder_path):
    app.mount("/static", StaticFiles(directory=static_folder_path), name="static")

# Initialize the claim processor and PDF generator
claim_processor = ClaimProcessor()
pdf_generator = PDFGenerator()

@app.post("/process-claim", response_model=ProcessClaimResponse)
async def process_claim(files: List[UploadFile] = File(...)):
    """
    Process medical claim documents and return a claim decision.
    
    Accepts multiple PDF files (hospital bills, discharge summaries, insurance cards)
    and returns structured data with a claim approval/rejection decision.
    """
    try:
        # Validate file types
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        # Process the claim
        result = await claim_processor.process_claim(files)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-pdf")
async def generate_pdf(results: dict):
    """
    Generate a professional PDF report from claim processing results.
    """
    try:
        pdf_bytes = pdf_generator.generate_claim_report(results)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=claim-processing-result.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.get("/")
async def serve_index():
    """Serve the index.html file"""
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "Medical Claim Processor API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Medical Claim Processor"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    uvicorn.run("src.main:app", host='0.0.0.0', port=port, reload=False)

