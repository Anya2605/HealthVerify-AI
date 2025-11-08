"""
Agent 1: Data Validation Agent
Validates provider contact information using public APIs and web sources
"""
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.npi_service import NPIService
from services.location_service import LocationService
from services.phone_service import PhoneService
from services.web_scraper import WebScraper
from utils.confidence_scorer import ConfidenceScorer
from fuzzywuzzy import fuzz


class DataValidationAgent:
    """
    AGENT NAME: Data Validation Agent
    AGENT ID: DVA-001
    PRIMARY FUNCTION: Validate provider contact information using public APIs and web sources
    """
    
    def __init__(self):
        self.npi_service = NPIService()
        self.location_service = LocationService()
        self.phone_service = PhoneService()
        self.web_scraper = WebScraper()
        self.confidence_scorer = ConfidenceScorer()
    
    def validate_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation method - validates provider data using all available sources
        
        Args:
            provider_data: Provider data dictionary with required fields
            
        Returns:
            Complete validation result dictionary
        """
        start_time = time.time()
        provider_id = provider_data.get('provider_id', 'UNKNOWN')
        
        # Initialize validation result structure
        validation_result = {
            'provider_id': provider_id,
            'npi': provider_data.get('npi', ''),
            'name': provider_data.get('full_name', ''),
            'validation_timestamp': datetime.now().isoformat(),
            'validation_duration_seconds': 0.0,
            'validations': {},
            'overall_confidence': 0.0,
            'validation_status': 'PENDING',
            'flags': [],
            'recommendations': [],
            'sources_used': []
        }
        
        try:
            # Step 1: NPI Validation (HIGHEST PRIORITY)
            npi_validation = self._validate_npi(provider_data)
            validation_result['validations']['npi'] = npi_validation
            validation_result['sources_used'].append(npi_validation.get('source', 'NPI Registry (CMS)'))
            
            # Step 2: Address Validation
            address_validation = self._validate_address(provider_data)
            validation_result['validations']['address'] = address_validation
            if address_validation.get('source'):
                validation_result['sources_used'].append(address_validation['source'])
            
            # Step 3: Phone Number Validation
            phone_validation = self._validate_phone(provider_data)
            validation_result['validations']['phone'] = phone_validation
            validation_result['sources_used'].append(phone_validation.get('source', 'NumVerify API'))
            
            # Step 4: Web Presence Verification
            web_validation = self._validate_web_presence(provider_data)
            validation_result['validations']['website'] = web_validation
            if web_validation.get('source'):
                validation_result['sources_used'].append(web_validation['source'])
            
            # Step 5: Cross-Validation & Confidence Aggregation
            validation_result = self.confidence_scorer.score_validation_result(validation_result)
            
            # Step 6: Flag Generation
            flags = self._generate_flags(validation_result, provider_data)
            validation_result['flags'] = flags
            
            # Calculate duration
            validation_result['validation_duration_seconds'] = round(time.time() - start_time, 2)
            
            return validation_result
            
        except Exception as e:
            validation_result['validation_status'] = 'ERROR'
            validation_result['error'] = str(e)
            validation_result['validation_duration_seconds'] = round(time.time() - start_time, 2)
            return validation_result
    
    def _validate_npi(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: NPI Validation"""
        npi = provider_data.get('npi', '')
        
        # Validate NPI
        npi_result = self.npi_service.validate_npi(npi)
        
        # Compare with input data
        if npi_result.get('valid'):
            npi_result = self.npi_service.compare_with_input(npi_result, provider_data)
        
        # Adjust confidence based on matches
        if not npi_result.get('matches_input', True) and npi_result.get('valid'):
            npi_result['confidence'] = 60
            npi_result['matches_input'] = False
        
        return npi_result
    
    def _validate_address(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Address Validation"""
        address = provider_data.get('practice_address', '')
        city = provider_data.get('city', '')
        state = provider_data.get('state', '')
        zip_code = provider_data.get('zip_code', '')
        
        if not all([address, city, state, zip_code]):
            return {
                'valid': False,
                'confidence': 30,
                'source': None,
                'error': 'Incomplete address information',
                'verified_data': None
            }
        
        return self.location_service.validate_address(address, city, state, zip_code)
    
    def _validate_phone(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Phone Number Validation"""
        phone = provider_data.get('phone', '')
        
        if not phone:
            return {
                'valid': False,
                'confidence': 40,
                'source': 'NumVerify API',
                'error': 'No phone number provided',
                'verified_data': None
            }
        
        return self.phone_service.validate_phone(phone)
    
    def _validate_web_presence(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Web Presence Verification"""
        full_name = provider_data.get('full_name', '')
        city = provider_data.get('city', '')
        state = provider_data.get('state', '')
        phone = provider_data.get('phone', '')
        address = provider_data.get('practice_address', '')
        
        if not full_name or not city or not state:
            return {
                'valid': False,
                'confidence': 50,
                'source': 'Web Scraping',
                'error': 'Insufficient information for web search',
                'verified_data': {
                    'url': None,
                    'phone_on_site': None,
                    'address_on_site': None,
                    'last_updated': None
                }
            }
        
        # Construct full address for comparison
        full_address = f"{address}, {city}, {state}"
        
        return self.web_scraper.verify_provider_web_presence(
            full_name, city, state, phone, full_address
        )
    
    def _generate_flags(self, validation_result: Dict[str, Any], provider_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Step 6: Flag Generation"""
        flags = []
        validations = validation_result.get('validations', {})
        provider_id = validation_result.get('provider_id', '')
        
        # CRITICAL FLAGS
        npi_validation = validations.get('npi', {})
        if not npi_validation.get('valid'):
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'CRITICAL',
                'severity': 'high',
                'field': 'npi',
                'message': 'NPI not found in registry or invalid',
                'details': {
                    'error': npi_validation.get('error', 'Unknown error'),
                    'npi': provider_data.get('npi', '')
                }
            })
        elif not npi_validation.get('matches_input', True):
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'CRITICAL',
                'severity': 'high',
                'field': 'npi',
                'message': 'NPI belongs to different provider - name mismatch',
                'details': {
                    'input_name': provider_data.get('full_name', ''),
                    'npi_name': npi_validation.get('verified_data', {}).get('name', '')
                }
            })
        
        # Address validation flags
        address_validation = validations.get('address', {})
        if not address_validation.get('valid'):
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'CRITICAL',
                'severity': 'high',
                'field': 'address',
                'message': 'Address completely invalid or cannot be geocoded',
                'details': {
                    'error': address_validation.get('error', 'Unknown error'),
                    'input_address': f"{provider_data.get('practice_address', '')}, {provider_data.get('city', '')}, {provider_data.get('state', '')}"
                }
            })
        elif address_validation.get('confidence', 0) < 60:
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'WARNING',
                'severity': 'medium',
                'field': 'address',
                'message': 'Address partial match only - verify address',
                'details': {
                    'confidence': address_validation.get('confidence', 0),
                    'match_quality': address_validation.get('verified_data', {}).get('match_quality', 'unknown')
                }
            })
        
        # Phone validation flags
        phone_validation = validations.get('phone', {})
        if not phone_validation.get('valid'):
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'WARNING',
                'severity': 'medium',
                'field': 'phone',
                'message': 'Phone number validation failed',
                'details': {
                    'error': phone_validation.get('error', 'Unknown error'),
                    'input_phone': provider_data.get('phone', '')
                }
            })
        else:
            phone_data = phone_validation.get('verified_data', {})
            if phone_data.get('line_type') == 'unknown' and not phone_data.get('carrier'):
                flags.append({
                    'provider_id': provider_id,
                    'flag_type': 'WARNING',
                    'severity': 'medium',
                    'field': 'phone',
                    'message': 'Phone number may be disconnected - carrier unknown',
                    'details': {
                        'line_type': phone_data.get('line_type', 'unknown')
                    }
                })
        
        # Website flags
        web_validation = validations.get('website', {})
        if not web_validation.get('valid'):
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'INFO',
                'severity': 'low',
                'field': 'website',
                'message': 'No website found for provider',
                'details': {
                    'error': web_validation.get('error', 'No website found')
                }
            })
        elif web_validation.get('confidence', 0) < 60:
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'WARNING',
                'severity': 'medium',
                'field': 'website',
                'message': 'Website information contradicts input data',
                'details': {
                    'confidence': web_validation.get('confidence', 0),
                    'matches': web_validation.get('matches', [])
                }
            })
        
        # Check for multiple data source conflicts
        valid_count = sum(1 for v in validations.values() if v.get('valid', False))
        if valid_count == 1 and len(validations) > 1:
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'WARNING',
                'severity': 'medium',
                'field': 'multiple',
                'message': 'Multiple data source conflicts - only one source validated successfully',
                'details': {
                    'valid_sources': valid_count,
                    'total_sources': len(validations)
                }
            })
        
        # Check if all contact methods failed
        if not any([npi_validation.get('valid'), address_validation.get('valid'), 
                   phone_validation.get('valid')]):
            flags.append({
                'provider_id': provider_id,
                'flag_type': 'CRITICAL',
                'severity': 'high',
                'field': 'all',
                'message': 'All contact methods failed validation',
                'details': {
                    'npi_valid': npi_validation.get('valid', False),
                    'address_valid': address_validation.get('valid', False),
                    'phone_valid': phone_validation.get('valid', False)
                }
            })
        
        return flags
    
    def batch_validate(self, providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate multiple providers in batch
        
        Args:
            providers: List of provider data dictionaries
            
        Returns:
            List of validation results
        """
        results = []
        for provider in providers:
            result = self.validate_provider(provider)
            results.append(result)
        return results

