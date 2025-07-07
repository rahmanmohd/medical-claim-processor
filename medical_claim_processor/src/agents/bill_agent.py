import re
from datetime import datetime
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent
from src.models.data_models import ExtractedData, HospitalBillData

class BillAgent(BaseAgent):
    """
    Agent specialized in extracting data from hospital bills.
    """
    
    def __init__(self):
        super().__init__("hospital_bill")
    
    async def extract_data(self, text_content: str) -> ExtractedData:
        """
        Extract structured data from hospital bill text.
        """
        # Clean the text
        cleaned_text = self._clean_text_for_processing(text_content)
        
        # Try LLM extraction first
        llm_data = await self._llm_extract_bill_data(cleaned_text)
        
        # Fallback to rule-based extraction
        rule_based_data = self._rule_based_extract(cleaned_text)
        
        # Combine results, preferring LLM data when available
        final_data = self._combine_extraction_results(llm_data, rule_based_data)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(final_data, cleaned_text)
        
        return ExtractedData(
            document_type="hospital_bill",
            data=final_data,
            extraction_confidence=confidence,
            raw_text=text_content
        )
    
    async def _llm_extract_bill_data(self, text_content: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to extract bill data.
        """
        prompt = """
        Extract the following information from this hospital bill and return it as a JSON object:
        
        {
            "hospital_name": "Name of the hospital",
            "total_amount": 123.45,
            "date_of_service": "YYYY-MM-DD",
            "patient_name": "Patient's name",
            "admission_date": "YYYY-MM-DD",
            "discharge_date": "YYYY-MM-DD",
            "insurance_company": "Insurance company name",
            "policy_number": "Policy number",
            "items": [
                {
                    "description": "Service description",
                    "amount": 123.45,
                    "quantity": 1
                }
            ]
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
            "hospital_name": self._extract_hospital_name(text_content),
            "total_amount": self._extract_total_amount(text_content),
            "date_of_service": self._extract_service_date(text_content),
            "patient_name": self._extract_patient_name(text_content),
            "admission_date": self._extract_admission_date(text_content),
            "discharge_date": self._extract_discharge_date(text_content),
            "insurance_company": self._extract_insurance_company(text_content),
            "policy_number": self._extract_policy_number(text_content),
            "items": self._extract_line_items(text_content)
        }
        
        return data
    
    def _extract_hospital_name(self, text: str) -> Optional[str]:
        """Extract hospital name from text."""
        # Look for common hospital name patterns
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
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text."""
        # Look for total amount patterns
        patterns = [
            r'(?:Total|Grand Total|Net Amount|Bill Amount)[\s:]*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?[0-9]*)',
            r'(?:₹|Rs\.?)\s*([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*(?:/-|Rs|INR)'
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue
        
        # Return the largest amount found (likely to be the total)
        return max(amounts) if amounts else None
    
    def _extract_service_date(self, text: str) -> Optional[str]:
        """Extract service date from text."""
        return self._extract_date_pattern(text, ['service', 'treatment', 'visit'])
    
    def _extract_admission_date(self, text: str) -> Optional[str]:
        """Extract admission date from text."""
        return self._extract_date_pattern(text, ['admission', 'admit'])
    
    def _extract_discharge_date(self, text: str) -> Optional[str]:
        """Extract discharge date from text."""
        return self._extract_date_pattern(text, ['discharge'])
    
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
    
    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from text."""
        patterns = [
            r'(?:Patient|Name)[\s:]*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?:Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Name[\s:]*([A-Z][A-Z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_insurance_company(self, text: str) -> Optional[str]:
        """Extract insurance company name."""
        patterns = [
            r'(ACKO General Insurance)',
            r'(Family Health Plan)',
            r'(SBI General Insurance)',
            r'([A-Z][a-z]+ Insurance)',
            r'Insurance Company[\s:]*([A-Z][a-z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_policy_number(self, text: str) -> Optional[str]:
        """Extract policy number."""
        patterns = [
            r'Policy[\s\w]*[:\s]*([A-Z0-9\-]+)',
            r'([0-9]{10,})',  # Long numeric sequences
            r'([A-Z]{2,}[0-9]{8,})'  # Alphanumeric policy numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_line_items(self, text: str) -> list:
        """Extract line items from the bill."""
        items = []
        
        # Look for itemized charges
        lines = text.split('\n')
        for line in lines:
            # Look for lines with description and amount
            amount_match = re.search(r'([0-9,]+\.?[0-9]*)', line)
            if amount_match and len(line.strip()) > 10:
                try:
                    amount = float(amount_match.group(1).replace(',', ''))
                    description = re.sub(r'[0-9,]+\.?[0-9]*', '', line).strip()
                    if description and amount > 0:
                        items.append({
                            "description": description,
                            "amount": amount,
                            "quantity": 1
                        })
                except ValueError:
                    continue
        
        return items[:10]  # Limit to first 10 items
    
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
        total_fields = 8
        
        # Check if key fields are extracted
        if data.get('hospital_name'):
            score += 0.2
        if data.get('total_amount'):
            score += 0.2
        if data.get('patient_name'):
            score += 0.15
        if data.get('date_of_service') or data.get('admission_date'):
            score += 0.15
        if data.get('insurance_company'):
            score += 0.1
        if data.get('policy_number'):
            score += 0.1
        if data.get('items') and len(data['items']) > 0:
            score += 0.1
        
        return min(score, 1.0)

