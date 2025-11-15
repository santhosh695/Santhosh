import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.datastructures import FileStorage
from app.utils.decorators import authenticated_required
from app.utils.validators import validate_file_upload
from app.utils.helpers import (
    save_uploaded_file, delete_file, format_error_response,
    format_success_response, allowed_file, log_user_activity
)

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/evidence', methods=['POST'])
@login_required
@authenticated_required
def upload_evidence():
    """
    Upload evidence files for FIRs and complaints.
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return format_error_response("No file provided")

        file = request.files['file']
        if file.filename == '':
            return format_error_response("No file selected")

        # Validate file
        is_valid, error_message = validate_file_upload(file)
        if not is_valid:
            return format_error_response(error_message)

        # Save file
        file_path = save_uploaded_file(file)
        if not file_path:
            return format_error_response("Failed to save file")

        # Create relative path for API response
        relative_path = os.path.relpath(file_path, current_app.config.get('UPLOAD_FOLDER', 'uploads'))

        # Log activity
        log_user_activity(current_user.id, 'file_uploaded', {
            'filename': file.filename,
            'file_path': relative_path,
            'file_size': os.path.getsize(file_path)
        })

        return format_success_response(
            data={
                'filename': file.filename,
                'file_path': relative_path,
                'file_url': f'/api/upload/evidence/{relative_path}',
                'file_size': os.path.getsize(file_path)
            },
            message="File uploaded successfully",
            status_code=201
        )

    except Exception as e:
        return format_error_response("Failed to upload file")

@upload_bp.route('/evidence/<path:filename>', methods=['GET'])
@login_required
@authenticated_required
def download_evidence(filename):
    """
    Download evidence file.
    """
    try:
        # Security: Validate filename
        from app.utils.helpers import sanitize_text
        sanitized_filename = sanitize_text(filename)
        if not sanitized_filename or sanitized_filename != filename:
            return format_error_response("Invalid filename", 400)

        # Construct file path
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(upload_folder, filename)

        # Check if file exists
        if not os.path.exists(file_path):
            return format_error_response("File not found", 404)

        # Check if file is within upload folder (security check)
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            return format_error_response("Access denied", 403)

        # Log activity
        log_user_activity(current_user.id, 'file_downloaded', {
            'filename': filename
        })

        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )

    except Exception as e:
        return format_error_response("Failed to download file")

@upload_bp.route('/evidence/<path:filename>', methods=['DELETE'])
@login_required
@authenticated_required
def delete_evidence(filename):
    """
    Delete evidence file.
    """
    try:
        # Security: Validate filename
        from app.utils.helpers import sanitize_text
        sanitized_filename = sanitize_text(filename)
        if not sanitized_filename or sanitized_filename != filename:
            return format_error_response("Invalid filename", 400)

        # Construct file path
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(upload_folder, filename)

        # Check if file exists
        if not os.path.exists(file_path):
            return format_error_response("File not found", 404)

        # Check if file is within upload folder (security check)
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            return format_error_response("Access denied", 403)

        # Delete file
        success = delete_file(file_path)
        if not success:
            return format_error_response("Failed to delete file")

        # Log activity
        log_user_activity(current_user.id, 'file_deleted', {
            'filename': filename
        })

        return format_success_response(message="File deleted successfully")

    except Exception as e:
        return format_error_response("Failed to delete file")

@upload_bp.route('/evidence/<path:filename>/info', methods=['GET'])
@login_required
@authenticated_required
def get_file_info(filename):
    """
    Get information about an uploaded file.
    """
    try:
        # Security: Validate filename
        from app.utils.helpers import sanitize_text
        sanitized_filename = sanitize_text(filename)
        if not sanitized_filename or sanitized_filename != filename:
            return format_error_response("Invalid filename", 400)

        # Construct file path
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(upload_folder, filename)

        # Check if file exists
        if not os.path.exists(file_path):
            return format_error_response("File not found", 404)

        # Check if file is within upload folder (security check)
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            return format_error_response("Access denied", 403)

        # Get file information
        stat = os.stat(file_path)
        from datetime import datetime

        file_info = {
            'filename': filename,
            'file_url': f'/api/upload/evidence/{filename}',
            'file_size': stat.st_size,
            'file_size_formatted': format_file_size(stat.st_size),
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'file_extension': os.path.splitext(filename)[1].lower() if '.' in filename else 'unknown'
        }

        return format_success_response(data=file_info)

    except Exception as e:
        return format_error_response("Failed to retrieve file information")

@upload_bp.route('/batch', methods=['POST'])
@login_required
@authenticated_required
def upload_multiple_files():
    """
    Upload multiple files at once.
    """
    try:
        # Check if files are present
        if 'files' not in request.files:
            return format_error_response("No files provided")

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return format_error_response("No files selected")

        uploaded_files = []
        errors = []

        for file in files:
            if file.filename == '':
                continue

            # Validate file
            is_valid, error_message = validate_file_upload(file)
            if not is_valid:
                errors.append({
                    'filename': file.filename,
                    'error': error_message
                })
                continue

            # Save file
            file_path = save_uploaded_file(file)
            if not file_path:
                errors.append({
                    'filename': file.filename,
                    'error': "Failed to save file"
                })
                continue

            # Create relative path for API response
            relative_path = os.path.relpath(file_path, current_app.config.get('UPLOAD_FOLDER', 'uploads'))

            uploaded_files.append({
                'filename': file.filename,
                'file_path': relative_path,
                'file_url': f'/api/upload/evidence/{relative_path}',
                'file_size': os.path.getsize(file_path)
            })

        # Log activity
        log_user_activity(current_user.id, 'multiple_files_uploaded', {
            'total_files': len(files),
            'successful_uploads': len(uploaded_files),
            'failed_uploads': len(errors)
        })

        return format_success_response(
            data={
                'uploaded_files': uploaded_files,
                'errors': errors,
                'summary': {
                    'total_files': len(files),
                    'successful_uploads': len(uploaded_files),
                    'failed_uploads': len(errors)
                }
            },
            message=f"Uploaded {len(uploaded_files)} files successfully" +
                   (f" with {len(errors)} errors" if errors else "")
        )

    except Exception as e:
        return format_error_response("Failed to upload files")

@upload_bp.route('/cleanup', methods=['POST'])
@login_required
@authenticated_required
def cleanup_orphaned_files():
    """
    Clean up orphaned files (files not referenced by any FIR or complaint).
    This is a maintenance endpoint, typically called by administrators.
    """
    try:
        # Get all uploaded files
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            return format_success_response(message="Upload folder does not exist")

        # Get all files in upload folder
        uploaded_files = set()
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), upload_folder)
                uploaded_files.add(relative_path)

        # Get all referenced files from database
        from app.models.fir import FIR
        from app.models.complaint import Complaint

        referenced_files = set()

        # Get files from FIRs
        firs = FIR.query.all()
        for fir in firs:
            fir_files = fir.get_evidence_files()
            referenced_files.update(fir_files)

        # Get files from complaints
        complaints = Complaint.query.all()
        for complaint in complaints:
            complaint_files = complaint.get_evidence_files()
            referenced_files.update(complaint_files)

        # Find orphaned files
        orphaned_files = uploaded_files - referenced_files

        # Delete orphaned files
        deleted_files = []
        errors = []

        for file_path in orphaned_files:
            full_path = os.path.join(upload_folder, file_path)
            try:
                success = delete_file(full_path)
                if success:
                    deleted_files.append(file_path)
                else:
                    errors.append(file_path)
            except Exception:
                errors.append(file_path)

        # Log activity
        log_user_activity(current_user.id, 'orphaned_files_cleanup', {
            'total_files': len(uploaded_files),
            'referenced_files': len(referenced_files),
            'orphaned_files': len(orphaned_files),
            'deleted_files': len(deleted_files),
            'errors': len(errors)
        })

        return format_success_response(
            data={
                'summary': {
                    'total_files': len(uploaded_files),
                    'referenced_files': len(referenced_files),
                    'orphaned_files': len(orphaned_files),
                    'deleted_files': len(deleted_files),
                    'errors': len(errors)
                },
                'deleted_files': deleted_files,
                'errors': errors
            },
            message=f"Cleaned up {len(deleted_files)} orphaned files" +
                   (f" with {len(errors)} errors" if errors else "")
        )

    except Exception as e:
        return format_error_response("Failed to cleanup orphaned files")

@upload_bp.route('/stats', methods=['GET'])
@login_required
@authenticated_required
def get_upload_stats():
    """
    Get upload statistics for the current user.
    """
    try:
        # Get file count and size from user's FIRs and complaints
        from app.models.fir import FIR
        from app.models.complaint import Complaint

        total_files = 0
        total_size = 0

        # Count files from user's FIRs
        user_firs = FIR.query.filter_by(user_id=current_user.id).all()
        for fir in user_firs:
            fir_files = fir.get_evidence_files()
            for file_path in fir_files:
                total_files += 1
                full_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), file_path)
                if os.path.exists(full_path):
                    total_size += os.path.getsize(full_path)

        # Count files from user's complaints
        user_complaints = Complaint.query.filter_by(user_id=current_user.id).all()
        for complaint in user_complaints:
            complaint_files = complaint.get_evidence_files()
            for file_path in complaint_files:
                total_files += 1
                full_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), file_path)
                if os.path.exists(full_path):
                    total_size += os.path.getsize(full_path)

        stats = {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_formatted': format_file_size(total_size),
            'fir_files': len(user_firs),
            'complaint_files': len(user_complaints)
        }

        return format_success_response(data=stats)

    except Exception as e:
        return format_error_response("Failed to retrieve upload statistics")

def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"