"""
Flask main application for HealthVerify AI Provider Validation System
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import threading

import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config import Config
from utils.database import Database
from utils.file_processor import FileProcessor
from agents.data_validation_agent import DataValidationAgent
from agents.enrichment_agent import EnrichmentAgent
from agents.quality_agent import QualityAgent
from agents.directory_agent import DirectoryAgent
from utils.report_generator import ReportGenerator

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
db = Database()
file_processor = FileProcessor()
validation_agent = DataValidationAgent()
enrichment_agent = EnrichmentAgent()
quality_agent = QualityAgent()
directory_agent = DirectoryAgent()
report_generator = ReportGenerator()

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(project_root, 'data', 'uploads')
RESULTS_FOLDER = os.path.join(project_root, 'data', 'validation_results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard with KPIs"""
    stats = directory_agent.get_directory_stats()
    
    # Get recent validation results for summary
    all_providers = db.get_all_providers()
    recent_results = []
    for provider in all_providers[:10]:  # Last 10 providers
        result = db.get_validation_result(provider['provider_id'])
        if result:
            recent_results.append(result)
    
    # Calculate KPIs
    total_providers = len(all_providers)
    validated_count = sum(1 for r in recent_results if r.get('validation_status') == 'VALIDATED')
    avg_confidence = sum(r.get('overall_confidence', 0) for r in recent_results) / len(recent_results) if recent_results else 0
    
    kpis = {
        'total_providers': total_providers,
        'validated': validated_count,
        'average_confidence': round(avg_confidence, 2),
        'unresolved_flags': stats.get('unresolved_flags', 0),
        'critical_flags': stats.get('critical_flags', 0)
    }
    
    return render_template('dashboard.html', kpis=kpis, recent_results=recent_results[:5])


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """File upload page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        # Validate extension against allowed list
        ext = file_processor.get_file_extension(file.filename)
        if ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'error': f'Invalid or unsupported file type: .{ext}'}), 400

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process file using FileProcessor (supports CSV, Excel, PDF, images, JSON)
        try:
            df, metadata = file_processor.process_file(filepath)
            # Convert DataFrame rows to provider dicts
            providers = df.to_dict(orient='records') if not df.empty else []

            # Create job
            job_id = str(uuid.uuid4())
            job = {
                'job_id': job_id,
                'filename': filename,
                'total_providers': len(providers),
                'status': 'PENDING',
                'file_metadata': metadata
            }
            db.create_job(job)

            # Store providers in database
            for provider in providers:
                db.insert_provider(provider)

            # Start processing in background
            thread = threading.Thread(target=process_providers_background, args=(job_id, providers))
            thread.daemon = True
            thread.start()

            return jsonify({
                'success': True,
                'job_id': job_id,
                'total_providers': len(providers),
                'redirect': url_for('processing', job_id=job_id)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('upload.html')


@app.route('/processing/<job_id>')
def processing(job_id):
    """Real-time processing view"""
    job = db.get_job(job_id)
    if not job:
        return redirect(url_for('upload'))
    
    return render_template('processing.html', job_id=job_id, job=job)


@app.route('/api/processing/<job_id>')
def api_processing_status(job_id):
    """API endpoint for processing status"""
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)


@app.route('/results/<job_id>')
def results(job_id):
    """Results dashboard"""
    job = db.get_job(job_id)
    if not job:
        return redirect(url_for('dashboard'))
    
    # Get all providers for this job (simplified - in production would track by job)
    all_providers = db.get_all_providers()
    validation_results = []
    
    for provider in all_providers:
        result = db.get_validation_result(provider['provider_id'])
        if result:
            validation_results.append(result)
    
    # Generate summary
    summary = report_generator.generate_summary_report(validation_results)
    
    return render_template('results.html', job_id=job_id, job=job, 
                         results=validation_results, summary=summary)


@app.route('/flagged')
def flagged():
    """Flagged items review page"""
    flags = db.get_flags(resolved=False)
    
    # Group flags by provider
    flags_by_provider = {}
    for flag in flags:
        provider_id = flag['provider_id']
        if provider_id not in flags_by_provider:
            flags_by_provider[provider_id] = {
                'provider': db.get_provider(provider_id),
                'flags': []
            }
        flags_by_provider[provider_id]['flags'].append(flag)
    
    return render_template('flagged.html', flags_by_provider=flags_by_provider)


@app.route('/export/<job_id>')
def export(job_id):
    """Export reports page"""
    job = db.get_job(job_id)
    if not job:
        return redirect(url_for('dashboard'))
    
    # Get validation results
    all_providers = db.get_all_providers()
    validation_results = []
    
    for provider in all_providers:
        result = db.get_validation_result(provider['provider_id'])
        if result:
            validation_results.append(result)
    
    return render_template('export.html', job_id=job_id, job=job, 
                         total_results=len(validation_results))


@app.route('/api/export/<job_id>')
def api_export(job_id):
    """API endpoint for exporting reports"""
    try:
        # Get validation results
        all_providers = db.get_all_providers()
        validation_results = []
        
        for provider in all_providers:
            result = db.get_validation_result(provider['provider_id'])
            if result:
                validation_results.append(result)
        
        # Generate Excel report
        output_filename = f"validation_report_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(RESULTS_FOLDER, output_filename)
        
        report_generator.generate_excel_report(validation_results, output_path)
        
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/validate/<provider_id>')
def api_validate_provider(provider_id):
    """API endpoint for validating a single provider"""
    provider = db.get_provider(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404
    
    # Validate provider
    result = validation_agent.validate_provider(provider)
    
    # Store result
    db.insert_validation_result(result)
    
    # Store flags
    for flag in result.get('flags', []):
        db.insert_flag(flag)
    
    return jsonify(result)


def process_providers_background(job_id, providers):
    """Background processing function"""
    try:
        db.update_job(job_id, {
            'status': 'PROCESSING',
            'started_at': datetime.now().isoformat()
        })
        
        success_count = 0
        error_count = 0
        
        for i, provider in enumerate(providers):
            try:
                # Validate provider
                result = validation_agent.validate_provider(provider)
                
                # Store result
                db.insert_validation_result(result)
                
                # Store flags
                for flag in result.get('flags', []):
                    db.insert_flag(flag)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error processing provider {provider.get('provider_id')}: {e}")
            
            # Update progress
            db.update_job(job_id, {
                'processed_count': i + 1,
                'success_count': success_count,
                'error_count': error_count
            })
        
        # Mark as completed
        db.update_job(job_id, {
            'status': 'COMPLETED',
            'completed_at': datetime.now().isoformat(),
            'processed_count': len(providers),
            'success_count': success_count,
            'error_count': error_count
        })
        
    except Exception as e:
        db.update_job(job_id, {
            'status': 'FAILED',
            'error_message': str(e),
            'completed_at': datetime.now().isoformat()
        })


if __name__ == '__main__':
    # For a stable local run during debugging sessions, disable Flask auto-reloader
    # to avoid repeated import-time side effects. In production, use a WSGI server.
    app.run(debug=False, host='0.0.0.0', port=5000)

