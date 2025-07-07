import google.generativeai as genai
import os
import json
import re
from typing import Dict, Any, Optional
from src.models.data_models import ExtractedData

class BaseAgent:
    """
    Base class for all document processing agents.
    """
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
        if api_key != 'your-api-key-here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def extract_data(self, text_content: str) -> ExtractedData:
        """
        Extract structured data from text content.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement extract_data method")
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response text.
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # If no JSON found, try to parse the entire response
                return json.loads(response_text)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response: {response_text}")
            return None
    
    def _clean_text_for_processing(self, text: str) -> str:
        """
        Clean text for better LLM processing.
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with JSON parsing
        text = text.replace('\x00', '')
        return text.strip()
    
    async def _llm_extract(self, prompt: str, text_content: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to extract data based on a prompt.
        """
        if self.model is None:
            return None
        
        try:
            full_prompt = f"{prompt}\n\nDocument text:\n{text_content[:4000]}"
            response = self.model.generate_content(full_prompt)
            return self._extract_json_from_response(response.text)
        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            return None

