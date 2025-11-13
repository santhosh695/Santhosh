from datetime import datetime
from app import db
import json

class FIR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    ai_analysis = db.Column(db.Text)
    suggested_sections = db.Column(db.Text)  # JSON string of legal sections
    structured_fir = db.Column(db.Text)  # JSON of FIR structure
    fir_type = db.Column(db.String(50))
    incident_date = db.Column(db.DateTime)
    incident_location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='draft')  # draft, submitted, archived
    evidence_files = db.Column(db.Text)  # JSON string of file references
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, complaint_text, **kwargs):
        self.user_id = user_id
        self.complaint_text = complaint_text
        self.fir_type = kwargs.get('fir_type')
        self.incident_date = kwargs.get('incident_date')
        self.incident_location = kwargs.get('incident_location')
        self.evidence_files = json.dumps(kwargs.get('evidence_files', []))

    def set_ai_analysis(self, analysis, sections, structured_data):
        """Set AI analysis results."""
        self.ai_analysis = analysis
        self.suggested_sections = json.dumps(sections) if sections else None
        self.structured_fir = json.dumps(structured_data) if structured_data else None

    def get_suggested_sections(self):
        """Get suggested sections as list."""
        if self.suggested_sections:
            try:
                return json.loads(self.suggested_sections)
            except json.JSONDecodeError:
                return []
        return []

    def get_structured_fir(self):
        """Get structured FIR as dictionary."""
        if self.structured_fir:
            try:
                return json.loads(self.structured_fir)
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
        """Add an evidence file to the FIR."""
        current_files = self.get_evidence_files()
        current_files.append(file_path)
        self.evidence_files = json.dumps(current_files)

    def remove_evidence_file(self, file_path):
        """Remove an evidence file from the FIR."""
        current_files = self.get_evidence_files()
        if file_path in current_files:
            current_files.remove(file_path)
            self.evidence_files = json.dumps(current_files)

    def submit(self):
        """Submit the FIR."""
        self.status = 'submitted'
        self.updated_at = datetime.utcnow()

    def archive(self):
        """Archive the FIR."""
        self.status = 'archived'
        self.updated_at = datetime.utcnow()

    def is_draft(self):
        """Check if FIR is in draft status."""
        return self.status == 'draft'

    def is_submitted(self):
        """Check if FIR is submitted."""
        return self.status == 'submitted'

    def is_archived(self):
        """Check if FIR is archived."""
        return self.status == 'archived'

    def update_content(self, complaint_text=None, fir_type=None, incident_date=None, incident_location=None):
        """Update FIR content."""
        if complaint_text:
            self.complaint_text = complaint_text
        if fir_type:
            self.fir_type = fir_type
        if incident_date:
            self.incident_date = incident_date
        if incident_location:
            self.incident_location = incident_location
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_ai_data=False):
        """Convert FIR object to dictionary."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'complaint_text': self.complaint_text,
            'fir_type': self.fir_type,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'incident_location': self.incident_location,
            'status': self.status,
            'evidence_files': self.get_evidence_files(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_ai_data:
            result.update({
                'ai_analysis': self.ai_analysis,
                'suggested_sections': self.get_suggested_sections(),
                'structured_fir': self.get_structured_fir()
            })

        return result

    @staticmethod
    def get_by_user_id(user_id, status=None, page=1, per_page=20):
        """Get FIRs by user ID with optional status filter."""
        query = FIR.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(FIR.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def search_firs(user_id, search_term, page=1, per_page=20):
        """Search FIRs by content."""
        query = FIR.query.filter_by(user_id=user_id).filter(
            (FIR.complaint_text.contains(search_term)) |
            (FIR.incident_location.contains(search_term)) |
            (FIR.fir_type.contains(search_term))
        )
        return query.order_by(FIR.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def __repr__(self):
        return f'<FIR {self.id} - {self.status}>'

# Helper functions for FIR management
def create_fir(user_id, complaint_text, **kwargs):
    """Create a new FIR."""
    try:
        fir = FIR(user_id=user_id, complaint_text=complaint_text, **kwargs)
        db.session.add(fir)
        db.session.commit()
        return fir
    except Exception as e:
        db.session.rollback()
        raise e

def get_fir_by_id(fir_id):
    """Get FIR by ID."""
    return FIR.query.get(fir_id)

def update_fir(fir_id, **kwargs):
    """Update FIR details."""
    fir = FIR.query.get(fir_id)
    if fir:
        fir.update_content(**kwargs)
        db.session.commit()
    return fir

def delete_fir(fir_id):
    """Delete FIR."""
    fir = FIR.query.get(fir_id)
    if fir:
        db.session.delete(fir)
        db.session.commit()
        return True
    return False