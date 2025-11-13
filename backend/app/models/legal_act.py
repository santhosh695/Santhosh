from app import db
import json

class LegalAct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    act_name = db.Column(db.String(200), nullable=False)
    section_number = db.Column(db.String(20), nullable=False)
    section_title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    punishment = db.Column(db.Text)
    bailable = db.Column(db.String(10))  # Yes/No
    cognizable = db.Column(db.String(10))  # Yes/No
    court = db.Column(db.String(50))
    examples = db.Column(db.Text)  # JSON string of examples
    search_keywords = db.Column(db.String(500))  # Comma-separated keywords
    category = db.Column(db.String(50))  # IPC, CrPC, etc.

    def __init__(self, act_name, section_number, section_title, description, **kwargs):
        self.act_name = act_name
        self.section_number = section_number
        self.section_title = section_title
        self.description = description
        self.punishment = kwargs.get('punishment')
        self.bailable = kwargs.get('bailable')
        self.cognizable = kwargs.get('cognizable')
        self.court = kwargs.get('court')
        self.examples = json.dumps(kwargs.get('examples', []))
        self.search_keywords = kwargs.get('search_keywords', '')
        self.category = kwargs.get('category', 'Other')

    def get_examples(self):
        """Get examples as list."""
        if self.examples:
            try:
                return json.loads(self.examples)
            except json.JSONDecodeError:
                return []
        return []

    def set_examples(self, examples_list):
        """Set examples from list."""
        self.examples = json.dumps(examples_list)

    def get_keywords(self):
        """Get keywords as list."""
        if self.search_keywords:
            return [kw.strip() for kw in self.search_keywords.split(',') if kw.strip()]
        return []

    def set_keywords(self, keywords_list):
        """Set keywords from list."""
        self.search_keywords = ', '.join(keywords_list)

    def add_keyword(self, keyword):
        """Add a single keyword."""
        keywords = self.get_keywords()
        if keyword not in keywords:
            keywords.append(keyword)
            self.set_keywords(keywords)

    def is_bailable(self):
        """Check if offense is bailable."""
        return self.bailable and self.bailable.lower() == 'yes'

    def is_cognizable(self):
        """Check if offense is cognizable."""
        return self.cognizable and self.cognizable.lower() == 'yes'

    def to_dict(self):
        """Convert legal act to dictionary."""
        return {
            'id': self.id,
            'act_name': self.act_name,
            'section_number': self.section_number,
            'section_title': self.section_title,
            'description': self.description,
            'punishment': self.punishment,
            'bailable': self.bailable,
            'cognizable': self.cognizable,
            'court': self.court,
            'examples': self.get_examples(),
            'keywords': self.get_keywords(),
            'category': self.category
        }

    @staticmethod
    def search_by_keyword(keyword, limit=20):
        """Search legal acts by keyword."""
        return LegalAct.query.filter(
            (LegalAct.section_title.contains(keyword)) |
            (LegalAct.description.contains(keyword)) |
            (LegalAct.search_keywords.contains(keyword)) |
            (LegalAct.section_number.contains(keyword))
        ).limit(limit).all()

    @staticmethod
    def search_by_section(section_number, limit=10):
        """Search legal acts by section number."""
        return LegalAct.query.filter(
            LegalAct.section_number.contains(section_number)
        ).limit(limit).all()

    @staticmethod
    def get_by_category(category, limit=50):
        """Get legal acts by category."""
        return LegalAct.query.filter_by(category=category).limit(limit).all()

    @staticmethod
    def get_by_act(act_name, limit=100):
        """Get all sections of a specific act."""
        return LegalAct.query.filter_by(act_name=act_name).order_by(
            LegalAct.section_number
        ).limit(limit).all()

    @staticmethod
    def advanced_search(query, category=None, act_name=None, bailable=None, cognizable=None, limit=20):
        """Advanced search with multiple filters."""
        db_query = LegalAct.query

        if query:
            db_query = db_query.filter(
                (LegalAct.section_title.contains(query)) |
                (LegalAct.description.contains(query)) |
                (LegalAct.search_keywords.contains(query))
            )

        if category:
            db_query = db_query.filter_by(category=category)

        if act_name:
            db_query = db_query.filter_by(act_name=act_name)

        if bailable is not None:
            db_query = db_query.filter_by(bailable='Yes' if bailable else 'No')

        if cognizable is not None:
            db_query = db_query.filter_by(cognizable='Yes' if cognizable else 'No')

        return db_query.limit(limit).all()

    def __repr__(self):
        return f'<LegalAct {self.act_name} - {self.section_number}>'

# Helper functions for legal act management
def create_legal_act(act_name, section_number, section_title, description, **kwargs):
    """Create a new legal act."""
    try:
        legal_act = LegalAct(
            act_name=act_name,
            section_number=section_number,
            section_title=section_title,
            description=description,
            **kwargs
        )
        db.session.add(legal_act)
        db.session.commit()
        return legal_act
    except Exception as e:
        db.session.rollback()
        raise e

def get_legal_act_by_id(legal_act_id):
    """Get legal act by ID."""
    return LegalAct.query.get(legal_act_id)

def get_legal_act_by_section(act_name, section_number):
    """Get specific legal act section."""
    return LegalAct.query.filter_by(
        act_name=act_name,
        section_number=section_number
    ).first()

def bulk_create_legal_acts(legal_acts_data):
    """Bulk create legal acts from data."""
    try:
        legal_acts = []
        for act_data in legal_acts_data:
            legal_act = LegalAct(**act_data)
            legal_acts.append(legal_act)

        db.session.bulk_save_objects(legal_acts)
        db.session.commit()
        return legal_acts
    except Exception as e:
        db.session.rollback()
        raise e