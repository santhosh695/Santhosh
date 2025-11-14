from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, create_user, authenticate_user, get_user_by_email
from app.utils.validators import validate_email, validate_password, validate_name, validate_phone
from app.utils.helpers import format_error_response, format_success_response, log_user_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint without validation"""
    try:
        return {
            "success": True,
            "message": "Backend is working!",
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@auth_bp.route('/debug', methods=['POST'])
def debug_endpoint():
    """
    Debug endpoint to test registration data.
    """
    try:
        data = request.get_json()
        print(f"Debug - Received data: {data}")

        if not data:
            return format_error_response("No data provided")

        # Test validation
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()

        from app.utils.validators import validate_email, validate_password, validate_name, validate_phone

        validation_results = {
            'email': validate_email(email),
            'password': validate_password(password),
            'name': validate_name(name),
            'phone': validate_phone(phone)
        }

        print(f"Debug - Validation results: {validation_results}")

        return format_success_response(
            data={
                'received_data': data,
                'validation_results': validation_results
            },
            message="Debug data received"
        )

    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        return format_error_response(f"Debug error: {str(e)}")

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint.
    Automatically assigns role based on email domain.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        # Extract and validate required fields
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()

        # Validate inputs
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return format_error_response(email_error)

        password_valid, password_error = validate_password(password)
        if not password_valid:
            return format_error_response(password_error)

        name_valid, name_error = validate_name(name)
        if not name_valid:
            return format_error_response(name_error)

        phone_valid, phone_error = validate_phone(phone)
        if not phone_valid:
            return format_error_response(phone_error)

        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return format_error_response("Email already registered")

        # Create new user
        user = create_user(
            email=email,
            password=password,
            name=name,
            phone=phone if phone else None
        )

        # Log activity
        log_user_activity(user.id, 'user_registered', {
            'email': email,
            'role': user.role
        })

        # Log in the user
        login_user(user, remember=True)
        session.permanent = True

        return format_success_response(
            data=user.to_dict(),
            message="Registration successful",
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Registration failed. Please try again.")

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validate inputs
        if not email:
            return format_error_response("Email is required")

        if not password:
            return format_error_response("Password is required")

        # Authenticate user
        user = authenticate_user(email, password)
        if not user:
            return format_error_response("Invalid email or password")

        if not user.is_active:
            return format_error_response("Account is deactivated")

        # Log in the user
        login_user(user, remember=data.get('remember', False))
        session.permanent = True

        # Log activity
        log_user_activity(user.id, 'user_login', {
            'email': email,
            'role': user.role
        })

        return format_success_response(
            data=user.to_dict(),
            message="Login successful"
        )

    except Exception as e:
        return format_error_response("Login failed. Please try again.")

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    User logout endpoint.
    """
    try:
        user_id = current_user.id
        logout_user()

        # Log activity
        log_user_activity(user_id, 'user_logout')

        return format_success_response(message="Logout successful")

    except Exception as e:
        return format_error_response("Logout failed")

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Get current user profile.
    """
    try:
        return format_success_response(data=current_user.to_dict())

    except Exception as e:
        return format_error_response("Failed to retrieve profile")

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Update current user profile.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        # Extract fields
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()

        # Validate inputs
        if name:
            name_valid, name_error = validate_name(name)
            if not name_valid:
                return format_error_response(name_error)

        if phone:
            phone_valid, phone_error = validate_phone(phone)
            if not phone_valid:
                return format_error_response(phone_error)

        # Update user profile
        current_user.update_profile(name=name if name else None, phone=phone if phone else None)
        db.session.commit()

        # Log activity
        log_user_activity(current_user.id, 'profile_updated', {
            'fields_updated': list(filter(None, [name, phone]))
        })

        return format_success_response(
            data=current_user.to_dict(),
            message="Profile updated successfully"
        )

    except Exception as e:
        db.session.rollback()
        return format_error_response("Profile update failed")

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change user password.
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        # Validate inputs
        if not current_password:
            return format_error_response("Current password is required")

        if not new_password:
            return format_error_response("New password is required")

        # Verify current password
        if not current_user.check_password(current_password):
            return format_error_response("Current password is incorrect")

        # Validate new password
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return format_error_response(password_error)

        # Update password
        current_user.set_password(new_password)
        db.session.commit()

        # Log activity
        log_user_activity(current_user.id, 'password_changed')

        return format_success_response(message="Password changed successfully")

    except Exception as e:
        db.session.rollback()
        return format_error_response("Password change failed")

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """
    Check if user is authenticated.
    """
    try:
        if current_user.is_authenticated:
            return format_success_response(
                data={
                    'authenticated': True,
                    'user': current_user.to_dict()
                }
            )
        else:
            return format_success_response(
                data={
                    'authenticated': False,
                    'user': None
                }
            )

    except Exception as e:
        return format_error_response("Authentication check failed")

@auth_bp.route('/role-info', methods=['GET'])
@login_required
def get_role_info():
    """
    Get user role information and permissions.
    """
    try:
        role_info = {
            'role': current_user.role,
            'is_police': current_user.is_police(),
            'is_public': current_user.is_public(),
            'permissions': {
                'can_create_fir': current_user.is_police(),
                'can_search_legal': True,  # Both roles can search
                'can_write_complaint': True,  # Both roles can write complaints
                'can_access_police_portal': current_user.is_police(),
                'can_access_public_portal': True
            }
        }

        return format_success_response(data=role_info)

    except Exception as e:
        return format_error_response("Failed to retrieve role information")

@auth_bp.route('/delete-account', methods=['DELETE'])
@login_required
def delete_account():
    """
    Delete user account (with confirmation).
    """
    try:
        data = request.get_json()
        if not data:
            return format_error_response("No data provided")

        password = data.get('password', '')
        if not password:
            return format_error_response("Password is required to delete account")

        # Verify password
        if not current_user.check_password(password):
            return format_error_response("Password is incorrect")

        # Log activity before deletion
        user_id = current_user.id
        log_user_activity(user_id, 'account_deleted')

        # Delete user (this will cascade delete related records)
        db.session.delete(current_user)
        db.session.commit()

        # Logout user
        logout_user()

        return format_success_response(message="Account deleted successfully")

    except Exception as e:
        db.session.rollback()
        return format_error_response("Account deletion failed")