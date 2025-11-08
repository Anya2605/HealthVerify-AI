"""
Report generation utilities for PDF and Excel exports
"""
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import os


class ReportGenerator:
    """Utility for generating validation reports"""
    
    @staticmethod
    def generate_excel_report(validation_results: List[Dict[str, Any]], output_path: str):
        """Generate Excel report from validation results"""
        try:
            # Prepare data for Excel
            rows = []
            for result in validation_results:
                validations = result.get('validations', {})
                row = {
                    'Provider ID': result.get('provider_id', ''),
                    'NPI': result.get('npi', ''),
                    'Validation Status': result.get('validation_status', ''),
                    'Overall Confidence': result.get('overall_confidence', 0),
                    'NPI Valid': validations.get('npi', {}).get('valid', False),
                    'NPI Confidence': validations.get('npi', {}).get('confidence', 0),
                    'Address Valid': validations.get('address', {}).get('valid', False),
                    'Address Confidence': validations.get('address', {}).get('confidence', 0),
                    'Phone Valid': validations.get('phone', {}).get('valid', False),
                    'Phone Confidence': validations.get('phone', {}).get('confidence', 0),
                    'Website Valid': validations.get('website', {}).get('valid', False),
                    'Website Confidence': validations.get('website', {}).get('confidence', 0),
                    'Flag Count': len(result.get('flags', [])),
                    'Critical Flags': len([f for f in result.get('flags', []) if f.get('flag_type') == 'CRITICAL']),
                    'Warning Flags': len([f for f in result.get('flags', []) if f.get('flag_type') == 'WARNING']),
                    'Validation Timestamp': result.get('validation_timestamp', ''),
                    'Duration (seconds)': result.get('validation_duration_seconds', 0)
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # Write to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Validation Results', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Validation Results']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
            
            return True
        except Exception as e:
            raise Exception(f"Error generating Excel report: {str(e)}")
    
    @staticmethod
    def generate_summary_report(validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from validation results"""
        total = len(validation_results)
        if total == 0:
            return {}
        
        validated = sum(1 for r in validation_results if r.get('validation_status') == 'VALIDATED')
        partial = sum(1 for r in validation_results if r.get('validation_status') == 'PARTIAL')
        flagged = sum(1 for r in validation_results if r.get('validation_status') == 'FLAGGED')
        
        avg_confidence = sum(r.get('overall_confidence', 0) for r in validation_results) / total
        
        total_flags = sum(len(r.get('flags', [])) for r in validation_results)
        critical_flags = sum(len([f for f in r.get('flags', []) if f.get('flag_type') == 'CRITICAL']) 
                            for r in validation_results)
        warning_flags = sum(len([f for f in r.get('flags', []) if f.get('flag_type') == 'WARNING']) 
                            for r in validation_results)
        
        npi_valid_count = sum(1 for r in validation_results 
                             if r.get('validations', {}).get('npi', {}).get('valid', False))
        address_valid_count = sum(1 for r in validation_results 
                                 if r.get('validations', {}).get('address', {}).get('valid', False))
        phone_valid_count = sum(1 for r in validation_results 
                              if r.get('validations', {}).get('phone', {}).get('valid', False))
        
        return {
            'total_providers': total,
            'validated': validated,
            'partial': partial,
            'flagged': flagged,
            'validation_rate': round((validated / total) * 100, 2) if total > 0 else 0,
            'average_confidence': round(avg_confidence, 2),
            'total_flags': total_flags,
            'critical_flags': critical_flags,
            'warning_flags': warning_flags,
            'npi_validation_rate': round((npi_valid_count / total) * 100, 2) if total > 0 else 0,
            'address_validation_rate': round((address_valid_count / total) * 100, 2) if total > 0 else 0,
            'phone_validation_rate': round((phone_valid_count / total) * 100, 2) if total > 0 else 0
        }

