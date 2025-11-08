"""
Confidence scoring utilities
"""
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ml_models import MLModels


class ConfidenceScorer:
    """Utility for calculating confidence scores"""
    
    def __init__(self):
        self.ml_models = MLModels()
    
    def score_validation_result(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate confidence scores for validation result
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Updated validation result with confidence scores
        """
        validations = validation_result.get('validations', {})
        
        # Calculate overall confidence
        overall_confidence = self.ml_models.calculate_overall_confidence(validations)
        validation_result['overall_confidence'] = overall_confidence
        
        # Detect anomalies
        anomalies = self.ml_models.detect_anomalies(validation_result)
        if anomalies:
            validation_result['anomalies'] = anomalies
        
        # Generate recommendations
        recommendations = self.ml_models.generate_recommendations(validation_result)
        validation_result['recommendations'] = recommendations
        
        # Determine validation status
        if overall_confidence >= 80 and not validation_result.get('flags'):
            validation_result['validation_status'] = 'VALIDATED'
        elif overall_confidence >= 60:
            validation_result['validation_status'] = 'PARTIAL'
        else:
            validation_result['validation_status'] = 'FLAGGED'
        
        return validation_result

