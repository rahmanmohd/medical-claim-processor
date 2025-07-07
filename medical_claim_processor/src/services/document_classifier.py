import google.generativeai as genai
import os
from typing import Literal
from src.models.data_models import ClassifiedDocument

class DocumentClassifier:
    def __init__(self):
        # Configure Gemini API
        # Note: In production, use environment variables for API keys
        api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
        if api_key != 'your-api-key-here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def classify(self, file_id: str, filename: str, text_content: str) -> ClassifiedDocument:
        """
        Classify a document based on its filename and text content.
        """
        # Use the passed file_id
        # file_id = filename  # Simplified for now
        
        # If no model is available, use rule-based classification
        if self.model is None:
            return self._rule_based_classify(file_id, filename, text_content)
        
        try:
            # Use LLM for classification
            return await self._llm_classify(file_id, filename, text_content)
        except Exception as e:
            print(f"LLM classification failed: {e}")
            # Fallback to rule-based classification
            return self._rule_based_classify(file_id, filename, text_content)
    
    def _rule_based_classify(self, file_id: str, filename: str, text_content: str) -> ClassifiedDocument:
        """
        Rule-based document classification as fallback.
        """
        filename_lower = filename.lower()
        text_lower = text_content.lower()
        
        # Check for hospital bill indicators
        bill_keywords = ['bill', 'invoice', 'charges', 'amount', 'total', 'hospital', 'medical']
        discharge_keywords = ['discharge', 'summary', 'diagnosis', 'admission', 'patient']
        insurance_keywords = ['insurance', 'policy', 'card', 'coverage', 'premium']
        
        bill_score = sum(1 for keyword in bill_keywords if keyword in filename_lower or keyword in text_lower)
        discharge_score = sum(1 for keyword in discharge_keywords if keyword in filename_lower or keyword in text_lower)
        insurance_score = sum(1 for keyword in insurance_keywords if keyword in filename_lower or keyword in text_lower)
        
        # Determine document type based on highest score
        if bill_score >= discharge_score and bill_score >= insurance_score:
            doc_type = "hospital_bill"
            confidence = min(0.9, bill_score / len(bill_keywords))
        elif discharge_score >= insurance_score:
            doc_type = "discharge_summary"
            confidence = min(0.9, discharge_score / len(discharge_keywords))
        elif insurance_score > 0:
            doc_type = "insurance_card"
            confidence = min(0.9, insurance_score / len(insurance_keywords))
        else:
            doc_type = "other"
            confidence = 0.1
        
        return ClassifiedDocument(
            file_id=file_id,
            document_type=doc_type,
            confidence=confidence
        )
    
    async def _llm_classify(self, file_id: str, filename: str, text_content: str) -> ClassifiedDocument:
        """
        Use LLM for document classification.
        """
        prompt = f"""
        You are a medical document classifier. Analyze the following document and classify it into one of these categories:
        - hospital_bill: Medical bills, invoices, or billing statements
        - discharge_summary: Hospital discharge summaries or medical reports
        - insurance_card: Insurance cards or policy documents
        - other: Any other type of document
        
        Document filename: {filename}
        
        Document content (first 2000 characters):
        {text_content[:2000]}
        
        Respond with only the classification category (hospital_bill, discharge_summary, insurance_card, or other) and a confidence score between 0 and 1, separated by a comma.
        Example: hospital_bill,0.95
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse the response
            parts = result.split(',')
            if len(parts) == 2:
                doc_type = parts[0].strip()
                confidence = float(parts[1].strip())
                
                # Validate document type
                valid_types = ["hospital_bill", "discharge_summary", "insurance_card", "other"]
                if doc_type not in valid_types:
                    doc_type = "other"
                    confidence = 0.1
                
                return ClassifiedDocument(
                    file_id=file_id,
                    document_type=doc_type,
                    confidence=confidence
                )
            else:
                # Fallback if parsing fails
                return self._rule_based_classify(file_id, filename, text_content)
                
        except Exception as e:
            print(f"Error in LLM classification: {e}")
            return self._rule_based_classify(file_id, filename, text_content)

