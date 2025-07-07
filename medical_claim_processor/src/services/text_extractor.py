import subprocess
import tempfile
import os
from typing import Optional

class TextExtractor:
    """
    Service for extracting text from various document formats.
    """
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using pdftotext.
        """
        try:
            result = subprocess.run(
                ['pdftotext', pdf_path, '-'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
        except FileNotFoundError:
            print("pdftotext not found. Please install poppler-utils.")
            return ""
    
    def extract_from_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes by creating a temporary file.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_bytes)
            temp_file_path = temp_file.name
        
        try:
            text = self.extract_from_pdf(temp_file_path)
            return text
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_and_clean(self, pdf_path: str) -> str:
        """
        Extract and clean text from a PDF file.
        """
        raw_text = self.extract_from_pdf(pdf_path)
        return self.clean_text(raw_text)

