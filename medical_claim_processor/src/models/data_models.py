from pydantic import BaseModel
from typing import Literal, Dict, Any, List, Optional
from datetime import date

class InputDocument(BaseModel):
    filename: str
    content_type: str
    file_id: str

class ClassifiedDocument(BaseModel):
    file_id: str
    document_type: Literal["hospital_bill", "discharge_summary", "insurance_card", "other"]
    confidence: float = 0.0

class HospitalBillData(BaseModel):
    hospital_name: Optional[str] = None
    total_amount: Optional[float] = None
    date_of_service: Optional[date] = None
    patient_name: Optional[str] = None
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    items: List[Dict[str, Any]] = []
    insurance_company: Optional[str] = None
    policy_number: Optional[str] = None

class DischargeSummaryData(BaseModel):
    patient_name: Optional[str] = None
    diagnosis: Optional[str] = None
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    treatment_summary: Optional[str] = None

class InsuranceCardData(BaseModel):
    policy_number: Optional[str] = None
    card_holder_name: Optional[str] = None
    insurance_company: Optional[str] = None
    sum_insured: Optional[float] = None
    validity_date: Optional[date] = None

class ValidationResult(BaseModel):
    missing_documents: List[str] = []
    discrepancies: List[str] = []
    warnings: List[str] = []

class ClaimDecision(BaseModel):
    status: Literal["approved", "rejected", "pending"]
    reason: str
    confidence: float = 0.0
    recommended_amount: Optional[float] = None

class ProcessClaimResponse(BaseModel):
    documents: Dict[str, Any]  # Dictionary of file_id to extracted data
    validation: ValidationResult
    claim_decision: ClaimDecision
    processing_summary: Dict[str, Any] = {}

# Additional models for internal processing
class ExtractedData(BaseModel):
    document_type: str
    data: Dict[str, Any]
    extraction_confidence: float = 0.0
    raw_text: str = ""

