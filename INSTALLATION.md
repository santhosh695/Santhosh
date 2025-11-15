# Law Mate - Installation Guide

## 🚀 Quick Start Guide

### Option 1: Automated Setup (Recommended)

Run the setup script to automatically configure the entire project:

```bash
# Clone the repository
git clone <repository-url>
cd Santhosh

# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python3 -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Start Backend**
```bash
python run.py
```

#### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start Frontend**
```bash
npm start
```

## 📋 Prerequisites

### Required Software

1. **Python 3.9+**
   - Download from [python.org](https://python.org)
   - Verify installation: `python --version`

2. **Node.js 16+**
   - Download from [nodejs.org](https://nodejs.org)
   - Verify installation: `node --version`

3. **Git**
   - Download from [git-scm.com](https://git-scm.com)
   - Verify installation: `git --version`

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🔧 Configuration

### Backend Configuration (.env)

Edit `backend/.env`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
PORT=5000

# Database
DATABASE_URL=sqlite:///law_mate.db

# File Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800

# CORS
CORS_ORIGINS=http://localhost:3000

# AI Services (Optional)
AI_SERVICE_PROVIDER=mock
GOOGLE_TRANSLATE_API_KEY=your-api-key
HUGGINGFACE_API_KEY=your-api-key
```

### Frontend Configuration (.env)

Edit `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_NAME=Law Mate
REACT_APP_ENABLE_AI=true
REACT_APP_ENABLE_TRANSLATION=true
```

## 🧪 Testing the Installation

### 1. Verify Backend

Test backend API:
```bash
curl http://localhost:5000/api/auth/check-auth
```

Expected response:
```json
{
  "success": true,
  "data": {
    "authenticated": false,
    "user": null
  }
}
```

### 2. Verify Frontend

Open browser to: http://localhost:3000

You should see the Law Mate login page.

### 3. Test Authentication

**Create Police Account:**
- Email: `police@test.gov.in`
- Password: `Police123!`
- Name: `Test Police Officer`

**Create Public Account:**
- Email: `citizen@test.com`
- Password: `Public123!`
- Name: `Test Citizen`

### 4. Test Features

**Police Portal:**
1. Login with police account
2. Create a new FIR
3. Test legal search
4. Download FIR as PDF

**Public Portal:**
1. Login with public account
2. Create a complaint
3. Format complaint with AI
4. Search legal acts

## 📁 File Structure After Installation

```
Santhosh/
├── backend/
│   ├── venv/                 # Python virtual environment
│   ├── uploads/              # File upload directory
│   ├── law_mate.db          # SQLite database
│   ├── app/                  # Application code
│   ├── config.py             # Configuration
│   ├── run.py               # Application runner
│   ├── requirements.txt     # Dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── node_modules/         # Node.js dependencies
│   ├── build/               # Production build (created later)
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   ├── package.json         # Dependencies
│   └── .env                 # Environment variables
├── data/                    # Legal data files
├── setup.sh                 # Setup script
├── README.md               # Documentation
├── INSTALLATION.md         # This file
├── DEPLOYMENT.md           # Deployment guide
└── .gitignore              # Git ignore rules
```

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues

**Error: `ModuleNotFoundError`**
```bash
# Activate virtual environment
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: Port already in use**
```bash
# Kill process on port 5000
sudo lsof -ti:5000 | xargs kill

# Or change port in .env
PORT=5001
```

**Error: Database issues**
```bash
# Delete database and restart
rm backend/law_mate.db
python run.py
```

#### Frontend Issues

**Error: `npm install` fails**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: Cannot connect to backend**
```bash
# Check backend is running
curl http://localhost:5000/api/auth/check-auth

# Check API URL in frontend/.env
REACT_APP_API_URL=http://localhost:5000/api
```

**Error: Build fails**
```bash
# Clear build directory
rm -rf build

# Rebuild
npm run build
```

### Verification Commands

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check virtual environment
ls backend/venv

# Check database file
ls backend/law_mate.db

# Check node modules
ls frontend/node_modules

# Test backend health
curl http://localhost:5000/api/auth/check-auth

# Test frontend
curl http://localhost:3000
```

## 🚀 Next Steps

After successful installation:

1. **Explore Features**: Test all features described in README.md
2. **Customize**: Modify colors, logos, and content
3. **Add Data**: Import your legal data if needed
4. **Deploy**: Follow DEPLOYMENT.md for production deployment
5. **Monitor**: Set up logging and monitoring

## 📞 Support

If you encounter issues:

1. Check this installation guide
2. Review README.md for features
3. Check DEPLOYMENT.md for deployment issues
4. Open an issue on GitHub with:
   - Operating system
   - Python and Node.js versions
   - Error messages
   - Steps to reproduce

## 🎉 Success!

If you've completed all steps and the application is running, congratulations! You have successfully installed Law Mate - AI-Powered Legal Companion.

The application should now be fully functional with:
- ✅ User authentication and role-based access
- ✅ FIR management for police officers
- ✅ Complaint writing for citizens
- ✅ Legal search capabilities
- ✅ AI-powered analysis
- ✅ Multilingual support
- ✅ File upload and PDF generation

Enjoy using the application!