"""
Agent 4: Directory Management Agent
Handles reporting and directory management
"""
import sys
import os
from typing import Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.report_generator import ReportGenerator
from utils.database import Database


class DirectoryAgent:
    """Agent for reporting and directory management"""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.database = Database()
    
    def generate_report(self, validation_results: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
        """Generate Excel report from validation results"""
        try:
            self.report_generator.generate_excel_report(validation_results, output_path)
            summary = self.report_generator.generate_summary_report(validation_results)
            return {
                'success': True,
                'output_path': output_path,
                'summary': summary
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """Get directory statistics"""
        providers = self.database.get_all_providers()
        flags = self.database.get_flags(resolved=False)
        
        return {
            'total_providers': len(providers),
            'unresolved_flags': len(flags),
            'critical_flags': len([f for f in flags if f.get('flag_type') == 'CRITICAL']),
            'warning_flags': len([f for f in flags if f.get('flag_type') == 'WARNING'])
        }

