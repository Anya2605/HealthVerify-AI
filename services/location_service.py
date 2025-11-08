"""
Location/Geocoding Service using TomTom and LocationIQ APIs
"""
import requests
import time
import sys
import os
from typing import Dict, Any, Optional
from difflib import SequenceMatcher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class LocationService:
    """Service for geocoding and address validation"""
    
    def __init__(self):
        self.tomtom_key = Config.TOMTOM_API_KEY
        self.locationiq_key = Config.LOCATIONIQ_API_KEY
        self.timeout = Config.API_TIMEOUT
        self.retry_attempts = Config.API_RETRY_ATTEMPTS
        self.retry_delay = Config.API_RETRY_DELAY
    
    def validate_address(self, address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """
        Validate address using geocoding APIs
        
        Args:
            address: Street address
            city: City name
            state: State code
            zip_code: ZIP code
            
        Returns:
            Dictionary with validation results
        """
        full_address = f"{address}, {city}, {state} {zip_code}"
        
        # Try TomTom first
        result = self._geocode_tomtom(full_address, city, state, zip_code)
        
        # If TomTom fails, try LocationIQ as backup
        if not result.get('valid') or result.get('confidence', 0) < 60:
            locationiq_result = self._geocode_locationiq(full_address, city, state, zip_code)
            if locationiq_result.get('confidence', 0) > result.get('confidence', 0):
                result = locationiq_result
        
        return result
    
    def _geocode_tomtom(self, full_address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """Geocode using TomTom API"""
        url = f"https://api.tomtom.com/search/2/geocode/{full_address}.json"
        params = {
            'key': self.tomtom_key,
            'limit': 1
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('results'):
                    return {
                        'valid': False,
                        'confidence': 30,
                        'source': 'TomTom Geocoding API',
                        'error': 'No results found',
                        'verified_data': None
                    }
                
                result = data['results'][0]
                position = result.get('position', {})
                address_data = result.get('address', {})
                
                # Extract formatted address
                formatted_address = address_data.get('freeformAddress', full_address)
                returned_city = address_data.get('municipality', '')
                returned_state = address_data.get('countrySubdivision', '')
                returned_zip = address_data.get('postalCode', '')
                
                # Calculate match quality
                match_quality = self._calculate_address_match(
                    city, state, zip_code,
                    returned_city, returned_state, returned_zip
                )
                
                confidence = match_quality['confidence']
                
                verified_data = {
                    'formatted_address': formatted_address,
                    'latitude': position.get('lat'),
                    'longitude': position.get('lon'),
                    'city': returned_city,
                    'state': returned_state,
                    'zip_code': returned_zip,
                    'match_quality': match_quality['quality']
                }
                
                return {
                    'valid': True,
                    'confidence': confidence,
                    'source': 'TomTom Geocoding API',
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
                        'confidence': 20,
                        'source': 'TomTom Geocoding API',
                        'error': f'API request failed: {str(e)}',
                        'verified_data': None
                    }
            except Exception as e:
                return {
                    'valid': False,
                    'confidence': 20,
                    'source': 'TomTom Geocoding API',
                    'error': f'Unexpected error: {str(e)}',
                    'verified_data': None
                }
        
        return {
            'valid': False,
            'confidence': 20,
            'source': 'TomTom Geocoding API',
            'error': 'Max retry attempts exceeded',
            'verified_data': None
        }
    
    def _geocode_locationiq(self, full_address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """Geocode using LocationIQ API (backup)"""
        url = "https://us1.locationiq.com/v1/search.php"
        params = {
            'key': self.locationiq_key,
            'q': full_address,
            'format': 'json',
            'limit': 1
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                if not data or (isinstance(data, list) and len(data) == 0):
                    return {
                        'valid': False,
                        'confidence': 30,
                        'source': 'LocationIQ API',
                        'error': 'No results found',
                        'verified_data': None
                    }
                
                result = data[0] if isinstance(data, list) else data
                
                formatted_address = result.get('display_name', full_address)
                returned_city = result.get('address', {}).get('city', '') or result.get('address', {}).get('town', '')
                returned_state = result.get('address', {}).get('state', '')
                returned_zip = result.get('address', {}).get('postcode', '')
                
                # Calculate match quality
                match_quality = self._calculate_address_match(
                    city, state, zip_code,
                    returned_city, returned_state, returned_zip
                )
                
                confidence = match_quality['confidence']
                
                verified_data = {
                    'formatted_address': formatted_address,
                    'latitude': float(result.get('lat', 0)),
                    'longitude': float(result.get('lon', 0)),
                    'city': returned_city,
                    'state': returned_state,
                    'zip_code': returned_zip,
                    'match_quality': match_quality['quality']
                }
                
                return {
                    'valid': True,
                    'confidence': confidence,
                    'source': 'LocationIQ API',
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
                        'confidence': 20,
                        'source': 'LocationIQ API',
                        'error': f'API request failed: {str(e)}',
                        'verified_data': None
                    }
            except Exception as e:
                return {
                    'valid': False,
                    'confidence': 20,
                    'source': 'LocationIQ API',
                    'error': f'Unexpected error: {str(e)}',
                    'verified_data': None
                }
        
        return {
            'valid': False,
            'confidence': 20,
            'source': 'LocationIQ API',
            'error': 'Max retry attempts exceeded',
            'verified_data': None
        }
    
    def _calculate_address_match(self, input_city: str, input_state: str, input_zip: str,
                                 returned_city: str, returned_state: str, returned_zip: str) -> Dict[str, Any]:
        """Calculate address match quality"""
        input_city = input_city.lower().strip()
        input_state = input_state.lower().strip()
        input_zip = input_zip.strip()
        
        returned_city = returned_city.lower().strip()
        returned_state = returned_state.lower().strip()
        returned_zip = returned_zip.strip()
        
        # Perfect match
        if (input_city == returned_city and 
            input_state == returned_state and 
            input_zip == returned_zip):
            return {'quality': 'exact', 'confidence': 95}
        
        # Close match (city and state match, zip might differ)
        city_match = SequenceMatcher(None, input_city, returned_city).ratio()
        state_match = input_state == returned_state
        zip_match = input_zip == returned_zip
        
        if city_match > 0.8 and state_match:
            if zip_match:
                return {'quality': 'close', 'confidence': 85}
            else:
                return {'quality': 'partial', 'confidence': 60}
        
        # Partial match
        if city_match > 0.6 and state_match:
            return {'quality': 'partial', 'confidence': 60}
        
        # No match
        return {'quality': 'none', 'confidence': 30}

