import re
from datetime import datetime
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent
from src.models.data_models import ExtractedData, DischargeSummaryData

class DischargeAgent(BaseAgent):
    """
    Agent specialized in extracting data from discharge summaries.
    """
    
    def __init__(self):
        super().__init__("discharge_summary")
    
    async def extract_data(self, text_content: str) -> ExtractedData:
        """
        Extract structured data from discharge summary text.
        """
        # Clean the text
        cleaned_text = self._clean_text_for_processing(text_content)
        
        # Try LLM extraction first
        llm_data = await self._llm_extract_discharge_data(cleaned_text)
        
        # Fallback to rule-based extraction
        rule_based_data = self._rule_based_extract(cleaned_text)
        
        # Combine results
        final_data = self._combine_extraction_results(llm_data, rule_based_data)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(final_data, cleaned_text)
        
        return ExtractedData(
            document_type="discharge_summary",
            data=final_data,
            extraction_confidence=confidence,
            raw_text=text_content
        )
    
    async def _llm_extract_discharge_data(self, text_content: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to extract discharge summary data.
        """
        prompt = """
        Extract the following information from this discharge summary and return it as a JSON object:
        
        {
            "patient_name": "Patient's full name",
            "diagnosis": "Primary diagnosis or condition",
            "admission_date": "YYYY-MM-DD",
            "discharge_date": "YYYY-MM-DD",
            "doctor_name": "Attending physician name",
            "hospital_name": "Hospital name",
            "treatment_summary": "Brief summary of treatment provided"
        }
        
        If any field is not found, use null. For dates, use YYYY-MM-DD format.
        Return only the JSON object, no additional text.
        """
        
        return await self._llm_extract(prompt, text_content)
    
    def _rule_based_extract(self, text_content: str) -> Dict[str, Any]:
        """
        Rule-based extraction as fallback.
        """
        data = {
            "patient_name": self._extract_patient_name(text_content),
            "diagnosis": self._extract_diagnosis(text_content),
            "admission_date": self._extract_admission_date(text_content),
            "discharge_date": self._extract_discharge_date(text_content),
            "doctor_name": self._extract_doctor_name(text_content),
            "hospital_name": self._extract_hospital_name(text_content),
            "treatment_summary": self._extract_treatment_summary(text_content)
        }
        
        return data
    
    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text."""
        patterns = [
            r'(?:Patient|Name)[\s:]*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?:Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Name[\s:]*([A-Z][A-Z\s]+)',
            r'Patient Name[\s:]*([A-Za-z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Validate name (should have at least 2 words)
                if len(name.split()) >= 2:
                    return name
        
        return None
    
    def _extract_diagnosis(self, text: str) -> Optional[str]:
        """Extract primary diagnosis from text."""
        patterns = [
            r'(?:Diagnosis|Primary Diagnosis|Final Diagnosis)[\s:]*([A-Za-z\s,\-]+?)(?:\n|\.)',
            r'(?:Condition|Medical Condition)[\s:]*([A-Za-z\s,\-]+?)(?:\n|\.)',
            r'(?:Admitted for|Treated for)[\s:]*([A-Za-z\s,\-]+?)(?:\n|\.)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                diagnosis = match.group(1).strip()
                # Clean up the diagnosis
                diagnosis = re.sub(r'\s+', ' ', diagnosis)
                if len(diagnosis) > 5:  # Ensure it's not too short
                    return diagnosis
        
        return None
    
    def _extract_admission_date(self, text: str) -> Optional[str]:
        """Extract admission date from text."""
        return self._extract_date_pattern(text, ['admission', 'admit', 'admitted'])
    
    def _extract_discharge_date(self, text: str) -> Optional[str]:
        """Extract discharge date from text."""
        return self._extract_date_pattern(text, ['discharge', 'discharged'])
    
    def _extract_date_pattern(self, text: str, keywords: list) -> Optional[str]:
        """Extract date based on keywords."""
        # Date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(\d{1,2}\s+\w+\s+\d{4})'
        ]
        
        for keyword in keywords:
            # Look for keyword followed by date
            for pattern in date_patterns:
                regex = rf'{keyword}[:\s]*{pattern}'
                match = re.search(regex, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    return self._normalize_date(date_str)
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to YYYY-MM-DD format."""
        try:
            # Try different date formats
            formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return None
        except:
            return None
    
    def _extract_doctor_name(self, text: str) -> Optional[str]:
        """Extract attending doctor name."""
        patterns = [
            r'(?:Dr\.?|Doctor)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?:Attending|Consultant)[\s\w]*[:\s]*(?:Dr\.?)\s*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?:Physician|Surgeon)[\s:]*(?:Dr\.?)\s*([A-Z][a-z]+ [A-Z][a-z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_hospital_name(self, text: str) -> Optional[str]:
        """Extract hospital name from text."""
        patterns = [
            r'([A-Z][a-z]+ (?:Hospital|Medical|Health|Care|Centre|Center))',
            r'((?:Sir |Dr\. )?[A-Z][a-z]+ [A-Z][a-z]+ Hospital)',
            r'([A-Z][A-Z\s]+HOSPITAL)',
            r'(Max Healthcare|Fortis|Apollo|AIIMS|PGIMER)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_treatment_summary(self, text: str) -> Optional[str]:
        """Extract treatment summary from text."""
        # Look for treatment or procedure sections
        patterns = [
            r'(?:Treatment|Procedure|Management)[\s:]*([A-Za-z\s,\.\-]+?)(?:\n\n|\n[A-Z])',
            r'(?:Summary|Course)[\s:]*([A-Za-z\s,\.\-]+?)(?:\n\n|\n[A-Z])'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Clean up the summary
                summary = re.sub(r'\s+', ' ', summary)
                if len(summary) > 20:  # Ensure it's substantial
                    return summary[:500]  # Limit length
        
        return None
    
    def _combine_extraction_results(self, llm_data: Optional[Dict[str, Any]], 
                                  rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine LLM and rule-based extraction results."""
        if llm_data is None:
            return rule_data
        
        # Prefer LLM data, but use rule-based as fallback
        combined = {}
        for key in rule_data.keys():
            combined[key] = llm_data.get(key) or rule_data.get(key)
        
        return combined
    
    def _calculate_confidence(self, data: Dict[str, Any], text: str) -> float:
        """Calculate confidence score based on extracted data quality."""
        score = 0.0
        
        # Check if key fields are extracted
        if data.get('patient_name'):
            score += 0.2
        if data.get('diagnosis'):
            score += 0.25
        if data.get('admission_date'):
            score += 0.15
        if data.get('discharge_date'):
            score += 0.15
        if data.get('doctor_name'):
            score += 0.1
        if data.get('hospital_name'):
            score += 0.1
        if data.get('treatment_summary'):
            score += 0.05
        
        return min(score, 1.0)

