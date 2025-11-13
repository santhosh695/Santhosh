import re
from flask import current_app
from werkzeug.datastructures import FileStorage

def validate_email(email):
    """
    Validate email format and domain requirements.

    Args:
        email (str): Email address to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    email = email.strip().lower()

    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    # Length validation
    if len(email) > 120:
        return False, "Email address is too long"

    # Check for common invalid domains
    invalid_domains = ['example.com', 'test.com', 'invalid.com']
    domain = email.split('@')[-1]
    if domain in invalid_domains:
        return False, "Invalid email domain"

    return True, None

def validate_password(password):
    """
    Validate password strength.

    Args:
        password (str): Password to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password is too long"

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    # Check for common weak passwords
    weak_passwords = [
        'password', 'password123', '12345678', 'qwerty123',
        'admin123', 'letmein', 'welcome123'
    ]
    if password.lower() in weak_passwords:
        return False, "Password is too common. Please choose a stronger password"

    return True, None

def validate_name(name):
    """
    Validate user name.

    Args:
        name (str): Name to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"

    name = name.strip()

    if len(name) < 2:
        return False, "Name must be at least 2 characters long"

    if len(name) > 100:
        return False, "Name is too long"

    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
        return False, "Name can only contain letters, spaces, hyphens, and apostrophes"

    # Check for consecutive spaces
    if '  ' in name:
        return False, "Name cannot contain consecutive spaces"

    return True, None

def validate_phone(phone):
    """
    Validate phone number.

    Args:
        phone (str): Phone number to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not phone:
        return True, None  # Phone is optional

    phone = phone.strip()

    # Remove common formatting characters
    phone_digits = re.sub(r'[+\-\s\(\)]', '', phone)

    # Check if all characters are digits
    if not phone_digits.isdigit():
        return False, "Phone number can only contain digits and formatting characters"

    # Check length (Indian phone numbers: 10 digits for mobile, landline varies)
    if len(phone_digits) < 6 or len(phone_digits) > 15:
        return False, "Phone number has invalid length"

    # Basic Indian phone number validation
    if len(phone_digits) == 10:
        # Mobile number validation
        if not phone_digits.startswith(('6', '7', '8', '9')):
            return False, "Invalid Indian mobile number"
    elif len(phone_digits) == 11 and phone_digits.startswith('0'):
        # Mobile number with leading 0
        if not phone_digits.startswith(('06', '07', '08', '09')):
            return False, "Invalid Indian mobile number"
    elif len(phone_digits) >= 11:
        # Landline with area code
        pass  # Accept longer numbers for landlines with area codes

    return True, None

def validate_file_upload(file):
    """
    Validate uploaded file.

    Args:
        file (FileStorage): Uploaded file object

    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"

    if not isinstance(file, FileStorage):
        return False, "Invalid file object"

    # Check file size
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)  # 50MB default
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset pointer

    if file_size > max_size:
        return False, f"File size exceeds maximum limit of {max_size // (1024 * 1024)}MB"

    # Check file extension
    filename = file.filename
    if not filename:
        return False, "File must have a name"

    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    if '.' not in filename:
        return False, "File must have an extension"

    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type '{extension}' is not allowed"

    # Check for potentially dangerous file names
    dangerous_patterns = ['../', '..\\', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False, "File name contains invalid characters"

    return True, None

def validate_fir_data(data):
    """
    Validate FIR creation/update data.

    Args:
        data (dict): FIR data to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"

    # Complaint text validation
    complaint_text = data.get('complaint_text', '').strip()
    if not complaint_text:
        return False, "Complaint text is required"

    if len(complaint_text) < 10:
        return False, "Complaint text must be at least 10 characters long"

    if len(complaint_text) > 10000:
        return False, "Complaint text is too long (max 10,000 characters)"

    # FIR type validation
    fir_type = data.get('fir_type', '').strip()
    if fir_type and len(fir_type) > 50:
        return False, "FIR type is too long"

    # Incident location validation
    incident_location = data.get('incident_location', '').strip()
    if incident_location and len(incident_location) > 200:
        return False, "Incident location is too long"

    return True, None

def validate_complaint_data(data):
    """
    Validate complaint creation/update data.

    Args:
        data (dict): Complaint data to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"

    # Original text validation
    original_text = data.get('original_text', '').strip()
    if not original_text:
        return False, "Complaint text is required"

    if len(original_text) < 10:
        return False, "Complaint text must be at least 10 characters long"

    if len(original_text) > 10000:
        return False, "Complaint text is too long (max 10,000 characters)"

    # Category validation
    category = data.get('category', '').strip()
    if category and len(category) > 50:
        return False, "Category is too long"

    return True, None