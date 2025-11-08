"""
Web Scraping Service for provider website verification
"""
import requests
from bs4 import BeautifulSoup
import time
import sys
import os
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class WebScraper:
    """Service for web scraping and provider website verification"""
    
    def __init__(self):
        self.timeout = Config.API_TIMEOUT
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_provider_website(self, full_name: str, city: str, state: str) -> Optional[str]:
        """
        Search for provider website (simplified - in production would use Google Search API)
        
        Args:
            full_name: Provider full name
            city: City name
            state: State code
            
        Returns:
            Website URL if found, None otherwise
        """
        # This is a simplified version
        # In production, you would use Google Custom Search API or similar
        # For now, we'll try to construct a potential website URL
        name_slug = full_name.lower().replace(' ', '').replace('.', '').replace('dr', '')
        potential_urls = [
            f"https://www.{name_slug}.com",
            f"https://{name_slug}.com",
            f"https://www.{name_slug}md.com"
        ]
        
        for url in potential_urls:
            if self._check_url_exists(url):
                return url
        
        return None
    
    def _check_url_exists(self, url: str) -> bool:
        """Check if URL exists and is accessible"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def extract_contact_info(self, url: str) -> Dict[str, Any]:
        """
        Extract contact information from provider website
        
        Args:
            url: Website URL
            
        Returns:
            Dictionary with extracted contact information
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract phone numbers
            phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
            phones = []
            for text in soup.stripped_strings:
                matches = phone_pattern.findall(text)
                phones.extend(matches)
            
            # Extract addresses (look for common address patterns)
            addresses = []
            address_keywords = ['address', 'location', 'office', 'clinic']
            for element in soup.find_all(['p', 'div', 'span']):
                text = element.get_text().lower()
                if any(keyword in text for keyword in address_keywords):
                    addresses.append(element.get_text().strip())
            
            # Extract email
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            emails = []
            for text in soup.stripped_strings:
                matches = email_pattern.findall(text)
                emails.extend(matches)
            
            # Try to find last updated date
            last_updated = None
            copyright_text = soup.find(string=re.compile(r'©|Copyright|©'))
            if copyright_text:
                year_match = re.search(r'20\d{2}', copyright_text)
                if year_match:
                    last_updated = year_match.group()
            
            return {
                'url': url,
                'phone_on_site': phones[0] if phones else None,
                'address_on_site': addresses[0] if addresses else None,
                'email_on_site': emails[0] if emails else None,
                'last_updated': last_updated,
                'phones_found': phones,
                'addresses_found': addresses
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'phone_on_site': None,
                'address_on_site': None,
                'email_on_site': None,
                'last_updated': None
            }
    
    def verify_provider_web_presence(self, full_name: str, city: str, state: str,
                                     input_phone: str = None, input_address: str = None) -> Dict[str, Any]:
        """
        Verify provider web presence and compare with input data
        
        Args:
            full_name: Provider full name
            city: City name
            state: State code
            input_phone: Input phone number for comparison
            input_address: Input address for comparison
            
        Returns:
            Dictionary with verification results
        """
        website_url = self.search_provider_website(full_name, city, state)
        
        if not website_url:
            return {
                'valid': False,
                'confidence': 50,
                'source': 'Web Scraping',
                'verified_data': {
                    'url': None,
                    'phone_on_site': None,
                    'address_on_site': None,
                    'last_updated': None
                },
                'error': 'No website found'
            }
        
        contact_info = self.extract_contact_info(website_url)
        
        if contact_info.get('error'):
            return {
                'valid': False,
                'confidence': 50,
                'source': 'Web Scraping',
                'verified_data': contact_info,
                'error': contact_info.get('error')
            }
        
        # Compare with input data
        confidence = 50  # Base confidence
        matches = []
        
        # Compare phone
        if input_phone and contact_info.get('phone_on_site'):
            input_clean = re.sub(r'\D', '', input_phone)
            site_clean = re.sub(r'\D', '', contact_info['phone_on_site'])
            if input_clean[-10:] == site_clean[-10:]:
                confidence = 75
                matches.append('phone')
        
        # Compare address (basic)
        if input_address and contact_info.get('address_on_site'):
            input_lower = input_address.lower()
            site_lower = contact_info['address_on_site'].lower()
            similarity = SequenceMatcher(None, input_lower, site_lower).ratio()
            if similarity > 0.7:
                confidence = max(confidence, 75)
                matches.append('address')
        
        # If multiple matches, increase confidence
        if len(matches) >= 2:
            confidence = 75
        
        # If website found but no matches, lower confidence
        if not matches and contact_info.get('phone_on_site') or contact_info.get('address_on_site'):
            confidence = 60
        
        return {
            'valid': True,
            'confidence': confidence,
            'source': 'Web Scraping',
            'verified_data': contact_info,
            'matches': matches,
            'error': None
        }

