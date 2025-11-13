from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.complaint import Complaint, create_complaint, get_complaint_by_id, update_complaint, delete_complaint, format_complaint_with_ai
from app.utils.decorators import authenticated_required
from app.utils.validators import validate_complaint_data
from app.utils.helpers import format_error_response, format_success_response, paginate_response, log_user_activity

public_bp = Blueprint('public', __name__)

@public_bp.route('/complaint', methods=['GET'])
@login_required
@authenticated_required
def get_complaints():
    """
    Get list of complaints for the logged-in user.
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

        # Get complaints based on filters
        if search:
            pagination = Complaint.search_complaints(current_user.id, search, page, per_page)
        elif status:
            pagination = Complaint.get_by_user_id(current_user.id, status, page, per_page)
        else:
            pagination = Complaint.get_by_user_id(current_user.id, None, page, per_page)

        # Format response
        response = {
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
            'items': [complaint.to_dict(include_formatted=True) for complaint in pagination.items]
        }

        # Log activity
        log_user_activity(current_user.id, 'complaints_listed', {
            'filters': {
                'status': status,
                'search': search,
                'page': page,
                'per_page': per_page
            }
        })

        return format_success_response(data=response)

    except Exception as e:
        return format_error_response("Failed to retrieve complaints")

@public_bp.route('/complaint', methods=['POST'])
@login_required
@authenticated_required
def create_complaint_endpoint():
    """
    Create a new complaint.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        # Validate complaint data
        is_valid, error_message = validate_complaint_data(data)
        if not is_valid:
            return format_error_response(error_message)

        # Extract complaint data
        original_text = data.get('original_text', '').strip()
        category = data.get('category', '').strip() or None

        # Create complaint
        complaint = create_complaint(
            user_id=current_user.id,
            original_text=original_text,
            category=category
        )

        # Log activity
        log_user_activity(current_user.id, 'complaint_created', {
            'complaint_id': complaint.id,
            'category': category
        })

        return format_success_response(
            data=complaint.to_dict(),
            message="Complaint created successfully",
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to create complaint")

@public_bp.route('/complaint/<int:complaint_id>', methods=['GET'])
@login_required
@authenticated_required
def get_complaint(complaint_id):
    """
    Get a specific complaint by ID.
    """
    try:
        complaint = get_complaint_by_id(complaint_id)
        if not complaint:
            return format_error_response("Complaint not found", 404)

        # Check if user owns this complaint
        if complaint.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Log activity
        log_user_activity(current_user.id, 'complaint_viewed', {'complaint_id': complaint_id})

        return format_success_response(data=complaint.to_dict(include_formatted=True))

    except Exception as e:
        return format_error_response("Failed to retrieve complaint")

@public_bp.route('/complaint/<int:complaint_id>', methods=['PUT'])
@login_required
@authenticated_required
def update_complaint_endpoint(complaint_id):
    """
    Update an existing complaint.
    """
    try:
        complaint = get_complaint_by_id(complaint_id)
        if not complaint:
            return format_error_response("Complaint not found", 404)

        # Check if user owns this complaint
        if complaint.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Check if complaint can be updated (only drafts can be updated)
        if complaint.is_formatted() or complaint.is_archived():
            return format_error_response("Cannot update formatted or archived complaint")

        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        # Validate updated data
        is_valid, error_message = validate_complaint_data(data)
        if not is_valid:
            return format_error_response(error_message)

        # Update complaint
        updated_complaint = update_complaint(complaint_id, **data)

        # Log activity
        log_user_activity(current_user.id, 'complaint_updated', {'complaint_id': complaint_id})

        return format_success_response(
            data=updated_complaint.to_dict(),
            message="Complaint updated successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to update complaint")

@public_bp.route('/complaint/<int:complaint_id>', methods=['DELETE'])
@login_required
@authenticated_required
def delete_complaint_endpoint(complaint_id):
    """
    Delete a complaint.
    """
    try:
        complaint = get_complaint_by_id(complaint_id)
        if not complaint:
            return format_error_response("Complaint not found", 404)

        # Check if user owns this complaint
        if complaint.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Check if complaint can be deleted (only drafts can be deleted)
        if complaint.is_formatted():
            return format_error_response("Cannot delete formatted complaint")

        # Delete complaint
        success = delete_complaint(complaint_id)
        if success:
            # Log activity
            log_user_activity(current_user.id, 'complaint_deleted', {'complaint_id': complaint_id})

            return format_success_response(message="Complaint deleted successfully")
        else:
            return format_error_response("Failed to delete complaint")

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to delete complaint")

@public_bp.route('/complaint/<int:complaint_id>/format', methods=['POST'])
@login_required
@authenticated_required
def format_complaint(complaint_id):
    """
    Format a complaint using AI.
    """
    try:
        complaint = get_complaint_by_id(complaint_id)
        if not complaint:
            return format_error_response("Complaint not found", 404)

        # Check if user owns this complaint
        if complaint.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Check if complaint can be formatted (only drafts can be formatted)
        if not complaint.is_draft():
            return format_error_response("Complaint is already formatted")

        # TODO: Implement AI formatting in AI service
        # For now, create a basic formatted version
        basic_formatted = f"""
FORMAL COMPLAINT

Date: {complaint.created_at.strftime('%d/%m/%Y')}

Subject: {complaint.category or 'General Complaint'}

Details:
{complaint.original_text}

This is a formal complaint based on the above details. The matter requires appropriate investigation and action.

Thank you for your attention to this matter.

Sincerely,
{current_user.name}
Email: {current_user.email}
        """.strip()

        basic_suggestions = {
            'improvements': [
                'Add specific dates and times',
                'Include witness information if available',
                'Add supporting evidence if available',
                'Specify desired resolution'
            ],
            'recommended_actions': [
                'Submit to relevant authority',
                'Keep copy for records',
                'Follow up if no response within 15 days'
            ]
        }

        # Update complaint with formatted version
        format_complaint_with_ai(complaint_id, basic_formatted, basic_suggestions)

        # Log activity
        log_user_activity(current_user.id, 'complaint_formatted', {'complaint_id': complaint_id})

        return format_success_response(
            data=complaint.to_dict(include_formatted=True),
            message="Complaint formatted successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to format complaint")

@public_bp.route('/complaint/<int:complaint_id>/archive', methods=['POST'])
@login_required
@authenticated_required
def archive_complaint(complaint_id):
    """
    Archive a complaint.
    """
    try:
        complaint = get_complaint_by_id(complaint_id)
        if not complaint:
            return format_error_response("Complaint not found", 404)

        # Check if user owns this complaint
        if complaint.user_id != current_user.id:
            return format_error_response("Access denied", 403)

        # Archive complaint
        complaint.archive()
        db.session.commit()

        # Log activity
        log_user_activity(current_user.id, 'complaint_archived', {'complaint_id': complaint_id})

        return format_success_response(
            data=complaint.to_dict(),
            message="Complaint archived successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Failed to archive complaint")

@public_bp.route('/complaint/search', methods=['GET'])
@login_required
@authenticated_required
def search_complaints():
    """
    Search complaints by content.
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

        # Search complaints
        pagination = Complaint.search_complaints(current_user.id, search_term, page, per_page)

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
            'items': [complaint.to_dict() for complaint in pagination.items]
        }

        # Log activity
        log_user_activity(current_user.id, 'complaints_searched', {
            'search_term': search_term,
            'results_count': pagination.total
        })

        return format_success_response(data=response)

    except Exception as e:
        return format_error_response("Failed to search complaints")

@public_bp.route('/complaint/stats', methods=['GET'])
@login_required
@authenticated_required
def get_complaint_stats():
    """
    Get complaint statistics for the logged-in user.
    """
    try:
        # Get counts by status
        total_complaints = Complaint.query.filter_by(user_id=current_user.id).count()
        draft_complaints = Complaint.query.filter_by(user_id=current_user.id, status='draft').count()
        formatted_complaints = Complaint.query.filter_by(user_id=current_user.id, status='formatted').count()
        archived_complaints = Complaint.query.filter_by(user_id=current_user.id, status='archived').count()

        # Get recent complaints
        recent_complaints = Complaint.query.filter_by(user_id=current_user.id)\
            .order_by(Complaint.created_at.desc())\
            .limit(5)\
            .all()

        stats = {
            'total_complaints': total_complaints,
            'draft_complaints': draft_complaints,
            'formatted_complaints': formatted_complaints,
            'archived_complaints': archived_complaints,
            'recent_complaints': [complaint.to_dict() for complaint in recent_complaints]
        }

        return format_success_response(data=stats)

    except Exception as e:
        return format_error_response("Failed to retrieve complaint statistics")

@public_bp.route('/complaint/categories', methods=['GET'])
@login_required
@authenticated_required
def get_complaint_categories():
    """
    Get predefined complaint categories.
    """
    try:
        categories = [
            {'value': 'civil_dispute', 'label': 'Civil Dispute'},
            {'value': 'property_dispute', 'label': 'Property Dispute'},
            {'value': 'consumer_complaint', 'label': 'Consumer Complaint'},
            {'value': 'employment_dispute', 'label': 'Employment Dispute'},
            {'value': 'family_matter', 'label': 'Family Matter'},
            {'value': 'harassment', 'label': 'Harassment'},
            {'value': 'fraud', 'label': 'Fraud'},
            {'value': 'theft', 'label': 'Theft'},
            {'value': 'public_service', 'label': 'Public Service Complaint'},
            {'value': 'environmental', 'label': 'Environmental Issue'},
            {'value': 'educational', 'label': 'Educational Matter'},
            {'value': 'healthcare', 'label': 'Healthcare Complaint'},
            {'value': 'traffic_violation', 'label': 'Traffic Violation'},
            {'value': 'noise_pollution', 'label': 'Noise Pollution'},
            {'value': 'other', 'label': 'Other'}
        ]

        return format_success_response(data=categories)

    except Exception as e:
        return format_error_response("Failed to retrieve complaint categories")