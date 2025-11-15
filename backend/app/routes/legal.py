from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.legal_act import LegalAct, get_legal_act_by_id, get_legal_act_by_section
from app.utils.decorators import authenticated_required
from app.utils.helpers import format_error_response, format_success_response, log_user_activity

legal_bp = Blueprint('legal', __name__)

@legal_bp.route('/search', methods=['GET'])
@authenticated_required
def search_legal_acts():
    """
    Search legal acts by keyword, section, or advanced filters.
    Accessible to both police and public users.
    """
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        section = request.args.get('section', '').strip()
        category = request.args.get('category', '').strip()
        act_name = request.args.get('act', '').strip()
        bailable = request.args.get('bailable', '').strip().lower()
        cognizable = request.args.get('cognizable', '').strip().lower()
        limit = request.args.get('limit', 20, type=int)

        # Validate limit
        if limit < 1 or limit > 100:
            limit = 20

        # Parse boolean parameters
        bailable_bool = None if bailable not in ['true', 'false'] else bailable == 'true'
        cognizable_bool = None if cognizable not in ['true', 'false'] else cognizable == 'true'

        # Perform search
        if section:
            # Search by section number
            results = LegalAct.search_by_section(section, limit)
        elif query or category or act_name or bailable_bool is not None or cognizable_bool is not None:
            # Advanced search
            results = LegalAct.advanced_search(
                query=query if query else None,
                category=category if category else None,
                act_name=act_name if act_name else None,
                bailable=bailable_bool,
                cognizable=cognizable_bool,
                limit=limit
            )
        else:
            # Simple keyword search
            results = LegalAct.search_by_keyword(query, limit)

        # Format results
        formatted_results = [act.to_dict() for act in results]

        # Log activity
        log_user_activity(current_user.id, 'legal_search', {
            'query': query,
            'section': section,
            'category': category,
            'act_name': act_name,
            'results_count': len(formatted_results)
        })

        return format_success_response(data={
            'results': formatted_results,
            'search_params': {
                'query': query,
                'section': section,
                'category': category,
                'act_name': act_name,
                'bailable': bailable,
                'cognizable': cognizable,
                'limit': limit
            },
            'count': len(formatted_results)
        })

    except Exception as e:
        return format_error_response("Failed to search legal acts")

@legal_bp.route('/section/<string:act_name>/<string:section_number>', methods=['GET'])
@authenticated_required
def get_legal_section(act_name, section_number):
    """
    Get a specific legal section by act name and section number.
    """
    try:
        # URL decode act name and section number
        from urllib.parse import unquote
        act_name = unquote(act_name)
        section_number = unquote(section_number)

        # Get legal act
        legal_act = get_legal_act_by_section(act_name, section_number)
        if not legal_act:
            return format_error_response("Legal section not found", 404)

        # Log activity
        log_user_activity(current_user.id, 'legal_section_viewed', {
            'act_name': act_name,
            'section_number': section_number
        })

        return format_success_response(data=legal_act.to_dict())

    except Exception as e:
        return format_error_response("Failed to retrieve legal section")

@legal_bp.route('/section/<int:section_id>', methods=['GET'])
@authenticated_required
def get_legal_section_by_id(section_id):
    """
    Get a specific legal section by ID.
    """
    try:
        # Get legal act
        legal_act = get_legal_act_by_id(section_id)
        if not legal_act:
            return format_error_response("Legal section not found", 404)

        # Log activity
        log_user_activity(current_user.id, 'legal_section_viewed', {
            'section_id': section_id
        })

        return format_success_response(data=legal_act.to_dict())

    except Exception as e:
        return format_error_response("Failed to retrieve legal section")

@legal_bp.route('/acts', methods=['GET'])
@authenticated_required
def get_legal_acts():
    """
    Get list of available legal acts.
    """
    try:
        # Get unique act names
        acts = db.session.query(LegalAct.act_name, LegalAct.category)\
            .distinct()\
            .order_by(LegalAct.act_name)\
            .all()

        # Group by category
        acts_by_category = {}
        for act_name, category in acts:
            if category not in acts_by_category:
                acts_by_category[category] = []
            acts_by_category[category].append({
                'name': act_name,
                'display_name': act_name.replace('_', ' ').title()
            })

        # Log activity
        log_user_activity(current_user.id, 'legal_acts_listed')

        return format_success_response(data={
            'categories': acts_by_category,
            'total_acts': len(acts)
        })

    except Exception as e:
        return format_error_response("Failed to retrieve legal acts")

@legal_bp.route('/act/<string:act_name>/sections', methods=['GET'])
@authenticated_required
def get_act_sections(act_name):
    """
    Get all sections of a specific act.
    """
    try:
        # URL decode act name
        from urllib.parse import unquote
        act_name = unquote(act_name)

        # Get sections
        limit = request.args.get('limit', 100, type=int)
        sections = LegalAct.get_by_act(act_name, limit)

        if not sections:
            return format_error_response("Act not found or has no sections", 404)

        # Format results
        formatted_sections = [section.to_dict() for section in sections]

        # Log activity
        log_user_activity(current_user.id, 'act_sections_viewed', {
            'act_name': act_name,
            'sections_count': len(formatted_sections)
        })

        return format_success_response(data={
            'act_name': act_name,
            'sections': formatted_sections,
            'count': len(formatted_sections)
        })

    except Exception as e:
        return format_error_response("Failed to retrieve act sections")

@legal_bp.route('/categories', methods=['GET'])
@authenticated_required
def get_legal_categories():
    """
    Get list of legal act categories.
    """
    try:
        # Get unique categories
        categories = db.session.query(LegalAct.category)\
            .distinct()\
            .order_by(LegalAct.category)\
            .all()

        # Format categories
        formatted_categories = [
            {
                'name': category[0],
                'display_name': category[0].replace('_', ' ').title()
            }
            for category in categories
        ]

        return format_success_response(data=formatted_categories)

    except Exception as e:
        return format_error_response("Failed to retrieve legal categories")

@legal_bp.route('/analyze', methods=['POST'])
@authenticated_required
def analyze_text_for_sections():
    """
    Analyze text to suggest relevant legal sections.
    AI-powered analysis endpoint.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        text = data.get('text', '').strip()
        if not text:
            return format_error_response("Text is required")

        if len(text) < 50:
            return format_error_response("Text is too short for analysis")

        # TODO: Implement AI analysis in AI service
        # For now, return basic keyword-based suggestions
        from app.utils.helpers import extract_keywords_from_text

        keywords = extract_keywords_from_text(text, max_keywords=5)
        suggested_sections = []

        # Search for sections based on keywords
        for keyword in keywords:
            matching_sections = LegalAct.search_by_keyword(keyword, limit=3)
            for section in matching_sections:
                section_dict = section.to_dict()
                section_dict['match_reason'] = f"Keyword match: '{keyword}'"
                suggested_sections.append(section_dict)

        # Remove duplicates and limit results
        unique_sections = []
        seen_ids = set()
        for section in suggested_sections:
            if section['id'] not in seen_ids:
                unique_sections.append(section)
                seen_ids.add(section['id'])
            if len(unique_sections) >= 10:
                break

        # Log activity
        log_user_activity(current_user.id, 'legal_analysis', {
            'text_length': len(text),
            'keywords': keywords,
            'suggestions_count': len(unique_sections)
        })

        return format_success_response(data={
            'keywords': keywords,
            'suggested_sections': unique_sections,
            'analysis_type': 'keyword_based'
        })

    except Exception as e:
        return format_error_response("Failed to analyze text")

@legal_bp.route('/popular', methods=['GET'])
@authenticated_required
def get_popular_sections():
    """
    Get popular/commonly referenced legal sections.
    """
    try:
        # For now, return some commonly used sections
        # In a real application, this could be based on usage statistics
        popular_sections = [
            "IPC 302", "IPC 304", "IPC 306", "IPC 323", "IPC 324",
            "IPC 363", "IPC 364", "IPC 365", "IPC 366", "IPC 376",
            "IPC 379", "IPC 380", "IPC 420", "IPC 468", "IPC 506",
            "CrPC 154", "CrPC 173", "CrPC 177", "CrPC 207"
        ]

        results = []
        for section_ref in popular_sections:
            if ' ' in section_ref:
                act_name, section_num = section_ref.split(' ', 1)
                act_name = act_name.strip()
                section_num = section_num.strip()

                legal_act = get_legal_act_by_section(
                    act_name + (' Code' if act_name not in ['Indian Penal', 'Code of Criminal'] else ''),
                    section_num
                )
                if legal_act:
                    results.append(legal_act.to_dict())

        # Log activity
        log_user_activity(current_user.id, 'popular_sections_viewed')

        return format_success_response(data={
            'sections': results,
            'count': len(results)
        })

    except Exception as e:
        return format_error_response("Failed to retrieve popular sections")