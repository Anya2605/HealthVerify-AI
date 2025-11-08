"""
Database schema definitions for HealthVerify AI Provider Validation System
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json

class Provider:
    """Provider data model"""
    
    def __init__(self, provider_id: str, npi: str, first_name: str, last_name: str,
                 full_name: str, specialty: str, practice_address: str, city: str,
                 state: str, zip_code: str, phone: str, email: Optional[str] = None,
                 website: Optional[str] = None):
        self.provider_id = provider_id
        self.npi = npi
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name
        self.specialty = specialty
        self.practice_address = practice_address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = phone
        self.email = email
        self.website = website
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provider to dictionary"""
        return {
            'provider_id': self.provider_id,
            'npi': self.npi,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'specialty': self.specialty,
            'practice_address': self.practice_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Provider':
        """Create provider from dictionary"""
        return cls(
            provider_id=data.get('provider_id', ''),
            npi=data.get('npi', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            full_name=data.get('full_name', ''),
            specialty=data.get('specialty', ''),
            practice_address=data.get('practice_address', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            zip_code=data.get('zip_code', ''),
            phone=data.get('phone', ''),
            email=data.get('email'),
            website=data.get('website')
        )


class ValidationResult:
    """Validation result model"""
    
    def __init__(self, provider_id: str, validation_timestamp: datetime,
                 validation_duration_seconds: float, validations: Dict[str, Any],
                 overall_confidence: float, validation_status: str,
                 flags: list, recommendations: list, sources_used: list):
        self.provider_id = provider_id
        self.validation_timestamp = validation_timestamp
        self.validation_duration_seconds = validation_duration_seconds
        self.validations = validations
        self.overall_confidence = overall_confidence
        self.validation_status = validation_status
        self.flags = flags
        self.recommendations = recommendations
        self.sources_used = sources_used
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary"""
        return {
            'provider_id': self.provider_id,
            'validation_timestamp': self.validation_timestamp.isoformat(),
            'validation_duration_seconds': self.validation_duration_seconds,
            'validations': self.validations,
            'overall_confidence': self.overall_confidence,
            'validation_status': self.validation_status,
            'flags': self.flags,
            'recommendations': self.recommendations,
            'sources_used': self.sources_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """Create validation result from dictionary"""
        return cls(
            provider_id=data.get('provider_id', ''),
            validation_timestamp=datetime.fromisoformat(data.get('validation_timestamp', datetime.now().isoformat())),
            validation_duration_seconds=data.get('validation_duration_seconds', 0.0),
            validations=data.get('validations', {}),
            overall_confidence=data.get('overall_confidence', 0.0),
            validation_status=data.get('validation_status', 'PENDING'),
            flags=data.get('flags', []),
            recommendations=data.get('recommendations', []),
            sources_used=data.get('sources_used', [])
        )


class Flag:
    """Flag model for validation issues"""
    
    def __init__(self, provider_id: str, flag_type: str, severity: str,
                 field: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.provider_id = provider_id
        self.flag_type = flag_type  # CRITICAL, WARNING, INFO
        self.severity = severity  # high, medium, low
        self.field = field
        self.message = message
        self.details = details or {}
        self.created_at = datetime.now()
        self.resolved = False
        self.resolved_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flag to dictionary"""
        return {
            'provider_id': self.provider_id,
            'flag_type': self.flag_type,
            'severity': self.severity,
            'field': self.field,
            'message': self.message,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class ProcessingJob:
    """Processing job model"""
    
    def __init__(self, job_id: str, filename: str, total_providers: int,
                 status: str = 'PENDING', processed_count: int = 0,
                 success_count: int = 0, error_count: int = 0):
        self.job_id = job_id
        self.filename = filename
        self.total_providers = total_providers
        self.status = status  # PENDING, PROCESSING, COMPLETED, FAILED
        self.processed_count = processed_count
        self.success_count = success_count
        self.error_count = error_count
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'job_id': self.job_id,
            'filename': self.filename,
            'total_providers': self.total_providers,
            'status': self.status,
            'processed_count': self.processed_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }

