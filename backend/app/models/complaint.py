from datetime import datetime
from app import db
import json

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    formatted_complaint = db.Column(db.Text)
    ai_suggestions = db.Column(db.Text)  # JSON string of AI suggestions
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='draft')  # draft, formatted, archived
    evidence_files = db.Column(db.Text)  # JSON string of file references
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, original_text, **kwargs):
        self.user_id = user_id
        self.original_text = original_text
        self.category = kwargs.get('category')
        self.evidence_files = json.dumps(kwargs.get('evidence_files', []))

    def set_formatted_complaint(self, formatted_text, ai_suggestions=None):
        """Set the formatted complaint and AI suggestions."""
        self.formatted_complaint = formatted_text
        self.ai_suggestions = json.dumps(ai_suggestions) if ai_suggestions else None
        self.status = 'formatted'
        self.updated_at = datetime.utcnow()

    def get_ai_suggestions(self):
        """Get AI suggestions as dictionary."""
        if self.ai_suggestions:
            try:
                return json.loads(self.ai_suggestions)
            except json.JSONDecodeError:
                return {}
        return {}

    def get_evidence_files(self):
        """Get evidence files as list."""
        if self.evidence_files:
            try:
                return json.loads(self.evidence_files)
            except json.JSONDecodeError:
                return []
        return []

    def add_evidence_file(self, file_path):
        """Add an evidence file to the complaint."""
        current_files = self.get_evidence_files()
        current_files.append(file_path)
        self.evidence_files = json.dumps(current_files)

    def remove_evidence_file(self, file_path):
        """Remove an evidence file from the complaint."""
        current_files = self.get_evidence_files()
        if file_path in current_files:
            current_files.remove(file_path)
            self.evidence_files = json.dumps(current_files)

    def archive(self):
        """Archive the complaint."""
        self.status = 'archived'
        self.updated_at = datetime.utcnow()

    def is_draft(self):
        """Check if complaint is in draft status."""
        return self.status == 'draft'

    def is_formatted(self):
        """Check if complaint is formatted."""
        return self.status == 'formatted'

    def is_archived(self):
        """Check if complaint is archived."""
        return self.status == 'archived'

    def update_content(self, original_text=None, category=None):
        """Update complaint content."""
        if original_text:
            self.original_text = original_text
        if category:
            self.category = category
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_formatted=False):
        """Convert complaint object to dictionary."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'original_text': self.original_text,
            'category': self.category,
            'status': self.status,
            'evidence_files': self.get_evidence_files(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_formatted:
            result.update({
                'formatted_complaint': self.formatted_complaint,
                'ai_suggestions': self.get_ai_suggestions()
            })

        return result

    @staticmethod
    def get_by_user_id(user_id, status=None, page=1, per_page=20):
        """Get complaints by user ID with optional status filter."""
        query = Complaint.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Complaint.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def search_complaints(user_id, search_term, page=1, per_page=20):
        """Search complaints by content."""
        query = Complaint.query.filter_by(user_id=user_id).filter(
            (Complaint.original_text.contains(search_term)) |
            (Complaint.formatted_complaint.contains(search_term)) |
            (Complaint.category.contains(search_term))
        )
        return query.order_by(Complaint.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def __repr__(self):
        return f'<Complaint {self.id} - {self.status}>'

# Helper functions for complaint management
def create_complaint(user_id, original_text, **kwargs):
    """Create a new complaint."""
    try:
        complaint = Complaint(user_id=user_id, original_text=original_text, **kwargs)
        db.session.add(complaint)
        db.session.commit()
        return complaint
    except Exception as e:
        db.session.rollback()
        raise e

def get_complaint_by_id(complaint_id):
    """Get complaint by ID."""
    return Complaint.query.get(complaint_id)

def update_complaint(complaint_id, **kwargs):
    """Update complaint details."""
    complaint = Complaint.query.get(complaint_id)
    if complaint:
        complaint.update_content(**kwargs)
        db.session.commit()
    return complaint

def delete_complaint(complaint_id):
    """Delete complaint."""
    complaint = Complaint.query.get(complaint_id)
    if complaint:
        db.session.delete(complaint)
        db.session.commit()
        return True
    return False

def format_complaint_with_ai(complaint_id, formatted_text, ai_suggestions):
    """Update complaint with AI-formatted content."""
    complaint = Complaint.query.get(complaint_id)
    if complaint:
        complaint.set_formatted_complaint(formatted_text, ai_suggestions)
        db.session.commit()
    return complaint