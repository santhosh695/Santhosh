from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.fir import FIR, create_fir, get_fir_by_id, update_fir, delete_fir
from app.utils.decorators import police_required
from app.utils.validators import validate_fir_data
from app.utils.helpers import format_error_response, format_success_response, paginate_response, log_user_activity

fir_bp = Blueprint('fir', __name__)

@fir_bp.route('/fir', methods=['GET'])
@login_required
@police_required
def get_firs():
    """
    Get list of FIRs for the logged-in police officer.
    Supports pagination and filtering.
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '')
        search = request.args.get('search', '')

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Get FIRs based on filters
        if search:
            pagination = FIR.search_firs(current_user.id, search, page, per_page)
        elif status:
            pagination = FIR.get_by_user_id(current_user.id, status, page, per_page)
        else:
            pagination = FIR.get_by_user_id(current_user.id, None, page, per_page)

        # Format response
        response = paginate_response(
            lambda: pagination.items,
            page,
            per_page,
            'fir.get_firs',
            status=status,
            search=search
        )

        # Update pagination data
        response['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }

        # Convert items to dictionaries
        response['items'] = [fir.to_dict(include_ai_data=True) for fir in pagination.items]

        # Log activity
        log_user_activity(current_user.id, 'firs_listed', {
            'filters': {
                'status': status,
                'search': search,
                'page': page,
                'per_page': per_page
            }
        })

        return format_success_response(data=response)

    except Exception as e:
        return format_error_response("Failed to retrieve FIRs")

@fir_bp.route('/fir', methods=['POST'])
@login_required
@police_required
def create_fir_endpoint():
    """
    Create a new FIR with AI analysis.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        # Validate FIR data
        is_valid, error_message = validate_fir_data(data)
        if not is_valid:
            return format_error_response(error_message)

        # Extract FIR data
        complaint_text = data.get('complaint_text', '').strip()
        fir_type = data.get('fir_type', '').strip() or None
        incident_date = data.get('incident_date')
        incident_location = data.get('incident_location', '').strip() or None

        # Convert incident_date to datetime if provided
        if incident_date:
            from datetime import datetime
            try:
                incident_date = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
            except ValueError:
                return format_error_response("Invalid incident date format")

        # Create FIR
        fir = create_fir(
            user_id=current_user.id,
            complaint_text=complaint_text,
            fir_type=fir_type,
            incident_date=incident_date,
            incident_location=incident_location
        )

        # TODO: Trigger AI analysis (will be implemented in AI service)
        # For now, we'll create a basic AI analysis
        basic_analysis = f"Analysis of complaint: {complaint_text[:200]}..."
        basic_sections = [
            {
                'act': 'Indian Penal Code',
                'section': 'To be determined',
                'description': 'AI analysis pending'
            }
        ]
        basic_structured = {
            'title': 'First Information Report',
            'sections': [
                {
                    'heading': 'Complaint Details',
                    'content': complaint_text
                }
            ]
        }

        fir.set_ai_analysis(basic_analysis, basic_sections, basic_structured)
        db.session.commit()

        # Log activity
        log_user_activity(current_user.id, 'fir_created', {
            'fir_id': fir.id,
            'fir_type': fir_type
        })

        return format_success_response(
            data=fir.to_dict(include_ai_data=True),
            message="FIR created successfully",
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to create FIR")

@fir_bp.route('/fir/<int:fir_id>', methods=['GET'])
@login_required
@police_required
def get_fir(fir_id):
    """
    Get a specific FIR by ID.
    """
    try:
        fir = get_fir_by_id(fir_id)
        if not fir:
            return format_error_response("FIR not found", 404)

        # Check if user owns this FIR
        if fir.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Log activity
        log_user_activity(current_user.id, 'fir_viewed', {'fir_id': fir_id})

        return format_success_response(data=fir.to_dict(include_ai_data=True))

    except Exception as e:
        return format_error_response("Failed to retrieve FIR")

@fir_bp.route('/fir/<int:fir_id>', methods=['PUT'])
@login_required
@police_required
def update_fir_endpoint(fir_id):
    """
    Update an existing FIR.
    """
    try:
        fir = get_fir_by_id(fir_id)
        if not fir:
            return format_error_response("FIR not found", 404)

        # Check if user owns this FIR
        if fir.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Check if FIR can be updated (only drafts can be updated)
        if fir.is_submitted() or fir.is_archived():
            return format_error_response("Cannot update submitted or archived FIR")

        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        # Validate updated data
        is_valid, error_message = validate_fir_data(data)
        if not is_valid:
            return format_error_response(error_message)

        # Update FIR
        updated_fir = update_fir(fir_id, **data)

        # Log activity
        log_user_activity(current_user.id, 'fir_updated', {'fir_id': fir_id})

        return format_success_response(
            data=updated_fir.to_dict(include_ai_data=True),
            message="FIR updated successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to update FIR")

@fir_bp.route('/fir/<int:fir_id>', methods=['DELETE'])
@login_required
@police_required
def delete_fir_endpoint(fir_id):
    """
    Delete a FIR.
    """
    try:
        fir = get_fir_by_id(fir_id)
        if not fir:
            return format_error_response("FIR not found", 404)

        # Check if user owns this FIR
        if fir.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Check if FIR can be deleted (only drafts can be deleted)
        if fir.is_submitted():
            return format_error_response("Cannot delete submitted FIR")

        # Delete FIR
        success = delete_fir(fir_id)
        if success:
            # Log activity
            log_user_activity(current_user.id, 'fir_deleted', {'fir_id': fir_id})

            return format_success_response(message="FIR deleted successfully")
        else:
            return format_error_response("Failed to delete FIR")

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to delete FIR")

@fir_bp.route('/fir/<int:fir_id>/submit', methods=['POST'])
@login_required
@police_required
def submit_fir(fir_id):
    """
    Submit a FIR (change status from draft to submitted).
    """
    try:
        fir = get_fir_by_id(fir_id)
        if not fir:
            return format_error_response("FIR not found", 404)

        # Check if user owns this FIR
        if fir.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Check if FIR can be submitted
        if not fir.is_draft():
            return format_error_response("FIR is already submitted")

        # Submit FIR
        fir.submit()
        db.session.commit()

        # Log activity
        log_user_activity(current_user.id, 'fir_submitted', {'fir_id': fir_id})

        return format_success_response(
            data=fir.to_dict(),
            message="FIR submitted successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to submit FIR")

@fir_bp.route('/fir/<int:fir_id>/archive', methods=['POST'])
@login_required
@police_required
def archive_fir(fir_id):
    """
    Archive a FIR.
    """
    try:
        fir = get_fir_by_id(fir_id)
        if not fir:
            return format_error_response("FIR not found", 404)

        # Check if user owns this FIR
        if fir.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Archive FIR
        fir.archive()
        db.session.commit()

        # Log activity
        log_user_activity(current_user.id, 'fir_archived', {'fir_id': fir_id})

        return format_success_response(
            data=fir.to_dict(),
            message="FIR archived successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to archive FIR")

@fir_bp.route('/fir/search', methods=['GET'])
@login_required
@police_required
def search_firs():
    """
    Search FIRs by content.
    """
    try:
        search_term = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if not search_term:
            return format_error_response("Search term is required")

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Search FIRs
        pagination = FIR.search_firs(current_user.id, search_term, page, per_page)

        # Format response
        response = {
            'search_term': search_term,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next,
                'prev_num': pagination.prev_num,
                'next_num': pagination.next_num
            },
            'items': [fir.to_dict() for fir in pagination.items]
        }

        # Log activity
        log_user_activity(current_user.id, 'firs_searched', {
            'search_term': search_term,
            'results_count': pagination.total
        })

        return format_success_response(data=response)

    except Exception as e:
        return format_error_response("Failed to search FIRs")

@fir_bp.route('/fir/stats', methods=['GET'])
@login_required
@police_required
def get_fir_stats():
    """
    Get FIR statistics for the logged-in police officer.
    """
    try:
        # Get counts by status
        total_firs = FIR.query.filter_by(user_id=current_user.id).count()
        draft_firs = FIR.query.filter_by(user_id=current_user.id, status='draft').count()
        submitted_firs = FIR.query.filter_by(user_id=current_user.id, status='submitted').count()
        archived_firs = FIR.query.filter_by(user_id=current_user.id, status='archived').count()

        # Get recent FIRs
        recent_firs = FIR.query.filter_by(user_id=current_user.id)\
            .order_by(FIR.created_at.desc())\
            .limit(5)\
            .all()

        stats = {
            'total_firs': total_firs,
            'draft_firs': draft_firs,
            'submitted_firs': submitted_firs,
            'archived_firs': archived_firs,
            'recent_firs': [fir.to_dict() for fir in recent_firs]
        }

        return format_success_response(data=stats)

    except Exception as e:
        return format_error_response("Failed to retrieve FIR statistics")