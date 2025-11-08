"""
Gemini AI Service for document extraction and OCR
"""
import google.generativeai as genai
import sys
import os
from typing import Dict, Any, Optional
import base64
import io
from PIL import Image
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class GeminiService:
    """Service for Gemini AI document processing"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
        else:
            self.model = None
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from image using Gemini Vision
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Gemini API key not configured',
                'text': None
            }
        
        try:
            img = Image.open(image_path)
            response = self.model.generate_content([
                "Extract all text from this image. Return only the text content.",
                img
            ])
            
            return {
                'success': True,
                'text': response.text,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': None
            }
    
    def extract_provider_info_from_document(self, document_text: str) -> Dict[str, Any]:
        """
        Extract provider information from document text using Gemini
        
        Args:
            document_text: Text content from document
            
        Returns:
            Dictionary with extracted provider information
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Gemini API key not configured',
                'extracted_data': None
            }
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Extract healthcare provider information from the following document text.
            Return a JSON object with the following fields if available:
            - name: Provider full name
            - npi: National Provider Identifier
            - license_number: Medical license number
            - specialty: Medical specialty
            - address: Practice address
            - city: City
            - state: State
            - zip_code: ZIP code
            - phone: Phone number
            - email: Email address
            - license_expiry: License expiration date
            - issue_date: License issue date
            
            Document text:
            {document_text}
            
            Return only valid JSON, no additional text.
            """
            
            response = model.generate_content(prompt)
            
            # Try to parse JSON from response
            import json
            try:
                # Extract JSON from response (might have markdown code blocks)
                text = response.text.strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                text = text.strip()
                
                extracted_data = json.loads(text)
                return {
                    'success': True,
                    'extracted_data': extracted_data,
                    'error': None
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': 'Failed to parse JSON from Gemini response',
                    'extracted_data': None,
                    'raw_response': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'extracted_data': None
            }

