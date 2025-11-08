"""
NPI Registry API Service for provider verification
"""
import requests
import time
import sys
import os
from typing import Dict, Any, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class NPIService:
    """Service for querying CMS NPI Registry API"""
    
    def __init__(self):
        self.base_url = Config.NPI_REGISTRY_API_URL
        self.timeout = Config.API_TIMEOUT
        self.retry_attempts = Config.API_RETRY_ATTEMPTS
        self.retry_delay = Config.API_RETRY_DELAY
    
    def validate_npi(self, npi: str) -> Dict[str, Any]:
        """
        Validate NPI number against CMS NPI Registry
        
        Args:
            npi: National Provider Identifier (10 digits)
            
        Returns:
            Dictionary with validation results
        """
        if not npi or len(npi) != 10 or not npi.isdigit():
            return {
                'valid': False,
                'confidence': 0,
                'source': 'NPI Registry (CMS)',
                'error': 'Invalid NPI format',
                'verified_data': None,
                'matches_input': False
            }
        
        url = f"{self.base_url}?number={npi}&version=2.1"
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if data.get('result_count', 0) == 0:
                    return {
                        'valid': False,
                        'confidence': 0,
                        'source': 'NPI Registry (CMS)',
                        'error': 'NPI not found in registry',
                        'verified_data': None,
                        'matches_input': False
                    }
                
                # Extract provider information from first result
                result = data.get('results', [{}])[0]
                
                # Extract basic information
                basic_info = result.get('basic', {})
                name = f"{basic_info.get('first_name', '')} {basic_info.get('last_name', '')}".strip()
                organization_name = basic_info.get('organization_name', '')
                
                # Extract taxonomy (specialty)
                taxonomies = result.get('taxonomies', [])
                primary_taxonomy = taxonomies[0] if taxonomies else {}
                specialty = primary_taxonomy.get('desc', '')
                
                # Extract addresses
                addresses = result.get('addresses', [])
                primary_address = addresses[0] if addresses else {}
                
                # Extract phone
                phone = basic_info.get('telephone_number', '')
                
                verified_data = {
                    'npi': npi,
                    'name': name or organization_name,
                    'organization_name': organization_name,
                    'taxonomy': specialty,
                    'address': {
                        'address_1': primary_address.get('address_1', ''),
                        'city': primary_address.get('city', ''),
                        'state': primary_address.get('state', ''),
                        'postal_code': primary_address.get('postal_code', ''),
                        'country_code': primary_address.get('country_code', '')
                    },
                    'phone': phone,
                    'enumeration_type': result.get('enumeration_type', ''),
                    'status': basic_info.get('status', '')
                }
                
                return {
                    'valid': True,
                    'confidence': 100,
                    'source': 'NPI Registry (CMS)',
                    'verified_data': verified_data,
                    'matches_input': True,
                    'error': None
                }
                
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return {
                        'valid': False,
                        'confidence': 0,
                        'source': 'NPI Registry (CMS)',
                        'error': f'API request failed: {str(e)}',
                        'verified_data': None,
                        'matches_input': False
                    }
            except Exception as e:
                return {
                    'valid': False,
                    'confidence': 0,
                    'source': 'NPI Registry (CMS)',
                    'error': f'Unexpected error: {str(e)}',
                    'verified_data': None,
                    'matches_input': False
                }
        
        return {
            'valid': False,
            'confidence': 0,
            'source': 'NPI Registry (CMS)',
            'error': 'Max retry attempts exceeded',
            'verified_data': None,
            'matches_input': False
        }
    
    def compare_with_input(self, npi_result: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare NPI registry data with input provider data
        
        Args:
            npi_result: Result from validate_npi()
            input_data: Input provider data
            
        Returns:
            Updated validation result with match information
        """
        if not npi_result.get('valid'):
            return npi_result
        
        verified_data = npi_result.get('verified_data', {})
        matches = True
        confidence = 100
        
        # Compare name
        verified_name = verified_data.get('name', '').lower().strip()
        input_name = input_data.get('full_name', '').lower().strip()
        
        if verified_name and input_name:
            # Simple name matching (can be enhanced with fuzzy matching)
            if verified_name not in input_name and input_name not in verified_name:
                matches = False
                confidence = 60  # Name mismatch
        
        # Compare address
        verified_addr = verified_data.get('address', {})
        input_city = input_data.get('city', '').lower().strip()
        input_state = input_data.get('state', '').lower().strip()
        input_zip = input_data.get('zip_code', '').strip()
        
        verified_city = verified_addr.get('city', '').lower().strip()
        verified_state = verified_addr.get('state', '').lower().strip()
        verified_zip = verified_addr.get('postal_code', '').strip()
        
        if verified_city and input_city:
            if verified_city != input_city or verified_state != input_state:
                matches = False
                if confidence > 60:
                    confidence = 60
        
        # Compare phone (basic)
        verified_phone = verified_data.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        input_phone = input_data.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        if verified_phone and input_phone:
            if verified_phone[-10:] != input_phone[-10:]:  # Compare last 10 digits
                matches = False
                if confidence > 60:
                    confidence = 60
        
        npi_result['matches_input'] = matches
        npi_result['confidence'] = confidence
        
        return npi_result

