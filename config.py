"""
Configuration file for HealthVerify AI Provider Validation System
Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')
    
    # API Keys - AI/ML
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # API Keys - Data Validation
    TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY', '')
    NUMVERIFY_API_KEY = os.getenv('NUMVERIFY_API_KEY', '')
    LOCATIONIQ_API_KEY = os.getenv('LOCATIONIQ_API_KEY', '')
    OCRSPACE_API_KEY = os.getenv('OCRSPACE_API_KEY', '')
    
    # Free Public APIs
    NPI_REGISTRY_API_URL = os.getenv('NPI_REGISTRY_API_URL', 'https://npiregistry.cms.hhs.gov/api/')
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', '2'))
    
    # Processing Configuration
    MAX_CONCURRENT_VALIDATIONS = int(os.getenv('MAX_CONCURRENT_VALIDATIONS', '10'))
    CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL_HOURS', '24'))
    
    # File Upload Configuration
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf'}
    
    # Confidence Scoring Weights
    NPI_WEIGHT = 0.40
    ADDRESS_WEIGHT = 0.30
    PHONE_WEIGHT = 0.20
    WEB_WEIGHT = 0.10

