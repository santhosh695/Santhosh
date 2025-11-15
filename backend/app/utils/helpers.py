import os
import uuid
from datetime import datetime
from flask import current_app, jsonify
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """
    Check if the file has an allowed extension.

    Args:
        filename (str): Name of the file

    Returns:
        bool: True if file is allowed, False otherwise
    """
    if not filename:
        return False

    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """
    Generate a unique filename to prevent collisions.

    Args:
        filename (str): Original filename

    Returns:
        str: Unique filename with timestamp and UUID
    """
    if not filename:
        return None

    # Get file extension
    if '.' not in filename:
        return None

    extension = filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]

    return f"{timestamp}_{unique_id}.{extension}"

def format_error_response(message, status_code=400, details=None):
    """
    Format a standardized error response.

    Args:
        message (str): Error message
        status_code (int): HTTP status code
        details (dict): Additional error details

    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }

    if details:
        response['details'] = details

    return response, status_code

def format_success_response(data=None, message=None, status_code=200):
    """
    Format a standardized success response.

    Args:
        data (dict): Response data
        message (str): Success message
        status_code (int): HTTP status code

    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': True,
        'timestamp': datetime.utcnow().isoformat()
    }

    if data:
        response['data'] = data

    if message:
        response['message'] = message

    return response, status_code

def paginate_response(query, page, per_page, endpoint, **kwargs):
    """
    Create a paginated response.

    Args:
        query: SQLAlchemy query object
        page (int): Page number
        per_page (int): Items per page
        endpoint (str): Endpoint name for URL generation
        **kwargs: Additional arguments for URL generation

    Returns:
        dict: Paginated response
    """
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    items = [item.to_dict() for item in pagination.items]

    response = {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }
    }

    return response

def save_uploaded_file(file, upload_folder=None):
    """
    Save an uploaded file securely.

    Args:
        file: FileStorage object
        upload_folder (str): Custom upload folder (optional)

    Returns:
        str: Path to saved file or None if failed
    """
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    # Get upload folder
    if upload_folder:
        folder = upload_folder
    else:
        folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(filename)

    if not unique_filename:
        return None

    # Save file
    file_path = os.path.join(folder, unique_filename)
    try:
        file.save(file_path)
        return file_path
    except Exception:
        return None

def delete_file(file_path):
    """
    Delete a file from the filesystem.

    Args:
        file_path (str): Path to file to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def format_file_size(size_bytes):
    """
    Format file size in human-readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"

def extract_keywords_from_text(text, max_keywords=10):
    """
    Extract keywords from text using simple frequency analysis.

    Args:
        text (str): Text to analyze
        max_keywords (int): Maximum number of keywords to return

    Returns:
        list: List of keywords
    """
    if not text:
        return []

    # Simple keyword extraction - remove common words and get frequent words
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
        'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'can', 'will', 'just', 'don', 'should', 'now', 'i', 'me', 'my', 'we',
        'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its',
        'they', 'them', 'their', 'what', 'which', 'who', 'whom', 'this', 'that',
        'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'should'
    }

    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    # Filter out common words and short words
    filtered_words = [
        word for word in words
        if word not in common_words and len(word) > 2
    ]

    # Count word frequency
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]

def sanitize_text(text, max_length=None):
    """
    Sanitize text input by removing potentially harmful characters.

    Args:
        text (str): Text to sanitize
        max_length (int): Maximum length (optional)

    Returns:
        str: Sanitized text
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)

    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()

    # Truncate if max_length is specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].strip()

    return sanitized

def log_user_activity(user_id, action, details=None):
    """
    Log user activity (placeholder for future logging implementation).

    Args:
        user_id (int): User ID
        action (str): Action performed
        details (dict): Additional details
    """
    # This is a placeholder for future logging implementation
    # Could be extended to write to database, file, or external logging service
    activity_log = {
        'user_id': user_id,
        'action': action,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }

    # For now, just print to console (in production, use proper logging)
    current_app.logger.info(f"User activity: {activity_log}")