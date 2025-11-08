"""
Agent 3: Quality Assurance Agent
Performs quality assurance and scoring
"""
import sys
import os
from typing import Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.confidence_scorer import ConfidenceScorer


class QualityAgent:
    """Agent for quality assurance and scoring"""
    
    def __init__(self):
        self.confidence_scorer = ConfidenceScorer()
    
    def assess_quality(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of validation result"""
        quality_score = validation_result.get('overall_confidence', 0)
        flags = validation_result.get('flags', [])
        
        critical_count = len([f for f in flags if f.get('flag_type') == 'CRITICAL'])
        warning_count = len([f for f in flags if f.get('flag_type') == 'WARNING'])
        
        quality_level = 'HIGH'
        if quality_score < 60 or critical_count > 0:
            quality_level = 'LOW'
        elif quality_score < 80 or warning_count > 2:
            quality_level = 'MEDIUM'
        
        return {
            'quality_score': quality_score,
            'quality_level': quality_level,
            'critical_issues': critical_count,
            'warnings': warning_count,
            'total_flags': len(flags)
        }

