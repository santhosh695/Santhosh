import os
from app import create_app, db
from app.models.user import User
from app.models.legal_act import LegalAct
from flask_migrate import Migrate

def create_initial_data():
    """Create initial legal data for testing."""
    # Sample IPC sections
    ipc_sections = [
        {
            'act_name': 'Indian Penal Code',
            'section_number': '302',
            'section_title': 'Punishment for murder',
            'description': 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
            'punishment': 'Death or imprisonment for life',
            'bailable': 'No',
            'cognizable': 'Yes',
            'court': 'Court of Session',
            'examples': [
                'Intentional killing of another person',
                'Causing death with the knowledge that it would likely result in death'
            ],
            'search_keywords': 'murder, killing, homicide, death',
            'category': 'IPC'
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '379',
            'section_title': 'Punishment for theft',
            'description': 'Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.',
            'punishment': 'Imprisonment up to 3 years, or fine, or both',
            'bailable': 'Yes',
            'cognizable': 'Yes',
            'court': 'Magistrate of the first class',
            'examples': [
                'Stealing jewelry from a house',
                'Taking someone\'s wallet without permission',
                'Shoplifting goods from a store'
            ],
            'search_keywords': 'theft, stealing, robbery, taking property',
            'category': 'IPC'
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '420',
            'section_title': 'Cheating and dishonestly inducing delivery of property',
            'description': 'Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.',
            'punishment': 'Imprisonment up to 7 years and fine',
            'bailable': 'No',
            'cognizable': 'Yes',
            'court': 'Magistrate of the first class',
            'examples': [
                'Fake investment schemes',
                'Online fraud scams',
                'Impersonation for financial gain'
            ],
            'search_keywords': 'cheating, fraud, deception, fake, scam',
            'category': 'IPC'
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '323',
            'section_title': 'Punishment for voluntarily causing hurt',
            'description': 'Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.',
            'punishment': 'Imprisonment up to 1 year, or fine up to Rs. 1000, or both',
            'bailable': 'Yes',
            'cognizable': 'Yes',
            'court': 'Any Magistrate',
            'examples': [
                'Physical assault causing minor injuries',
                'Punching someone during an argument',
                'Hitting someone with an object'
            ],
            'search_keywords': 'assault, hurt, violence, physical attack',
            'category': 'IPC'
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '506',
            'section_title': 'Punishment for criminal intimidation',
            'description': 'Whoever commits criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.',
            'punishment': 'Imprisonment up to 2 years, or fine, or both',
            'bailable': 'Yes',
            'cognizable': 'Yes',
            'court': 'Any Magistrate',
            'examples': [
                'Threatening someone with harm',
                'Blackmail for money',
                'Warning of consequences to force action'
            ],
            'search_keywords': 'threat, intimidation, blackmail, warning',
            'category': 'IPC'
        }
    ]

    # Sample CrPC sections
    crpc_sections = [
        {
            'act_name': 'Code of Criminal Procedure',
            'section_number': '154',
            'section_title': 'Information in cognizable cases',
            'description': 'Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the informant; and the substance thereof shall be entered in a book to be kept by such officer in such form as the State Government may prescribe in this behalf.',
            'punishment': 'Procedure for filing FIR',
            'bailable': 'Not Applicable',
            'cognizable': 'Yes',
            'court': 'Police Station',
            'examples': [
                'Filing FIR for theft',
                'Reporting murder to police',
                'Complaint about kidnapping'
            ],
            'search_keywords': 'FIR, cognizable, police, complaint, information',
            'category': 'CrPC'
        },
        {
            'act_name': 'Code of Criminal Procedure',
            'section_number': '173',
            'section_title': 'Report of police officer on completion of investigation',
            'description': 'Every investigation under this Chapter shall be completed without unnecessary delay. As soon as it is completed, the officer in charge of the police station shall forward to a Magistrate empowered to take cognizance of the offence on a police report, a report in the prescribed form stating the results of the investigation.',
            'punishment': 'Procedure for investigation report',
            'bailable': 'Not Applicable',
            'cognizable': 'Yes',
            'court': 'Magistrate',
            'examples': [
                'Submitting final investigation report',
                'Chargesheet filing in court',
                'Police investigation conclusion'
            ],
            'search_keywords': 'investigation, report, chargesheet, police report',
            'category': 'CrPC'
        }
    ]

    try:
        # Check if data already exists
        existing_ipc = LegalAct.query.filter_by(act_name='Indian Penal Code').count()
        existing_crpc = LegalAct.query.filter_by(act_name='Code of Criminal Procedure').count()

        if existing_ipc == 0:
            # Add IPC sections
            for section_data in ipc_sections:
                legal_act = LegalAct(**section_data)
                db.session.add(legal_act)
            print("Added IPC sections")

        if existing_crpc == 0:
            # Add CrPC sections
            for section_data in crpc_sections:
                legal_act = LegalAct(**section_data)
                db.session.add(legal_act)
            print("Added CrPC sections")

        db.session.commit()
        print("Initial legal data created successfully")

    except Exception as e:
        db.session.rollback()
        print(f"Error creating initial data: {str(e)}")

def init_database():
    """Initialize database with tables and initial data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created")

        # Create initial data
        create_initial_data()

        print("Database initialization complete")

if __name__ == '__main__':
    # Determine environment
    env = os.environ.get('FLASK_ENV', 'development')

    # Create app
    app = create_app(env)

    # Initialize database
    init_database()

    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))

    # Get host from environment or use default
    host = os.environ.get('HOST', '0.0.0.0')

    print(f"Starting Law Mate Backend in {env} mode")
    print(f"Server running on http://{host}:{port}")

    # Run the app
    app.run(host=host, port=port, debug=app.config.get('DEBUG', False))