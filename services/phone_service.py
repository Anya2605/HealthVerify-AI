"""
Phone Number Validation Service using NumVerify API
"""
import requests
import time
import re
import sys
import os
from typing import Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class PhoneService:
    """Service for phone number validation"""
    
    def __init__(self):
        self.api_key = Config.NUMVERIFY_API_KEY
        self.base_url = "http://apilayer.net/api/validate"
        self.timeout = Config.API_TIMEOUT
        self.retry_attempts = Config.API_RETRY_ATTEMPTS
        self.retry_delay = Config.API_RETRY_DELAY
    
    def clean_phone(self, phone: str) -> str:
        """Clean phone number to digits only"""
        if not phone:
            return ""
        return re.sub(r'\D', '', phone)
    
    def validate_phone(self, phone: str) -> Dict[str, Any]:
        """
        Validate phone number using NumVerify API
        
        Args:
            phone: Phone number in any format
            
        Returns:
            Dictionary with validation results
        """
        cleaned_phone = self.clean_phone(phone)
        
        if not cleaned_phone or len(cleaned_phone) < 10:
            return {
                'valid': False,
                'confidence': 40,
                'source': 'NumVerify API',
                'error': 'Invalid phone format',
                'verified_data': None
            }
        
        # Remove leading 1 for US numbers if present
        if cleaned_phone.startswith('1') and len(cleaned_phone) == 11:
            cleaned_phone = cleaned_phone[1:]
        
        params = {
            'access_key': self.api_key,
            'number': cleaned_phone,
            'country_code': 'US',
            'format': 1
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('valid'):
                    return {
                        'valid': False,
                        'confidence': 40,
                        'source': 'NumVerify API',
                        'error': 'Phone number is not valid',
                        'verified_data': {
                            'number': cleaned_phone,
                            'valid_format': False
                        }
                    }
                
                # Check if number is active/reachable
                line_type = data.get('line_type', 'unknown')
                carrier = data.get('carrier', '')
                
                # Determine confidence based on validation results
                confidence = 70  # Base confidence for valid format
                
                if carrier:
                    confidence = 85  # Carrier confirmed
                
                if line_type in ['mobile', 'landline']:
                    confidence = max(confidence, 85)
                elif line_type == 'voip':
                    confidence = max(confidence, 70)
                elif line_type == 'unknown':
                    confidence = 70
                
                # Check if number appears disconnected
                if line_type == 'unknown' and not carrier:
                    confidence = 20  # Likely disconnected
                
                verified_data = {
                    'number': cleaned_phone,
                    'country': data.get('country_name', ''),
                    'country_code': data.get('country_code', ''),
                    'carrier': carrier,
                    'line_type': line_type,
                    'valid_format': True,
                    'local_format': data.get('local_format', ''),
                    'international_format': data.get('international_format', '')
                }
                
                return {
                    'valid': True,
                    'confidence': confidence,
                    'source': 'NumVerify API',
                    'verified_data': verified_data,
                    'error': None
                }
                
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return {
                        'valid': False,
                        'confidence': 50,
                        'source': 'NumVerify API',
                        'error': f'API request failed: {str(e)}',
                        'verified_data': None
                    }
            except Exception as e:
                return {
                    'valid': False,
                    'confidence': 50,
                    'source': 'NumVerify API',
                    'error': f'Unexpected error: {str(e)}',
                    'verified_data': None
                }
        
        return {
            'valid': False,
            'confidence': 50,
            'source': 'NumVerify API',
            'error': 'Max retry attempts exceeded',
            'verified_data': None
        }

