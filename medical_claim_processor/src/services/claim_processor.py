import asyncio
import os
import tempfile
import uuid
from typing import List, Dict, Any
from fastapi import UploadFile
import subprocess

from src.models.data_models import (
    ProcessClaimResponse, ValidationResult, ClaimDecision,
    ClassifiedDocument, ExtractedData
)
from src.services.document_classifier import DocumentClassifier
from src.services.text_extractor import TextExtractor
from src.agents.bill_agent import BillAgent
from src.agents.discharge_agent import DischargeAgent
from src.agents.insurance_agent import InsuranceAgent
from src.services.validator import ClaimValidator
from src.services.decision_engine import DecisionEngine

class ClaimProcessor:
    def __init__(self):
        self.document_classifier = DocumentClassifier()
        self.text_extractor = TextExtractor()
        self.bill_agent = BillAgent()
        self.discharge_agent = DischargeAgent()
        self.insurance_agent = InsuranceAgent()
        self.validator = ClaimValidator()
        self.decision_engine = DecisionEngine()
        
    async def process_claim(self, files: List[UploadFile]) -> ProcessClaimResponse:
        """
        Main orchestration method for processing medical claim documents.
        """
        try:
            # Step 1: Save uploaded files temporarily and extract text
            documents_data = await self._prepare_documents(files)
            
            # Step 2: Classify each document
            classified_docs = await self._classify_documents(documents_data)
            
            # Step 3: Extract structured data using appropriate agents
            extracted_data = await self._extract_data(classified_docs, documents_data)
            
            # Step 4: Validate the extracted data
            validation_result = await self._validate_data(extracted_data)
            
            # Step 5: Make claim decision
            claim_decision = await self._make_decision(extracted_data, validation_result)
            
            # Step 6: Prepare response
            response = ProcessClaimResponse(
                documents=self._format_documents_response(extracted_data),
                validation=validation_result,
                claim_decision=claim_decision,
                processing_summary={
                    "total_documents": len(files),
                    "classified_documents": len(classified_docs),
                    "extracted_documents": len(extracted_data)
                }
            )
            
            return response
            
        except Exception as e:
            # Return error response
            return ProcessClaimResponse(
                documents={},
                validation=ValidationResult(
                    discrepancies=[f"Processing error: {str(e)}"]
                ),
                claim_decision=ClaimDecision(
                    status="rejected",
                    reason=f"Unable to process claim due to error: {str(e)}"
                )
            )
    
    async def _prepare_documents(self, files: List[UploadFile]) -> List[Dict[str, Any]]:
        """
        Save uploaded files and extract text content.
        """
        documents_data = []
        
        for file in files:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Extract text from PDF
            text_content = self._extract_text_from_pdf(temp_file_path)
            
            documents_data.append({
                'file_id': file_id,
                'filename': file.filename,
                'content_type': file.content_type,
                'temp_path': temp_file_path,
                'text_content': text_content
            })
            
        return documents_data
    
    async def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdftotext asynchronously.
        """
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,  # Use the default ThreadPoolExecutor
                lambda: subprocess.run(
                    ['pdftotext', pdf_path, '-'],
                    capture_output=True,
                    text=True,
                    check=True
                )
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
        finally:
            # Clean up the temporary PDF file immediately after text extraction
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    async def _classify_documents(self, documents_data: List[Dict[str, Any]]) -> List[ClassifiedDocument]:
        """
        Classify each document using the document classifier.
        """
        classified_docs = []
        
        for doc_data in documents_data:
            classification = await self.document_classifier.classify(
                doc_data['file_id'],  # Pass file_id instead of filename
                doc_data['filename'],
                doc_data['text_content']
            )
            classified_docs.append(classification)
            
        return classified_docs
    
    async def _extract_data(self, classified_docs: List[ClassifiedDocument], 
                          documents_data: List[Dict[str, Any]]) -> List[ExtractedData]:
        """
        Extract structured data using appropriate agents based on document type.
        """
        extracted_data = []
        
        # Create a mapping of file_id to document data
        doc_data_map = {doc['file_id']: doc for doc in documents_data}
        
        for classified_doc in classified_docs:
            doc_data = doc_data_map[classified_doc.file_id]
            text_content = doc_data['text_content']
            
            # Route to appropriate agent based on document type
            if classified_doc.document_type == "hospital_bill":
                extracted = await self.bill_agent.extract_data(text_content)
            elif classified_doc.document_type == "discharge_summary":
                extracted = await self.discharge_agent.extract_data(text_content)
            elif classified_doc.document_type == "insurance_card":
                extracted = await self.insurance_agent.extract_data(text_content)
            else:
                # Handle unknown document types
                extracted = ExtractedData(
                    document_type="other",
                    data={},
                    extraction_confidence=0.0,
                    raw_text=text_content
                )
            
            extracted.raw_text = text_content
            extracted_data.append(extracted)
            
        return extracted_data
    
    async def _validate_data(self, extracted_data: List[ExtractedData]) -> ValidationResult:
        """
        Validate the extracted data for consistency and completeness.
        """
        return await self.validator.validate(extracted_data)
    
    async def _make_decision(self, extracted_data: List[ExtractedData], 
                           validation_result: ValidationResult) -> ClaimDecision:
        """
        Make the final claim decision based on extracted data and validation results.
        """
        return await self.decision_engine.make_decision(extracted_data, validation_result)
    
    def _format_documents_response(self, extracted_data: List[ExtractedData]) -> Dict[str, Any]:
        """
        Format the extracted data for the API response.
        """
        documents = {}
        
        for i, data in enumerate(extracted_data):
            documents[f"document_{i+1}"] = {
                "type": data.document_type,
                "data": data.data,
                "confidence": data.extraction_confidence
            }
            
        return documents
    
    def __del__(self):
        """
        Cleanup temporary files when the processor is destroyed.
        """
        # Note: In a production system, you'd want a more robust cleanup mechanism
        pass

