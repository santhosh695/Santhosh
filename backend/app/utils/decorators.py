from functools import wraps
from flask import abort, jsonify, current_app
from flask_login import current_user

def role_required(required_role):
    """
    Decorator to require specific role to access a route.

    Args:
        required_role (str): Required role ('police' or 'public')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401

            if current_user.role != required_role:
                return jsonify({'error': 'Access forbidden: insufficient privileges'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def police_required(f):
    """
    Decorator to require police role to access a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        if not current_user.is_police():
            return jsonify({'error': 'Access forbidden: police privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def public_required(f):
    """
    Decorator to require public role to access a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        if not current_user.is_public():
            return jsonify({'error': 'Access forbidden: public access required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def authenticated_required(f):
    """
    Decorator to require authentication (any role).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """
    Decorator to require active user account.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        if not current_user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403

        return f(*args, **kwargs)
    return decorated_function

# Combine decorators for common use cases
def police_active_required(f):
    """
    Decorator to require active police user.
    """
    return police_required(active_user_required(f))

def public_active_required(f):
    """
    Decorator to require active public user.
    """
    return public_required(active_user_required(f))