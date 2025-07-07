import re
from datetime import datetime
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent
from src.models.data_models import ExtractedData, InsuranceCardData

class InsuranceAgent(BaseAgent):
    """
    Agent specialized in extracting data from insurance cards and policy documents.
    """
    
    def __init__(self):
        super().__init__("insurance_card")
    
    async def extract_data(self, text_content: str) -> ExtractedData:
        """
        Extract structured data from insurance card text.
        """
        # Clean the text
        cleaned_text = self._clean_text_for_processing(text_content)
        
        # Try LLM extraction first
        llm_data = await self._llm_extract_insurance_data(cleaned_text)
        
        # Fallback to rule-based extraction
        rule_based_data = self._rule_based_extract(cleaned_text)
        
        # Combine results
        final_data = self._combine_extraction_results(llm_data, rule_based_data)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(final_data, cleaned_text)
        
        return ExtractedData(
            document_type="insurance_card",
            data=final_data,
            extraction_confidence=confidence,
            raw_text=text_content
        )
    
    async def _llm_extract_insurance_data(self, text_content: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to extract insurance card data.
        """
        prompt = """
        Extract the following information from this insurance card or policy document and return it as a JSON object:
        
        {
            "policy_number": "Policy or card number",
            "card_holder_name": "Name of the card holder",
            "insurance_company": "Insurance company name",
            "sum_insured": 123456.78,
            "validity_date": "YYYY-MM-DD"
        }
        
        If any field is not found, use null. For dates, use YYYY-MM-DD format.
        For sum_insured, extract the numeric value only.
        Return only the JSON object, no additional text.
        """
        
        return await self._llm_extract(prompt, text_content)
    
    def _rule_based_extract(self, text_content: str) -> Dict[str, Any]:
        """
        Rule-based extraction as fallback.
        """
        data = {
            "policy_number": self._extract_policy_number(text_content),
            "card_holder_name": self._extract_card_holder_name(text_content),
            "insurance_company": self._extract_insurance_company(text_content),
            "sum_insured": self._extract_sum_insured(text_content),
            "validity_date": self._extract_validity_date(text_content)
        }
        
        return data
    
    def _extract_policy_number(self, text: str) -> Optional[str]:
        """Extract policy number from text."""
        patterns = [
            r'(?:Policy|Card|Member)[\s\w]*[:\s]*([A-Z0-9\-]{8,})',
            r'([0-9]{10,})',  # Long numeric sequences
            r'([A-Z]{2,}[0-9]{8,})',  # Alphanumeric policy numbers
            r'Policy No[\s.:]*([A-Z0-9\-]+)',
            r'Card No[\s.:]*([A-Z0-9\-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                policy_num = match.group(1).strip()
                # Validate policy number (should be at least 8 characters)
                if len(policy_num) >= 8:
                    return policy_num
        
        return None
    
    def _extract_card_holder_name(self, text: str) -> Optional[str]:
        """Extract card holder name from text."""
        patterns = [
            r'(?:Name|Card Holder|Member)[\s:]*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?:Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Member Name[\s:]*([A-Za-z\s]+)',
            r'Insured[\s:]*([A-Z][a-z]+ [A-Z][a-z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validate name (should have at least 2 words)
                if len(name.split()) >= 2:
                    return name
        
        return None
    
    def _extract_insurance_company(self, text: str) -> Optional[str]:
        """Extract insurance company name."""
        patterns = [
            r'(ACKO General Insurance)',
            r'(SBI General Insurance)',
            r'(Family Health Plan)',
            r'(HDFC ERGO)',
            r'(ICICI Lombard)',
            r'(Bajaj Allianz)',
            r'(Star Health)',
            r'(Max Bupa)',
            r'([A-Z][a-z]+ Insurance)',
            r'Insurance Company[\s:]*([A-Z][a-z\s]+)',
            r'Insurer[\s:]*([A-Z][a-z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 3:  # Ensure it's not too short
                    return company
        
        return None
    
    def _extract_sum_insured(self, text: str) -> Optional[float]:
        """Extract sum insured amount."""
        patterns = [
            r'(?:Sum Insured|Coverage|Limit)[\s:]*(?:Rs\.?|INR|₹)?\s*([0-9,]+\.?[0-9]*)',
            r'(?:₹|Rs\.?)\s*([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*(?:/-|Rs|INR)',
            r'Coverage[\s:]*([0-9,]+)',
            r'Limit[\s:]*([0-9,]+)'
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    amount = float(match.replace(',', ''))
                    # Filter out unreasonably small amounts (likely not sum insured)
                    if amount >= 10000:
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Return the largest amount found (likely to be the sum insured)
        return max(amounts) if amounts else None
    
    def _extract_validity_date(self, text: str) -> Optional[str]:
        """Extract validity or expiry date."""
        return self._extract_date_pattern(text, ['validity', 'valid', 'expiry', 'expires', 'until'])
    
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
        if data.get('policy_number'):
            score += 0.3
        if data.get('card_holder_name'):
            score += 0.25
        if data.get('insurance_company'):
            score += 0.25
        if data.get('sum_insured'):
            score += 0.15
        if data.get('validity_date'):
            score += 0.05
        
        return min(score, 1.0)

