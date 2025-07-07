import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from src.models.data_models import ExtractedData, ValidationResult, ClaimDecision

class DecisionEngine:
    """
    Service for making claim approval/rejection decisions based on extracted data and validation results.
    """
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
        if api_key != 'your-api-key-here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
        
        # Define decision rules
        self.approval_rules = {
            "required_documents": ["hospital_bill"],  # Minimum required
            "max_discrepancies": 2,  # Maximum allowed discrepancies
            "min_confidence": 0.3,  # Minimum extraction confidence
            "max_claim_amount": 1000000,  # Maximum claimable amount
        }
    
    async def make_decision(self, extracted_data: List[ExtractedData], 
                          validation_result: ValidationResult) -> ClaimDecision:
        """
        Make the final claim decision based on extracted data and validation results.
        """
        try:
            # First, apply rule-based decision logic
            rule_decision = self._rule_based_decision(extracted_data, validation_result)
            
            # If LLM is available, get AI-assisted decision
            if self.model is not None:
                ai_decision = await self._ai_assisted_decision(extracted_data, validation_result, rule_decision)
                return ai_decision
            else:
                return rule_decision
                
        except Exception as e:
            # Fallback to rejection in case of errors
            return ClaimDecision(
                status="rejected",
                reason=f"Unable to process claim due to system error: {str(e)}",
                confidence=0.1
            )
    
    def _rule_based_decision(self, extracted_data: List[ExtractedData], 
                           validation_result: ValidationResult) -> ClaimDecision:
        """
        Make decision based on predefined rules.
        """
        # Check for critical missing documents
        if validation_result.missing_documents:
            missing_critical = any("hospital_bill" in missing for missing in validation_result.missing_documents)
            if missing_critical:
                return ClaimDecision(
                    status="rejected",
                    reason="Missing critical documents: " + ", ".join(validation_result.missing_documents),
                    confidence=0.9
                )
        
        # Check for too many discrepancies
        if len(validation_result.discrepancies) > self.approval_rules["max_discrepancies"]:
            return ClaimDecision(
                status="rejected",
                reason=f"Too many discrepancies found ({len(validation_result.discrepancies)}): " + 
                       "; ".join(validation_result.discrepancies[:3]),
                confidence=0.8
            )
        
        # Check extraction confidence
        avg_confidence = sum(data.extraction_confidence for data in extracted_data) / len(extracted_data)
        if avg_confidence < self.approval_rules["min_confidence"]:
            return ClaimDecision(
                status="rejected",
                reason=f"Low data extraction confidence ({avg_confidence:.2f}). Unable to verify claim details.",
                confidence=0.7
            )
        
        # Check claim amount
        claim_amount = self._get_claim_amount(extracted_data)
        if claim_amount and claim_amount > self.approval_rules["max_claim_amount"]:
            return ClaimDecision(
                status="rejected",
                reason=f"Claim amount (₹{claim_amount:,.2f}) exceeds maximum limit (₹{self.approval_rules['max_claim_amount']:,.2f})",
                confidence=0.9,
                recommended_amount=self.approval_rules["max_claim_amount"]
            )
        
        # Check for basic claim validity
        if not self._is_claim_valid(extracted_data):
            return ClaimDecision(
                status="rejected",
                reason="Claim does not meet basic validity requirements",
                confidence=0.8
            )
        
        # If all checks pass, approve the claim
        approval_reason = "All documents verified and validation checks passed"
        if validation_result.warnings:
            approval_reason += f". Note: {len(validation_result.warnings)} warnings found"
        
        return ClaimDecision(
            status="approved",
            reason=approval_reason,
            confidence=min(avg_confidence + 0.2, 1.0),
            recommended_amount=claim_amount
        )
    
    async def _ai_assisted_decision(self, extracted_data: List[ExtractedData], 
                                  validation_result: ValidationResult,
                                  rule_decision: ClaimDecision) -> ClaimDecision:
        """
        Use AI to assist in decision making.
        """
        try:
            # Prepare data summary for AI
            data_summary = self._prepare_data_summary(extracted_data, validation_result)
            
            prompt = f"""
            You are a medical insurance claim processor. Based on the following information, 
            make a decision on whether to approve or reject this claim.
            
            Rule-based decision: {rule_decision.status} - {rule_decision.reason}
            
            Extracted Data Summary:
            {data_summary}
            
            Validation Results:
            - Missing documents: {validation_result.missing_documents}
            - Discrepancies: {validation_result.discrepancies}
            - Warnings: {validation_result.warnings}
            
            Consider the following factors:
            1. Document completeness and authenticity
            2. Data consistency across documents
            3. Medical necessity and reasonableness of charges
            4. Policy coverage and limits
            
            Respond with a JSON object in this format:
            {{
                "status": "approved" or "rejected" or "pending",
                "reason": "Detailed explanation for the decision",
                "confidence": 0.85,
                "recommended_amount": 12345.67
            }}
            
            Return only the JSON object, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            ai_result = self._parse_ai_response(response.text)
            
            if ai_result:
                return ClaimDecision(**ai_result)
            else:
                # Fallback to rule-based decision if AI parsing fails
                return rule_decision
                
        except Exception as e:
            print(f"Error in AI-assisted decision: {e}")
            return rule_decision
    
    def _prepare_data_summary(self, extracted_data: List[ExtractedData], 
                            validation_result: ValidationResult) -> str:
        """
        Prepare a summary of extracted data for AI processing.
        """
        summary_parts = []
        
        for data in extracted_data:
            doc_summary = f"\n{data.document_type.upper()}:"
            doc_summary += f"\n  Confidence: {data.extraction_confidence:.2f}"
            
            # Add key fields based on document type
            if data.document_type == "hospital_bill":
                doc_summary += f"\n  Hospital: {data.data.get('hospital_name', 'N/A')}"
                doc_summary += f"\n  Patient: {data.data.get('patient_name', 'N/A')}"
                doc_summary += f"\n  Total Amount: ₹{data.data.get('total_amount', 'N/A')}"
                doc_summary += f"\n  Service Date: {data.data.get('date_of_service', 'N/A')}"
                
            elif data.document_type == "discharge_summary":
                doc_summary += f"\n  Patient: {data.data.get('patient_name', 'N/A')}"
                doc_summary += f"\n  Diagnosis: {data.data.get('diagnosis', 'N/A')}"
                doc_summary += f"\n  Admission: {data.data.get('admission_date', 'N/A')}"
                doc_summary += f"\n  Discharge: {data.data.get('discharge_date', 'N/A')}"
                
            elif data.document_type == "insurance_card":
                doc_summary += f"\n  Card Holder: {data.data.get('card_holder_name', 'N/A')}"
                doc_summary += f"\n  Policy Number: {data.data.get('policy_number', 'N/A')}"
                doc_summary += f"\n  Sum Insured: ₹{data.data.get('sum_insured', 'N/A')}"
                doc_summary += f"\n  Insurance Company: {data.data.get('insurance_company', 'N/A')}"
            
            summary_parts.append(doc_summary)
        
        return "\n".join(summary_parts)
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response to extract decision data.
        """
        try:
            import json
            import re
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return None
        except json.JSONDecodeError:
            return None
    
    def _get_claim_amount(self, extracted_data: List[ExtractedData]) -> Optional[float]:
        """
        Extract the claim amount from the data.
        """
        for data in extracted_data:
            if data.document_type == "hospital_bill":
                amount = data.data.get("total_amount")
                if amount and isinstance(amount, (int, float)):
                    return float(amount)
        return None
    
    def _is_claim_valid(self, extracted_data: List[ExtractedData]) -> bool:
        """
        Check if the claim meets basic validity requirements.
        """
        # Check if we have at least one document with reasonable confidence
        has_valid_doc = any(data.extraction_confidence > 0.3 for data in extracted_data)
        
        # Check if we have essential information
        has_patient_info = False
        has_amount_info = False
        
        for data in extracted_data:
            if data.document_type in ["hospital_bill", "discharge_summary"]:
                if data.data.get("patient_name"):
                    has_patient_info = True
            
            if data.document_type == "hospital_bill":
                if data.data.get("total_amount"):
                    has_amount_info = True
        
        return has_valid_doc and has_patient_info and has_amount_info

