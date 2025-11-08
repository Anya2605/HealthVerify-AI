"""
ML Models for confidence scoring and anomaly detection
"""
import numpy as np
import sys
import os
from typing import Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class MLModels:
    """Machine learning models for confidence scoring"""
    
    def __init__(self):
        self.npi_weight = Config.NPI_WEIGHT
        self.address_weight = Config.ADDRESS_WEIGHT
        self.phone_weight = Config.PHONE_WEIGHT
        self.web_weight = Config.WEB_WEIGHT
    
    def calculate_overall_confidence(self, validations: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score from individual validations
        
        Args:
            validations: Dictionary with validation results for each field
            
        Returns:
            Overall confidence score (0-100)
        """
        npi_conf = validations.get('npi', {}).get('confidence', 0)
        address_conf = validations.get('address', {}).get('confidence', 0)
        phone_conf = validations.get('phone', {}).get('confidence', 0)
        web_conf = validations.get('website', {}).get('confidence', 0)
        
        # Weighted average
        overall = (
            npi_conf * self.npi_weight +
            address_conf * self.address_weight +
            phone_conf * self.phone_weight +
            web_conf * self.web_weight
        )
        
        # Apply penalties for inconsistencies
        penalties = self._calculate_penalties(validations)
        overall = max(0, overall - penalties)
        
        return round(overall, 2)
    
    def _calculate_penalties(self, validations: Dict[str, Any]) -> float:
        """Calculate penalty points for inconsistencies"""
        penalty = 0.0
        
        # Check for conflicts between sources
        npi_valid = validations.get('npi', {}).get('valid', False)
        address_valid = validations.get('address', {}).get('valid', False)
        phone_valid = validations.get('phone', {}).get('valid', False)
        
        # If NPI is invalid but others are valid, penalty
        if not npi_valid and (address_valid or phone_valid):
            penalty += 10
        
        # If multiple sources conflict
        valid_count = sum([npi_valid, address_valid, phone_valid])
        if valid_count == 1:  # Only one source valid
            penalty += 5
        
        # Check for name mismatches
        npi_matches = validations.get('npi', {}).get('matches_input', True)
        if not npi_matches:
            penalty += 15
        
        return penalty
    
    def detect_anomalies(self, validation_result: Dict[str, Any]) -> List[str]:
        """
        Detect anomalies in validation results
        
        Args:
            validation_result: Complete validation result
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        validations = validation_result.get('validations', {})
        overall_confidence = validation_result.get('overall_confidence', 0)
        
        # Low confidence but all sources valid
        if overall_confidence < 60:
            all_valid = all(v.get('valid', False) for v in validations.values())
            if all_valid:
                anomalies.append("Low overall confidence despite all sources being valid")
        
        # High confidence but NPI invalid
        if overall_confidence > 80:
            npi_valid = validations.get('npi', {}).get('valid', False)
            if not npi_valid:
                anomalies.append("High confidence but NPI validation failed")
        
        # Inconsistent address data
        address_conf = validations.get('address', {}).get('confidence', 0)
        if 40 < address_conf < 70:
            anomalies.append("Address validation shows partial match - may need review")
        
        # Phone disconnected but high confidence
        phone_data = validations.get('phone', {}).get('verified_data', {})
        if phone_data.get('line_type') == 'unknown' and overall_confidence > 70:
            anomalies.append("Phone number may be disconnected despite high confidence")
        
        return anomalies
    
    def generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on validation results
        
        Args:
            validation_result: Complete validation result
            
        Returns:
            List of recommendations
        """
        recommendations = []
        validations = validation_result.get('validations', {})
        overall_confidence = validation_result.get('overall_confidence', 0)
        flags = validation_result.get('flags', [])
        
        # High confidence - no action needed
        if overall_confidence >= 80 and not flags:
            recommendations.append("Provider successfully validated across all sources")
            recommendations.append("High confidence score - no manual review needed")
            return recommendations
        
        # Check individual validations
        npi_valid = validations.get('npi', {}).get('valid', False)
        if not npi_valid:
            recommendations.append("CRITICAL: NPI not found in registry - verify NPI number")
        
        address_conf = validations.get('address', {}).get('confidence', 0)
        if address_conf < 60:
            recommendations.append("WARNING: Address validation shows low confidence - verify address")
        
        phone_conf = validations.get('phone', {}).get('confidence', 0)
        if phone_conf < 60:
            recommendations.append("WARNING: Phone number validation failed - verify phone number")
        
        # Check for flags
        critical_flags = [f for f in flags if f.get('flag_type') == 'CRITICAL']
        if critical_flags:
            recommendations.append(f"CRITICAL: {len(critical_flags)} critical issue(s) require immediate attention")
        
        warning_flags = [f for f in flags if f.get('flag_type') == 'WARNING']
        if warning_flags:
            recommendations.append(f"WARNING: {len(warning_flags)} warning(s) need review")
        
        if not recommendations:
            recommendations.append("Provider data validated with minor issues")
        
        return recommendations

