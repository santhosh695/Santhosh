# Law Mate - AI-Powered Legal Companion

A comprehensive web application serving as an AI-powered legal companion for both police officers and citizens in India.

## Features

- 🔐 **IPS Email Authentication** - Automatic police role detection
- 📝 **FIR Management** with AI-powered legal analysis
- 📋 **Complaint Writing** with AI formatting assistance
- 🔍 **Legal Research** (IPC, CrPC, and other Indian legal acts)
- 🌐 **Multilingual Support** (English, Hindi, Tamil, Telugu)
- 📄 **Document Generation** (PDF and Word export)
- 📎 **Evidence Upload** for files and documents
- 🎨 **Professional Legal UI** for police and citizens

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Start the backend server:
```bash
python run.py
```

The backend will be available at: http://localhost:5000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm start
```

The frontend will be available at: http://localhost:3000

## Default Test Accounts

### Police Account
- Email: `police@test.gov.in`
- Password: `Police123!`

### Public Account
- Email: `citizen@test.com`
- Password: `Public123!`

## Project Structure

```
Santhosh/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # AI, PDF, Translation services
│   │   └── utils/          # Helper functions
│   ├── uploads/            # File upload directory
│   ├── config.py           # Configuration
│   ├── run.py             # Application runner
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   └── pages/         # Page components
│   └── package.json       # Node.js dependencies
└── data/                  # Legal data repository
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### FIR Endpoints (Police Only)
- `GET /api/police/fir` - List FIRs
- `POST /api/police/fir` - Create FIR
- `PUT /api/police/fir/{id}` - Update FIR
- `DELETE /api/police/fir/{id}` - Delete FIR

### Legal Search Endpoints
- `GET /api/legal/search` - Search legal acts
- `GET /api/legal/section/{act}/{section}` - Get section details

### Complaint Endpoints (Public)
- `GET /api/public/complaint` - List complaints
- `POST /api/public/complaint` - Create complaint
- `POST /api/public/complaint/{id}/format` - Format with AI

## Security Features

- Password hashing with bcrypt
- Session-based authentication
- CSRF protection
- Input validation and sanitization
- File upload security
- SQL injection prevention

## License

This project is for educational and demonstration purposes.