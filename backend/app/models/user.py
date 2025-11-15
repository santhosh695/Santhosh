from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='public')  # 'police' or 'public'
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    firs = db.relationship('FIR', backref='user', lazy=True, cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, email, password, name, role=None, phone=None):
        self.email = email.lower()
        self.set_password(password)
        self.name = name
        self.role = role or self.determine_role_from_email(email)
        self.phone = phone

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def determine_role_from_email(self, email):
        """Determine user role based on email domain."""
        email = email.lower()
        police_domains = ['ips.gov.in', 'police.gov.in', 'gov.in']

        for domain in police_domains:
            if email.endswith(domain):
                return 'police'
        return 'public'

    def is_police(self):
        """Check if user is a police officer."""
        return self.role == 'police'

    def is_public(self):
        """Check if user is a public citizen."""
        return self.role == 'public'

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_profile(self, name=None, phone=None):
        """Update user profile information."""
        if name:
            self.name = name
        if phone:
            self.phone = phone
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f'<User {self.email}>'

# Additional helper functions for user management
def create_user(email, password, name, phone=None):
    """Create a new user with automatic role assignment."""
    try:
        user = User(email=email, password=password, name=name, phone=phone)
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def authenticate_user(email, password):
    """Authenticate user credentials."""
    user = User.query.filter_by(email=email.lower()).first()
    if user and user.check_password(password):
        return user
    return None

def get_user_by_email(email):
    """Get user by email address."""
    return User.query.filter_by(email=email.lower()).first()

def get_user_by_id(user_id):
    """Get user by ID."""
    return User.query.get(user_id)