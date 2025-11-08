"""
Database utilities for SQLite operations
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class Database:
    """SQLite database operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Providers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    provider_id TEXT PRIMARY KEY,
                    npi TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    specialty TEXT,
                    practice_address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    phone TEXT,
                    email TEXT,
                    website TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Validation results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT,
                    validation_timestamp TEXT,
                    validation_duration_seconds REAL,
                    validations TEXT,
                    overall_confidence REAL,
                    validation_status TEXT,
                    flags TEXT,
                    recommendations TEXT,
                    sources_used TEXT,
                    FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
                )
            ''')
            
            # Flags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT,
                    flag_type TEXT,
                    severity TEXT,
                    field TEXT,
                    message TEXT,
                    details TEXT,
                    created_at TEXT,
                    resolved INTEGER DEFAULT 0,
                    resolved_at TEXT,
                    FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
                )
            ''')
            
            # Processing jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_jobs (
                    job_id TEXT PRIMARY KEY,
                    filename TEXT,
                    total_providers INTEGER,
                    status TEXT,
                    processed_count INTEGER,
                    success_count INTEGER,
                    error_count INTEGER,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
    
    def insert_provider(self, provider: Dict[str, Any]) -> bool:
        """Insert or update provider"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO providers 
                    (provider_id, npi, first_name, last_name, full_name, specialty,
                     practice_address, city, state, zip_code, phone, email, website,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    provider['provider_id'],
                    provider.get('npi', ''),
                    provider.get('first_name', ''),
                    provider.get('last_name', ''),
                    provider.get('full_name', ''),
                    provider.get('specialty', ''),
                    provider.get('practice_address', ''),
                    provider.get('city', ''),
                    provider.get('state', ''),
                    provider.get('zip_code', ''),
                    provider.get('phone', ''),
                    provider.get('email', ''),
                    provider.get('website', ''),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                return True
        except Exception as e:
            print(f"Error inserting provider: {e}")
            return False
    
    def insert_validation_result(self, result: Dict[str, Any]) -> bool:
        """Insert validation result"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO validation_results
                    (provider_id, validation_timestamp, validation_duration_seconds,
                     validations, overall_confidence, validation_status, flags,
                     recommendations, sources_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['provider_id'],
                    result['validation_timestamp'],
                    result['validation_duration_seconds'],
                    json.dumps(result['validations']),
                    result['overall_confidence'],
                    result['validation_status'],
                    json.dumps(result['flags']),
                    json.dumps(result['recommendations']),
                    json.dumps(result['sources_used'])
                ))
                return True
        except Exception as e:
            print(f"Error inserting validation result: {e}")
            return False
    
    def insert_flag(self, flag: Dict[str, Any]) -> bool:
        """Insert flag"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO flags
                    (provider_id, flag_type, severity, field, message, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    flag['provider_id'],
                    flag['flag_type'],
                    flag['severity'],
                    flag['field'],
                    flag['message'],
                    json.dumps(flag.get('details', {})),
                    flag.get('created_at', datetime.now().isoformat())
                ))
                return True
        except Exception as e:
            print(f"Error inserting flag: {e}")
            return False
    
    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get provider by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM providers WHERE provider_id = ?', (provider_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_validation_result(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get latest validation result for provider"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM validation_results 
                WHERE provider_id = ? 
                ORDER BY validation_timestamp DESC 
                LIMIT 1
            ''', (provider_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['validations'] = json.loads(result['validations'])
                result['flags'] = json.loads(result['flags'])
                result['recommendations'] = json.loads(result['recommendations'])
                result['sources_used'] = json.loads(result['sources_used'])
                return result
            return None
    
    def get_flags(self, provider_id: str = None, flag_type: str = None, resolved: bool = None) -> List[Dict[str, Any]]:
        """Get flags with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM flags WHERE 1=1'
            params = []
            
            if provider_id:
                query += ' AND provider_id = ?'
                params.append(provider_id)
            
            if flag_type:
                query += ' AND flag_type = ?'
                params.append(flag_type)
            
            if resolved is not None:
                query += ' AND resolved = ?'
                params.append(1 if resolved else 0)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            flags = []
            for row in rows:
                flag = dict(row)
                flag['details'] = json.loads(flag['details']) if flag['details'] else {}
                flags.append(flag)
            return flags
    
    def create_job(self, job: Dict[str, Any]) -> bool:
        """Create processing job"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO processing_jobs
                    (job_id, filename, total_providers, status, processed_count,
                     success_count, error_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job['job_id'],
                    job['filename'],
                    job['total_providers'],
                    job.get('status', 'PENDING'),
                    job.get('processed_count', 0),
                    job.get('success_count', 0),
                    job.get('error_count', 0),
                    job.get('created_at', datetime.now().isoformat())
                ))
                return True
        except Exception as e:
            print(f"Error creating job: {e}")
            return False
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update processing job"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                set_clauses = []
                params = []
                
                for key, value in updates.items():
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
                
                params.append(job_id)
                query = f"UPDATE processing_jobs SET {', '.join(set_clauses)} WHERE job_id = ?"
                cursor.execute(query, params)
                return True
        except Exception as e:
            print(f"Error updating job: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM processing_jobs WHERE job_id = ?', (job_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        """Get all providers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM providers ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

