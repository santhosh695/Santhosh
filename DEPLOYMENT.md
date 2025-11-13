# Law Mate - Deployment Guide

This guide provides step-by-step instructions for deploying the Law Mate application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Domain Configuration](#domain-configuration)
6. [Environment Variables](#environment-variables)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

- Git repository with the Law Mate code
- GitHub/GitLab/Bitbucket account
- Render account (for backend deployment)
- Vercel account (for frontend deployment)
- Domain name (optional)

## Local Development Setup

Before deploying to production, ensure the application works locally:

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd law-mate
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Start Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

### 4. Start Frontend
```bash
# In another terminal
cd frontend
npm start
```

### 5. Test Application
- Visit http://localhost:3000
- Test registration, login, FIR creation, legal search
- Verify all features work correctly

## Backend Deployment (Render)

Render provides free hosting for Python web applications.

### 1. Prepare Repository

Ensure your repository is pushed to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Create Render Account

1. Sign up at [render.com](https://render.com)
2. Connect your GitHub account

### 3. Create New Web Service

1. Click "New +" → "Web Service"
2. Select your repository
3. Configure service settings:

**Basic Settings:**
- Name: `law-mate-backend`
- Environment: `Python 3`
- Region: Choose nearest region
- Branch: `main`

**Build Settings:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`

**Advanced Settings:**
- Health Check Path: `/api/auth/check-auth`
- Auto-Deploy: Yes (for main branch)

### 4. Environment Variables

Add these environment variables in Render dashboard:

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
DATABASE_URL=sqlite:///law_mate.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-custom-domain.com
AI_SERVICE_PROVIDER=mock
```

### 5. Deploy

Click "Create Web Service" to deploy. Render will automatically:
- Build your application
- Install dependencies
- Start the server
- Provide a public URL

## Frontend Deployment (Vercel)

Vercel provides free hosting for React applications.

### 1. Create Vercel Account

1. Sign up at [vercel.com](https://vercel.com)
2. Connect your GitHub account

### 2. Import Project

1. Click "New Project"
2. Select your repository
3. Configure project settings:

**Project Settings:**
- Project Name: `law-mate-frontend`
- Framework Preset: `Create React App`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm install`

### 3. Environment Variables

Add these environment variables in Vercel dashboard:

```env
REACT_APP_API_URL=https://your-backend-domain.onrender.com/api
REACT_APP_NAME=Law Mate
REACT_APP_DESCRIPTION=AI-Powered Legal Companion
REACT_APP_ENABLE_AI=true
REACT_APP_ENABLE_TRANSLATION=true
```

### 4. Deploy

Click "Deploy" to deploy. Vercel will automatically:
- Build your React application
- Deploy to global CDN
- Provide a public URL

## Domain Configuration

### Custom Domain Setup

1. **Backend (Render):**
   - Go to your service settings
   - Click "Custom Domains"
   - Add your domain (e.g., `api.lawmate.in`)
   - Update DNS records as instructed

2. **Frontend (Vercel):**
   - Go to project settings
   - Click "Domains"
   - Add your domain (e.g., `lawmate.in`)
   - Update DNS records as instructed

### DNS Configuration

For both domains, add these DNS records:

```
Type: A
Name: @
Value: Vercel's IP addresses (provided in dashboard)

Type: CNAME
Name: api
Value: your-backend-domain.onrender.com
```

## Environment Variables

### Production Environment Variables

#### Backend (.env)
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=sqlite:///law_mate.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800
CORS_ORIGINS=https://lawmate.in,https://api.lawmate.in
AI_SERVICE_PROVIDER=mock
WTF_CSRF_ENABLED=true
```

#### Frontend (.env)
```env
REACT_APP_API_URL=https://api.lawmate.in/api
REACT_APP_NAME=Law Mate
REACT_APP_VERSION=1.0.0
REACT_APP_ENABLE_AI=true
REACT_APP_ENABLE_TRANSLATION=true
REACT_APP_DEFAULT_LANGUAGE=en
```

## Monitoring and Maintenance

### 1. Health Checks

Monitor application health using the endpoints:
- Backend: `https://api.lawmate.in/api/auth/check-auth`
- Frontend: `https://lawmate.in`

### 2. Error Monitoring

Consider adding error monitoring:
- **Sentry**: For error tracking
- **UptimeRobot**: For uptime monitoring

### 3. Backup Strategy

- Database: SQLite file backup to cloud storage
- User uploads: Regular backup to cloud storage
- Code: Version controlled in Git

### 4. SSL Certificates

Both Render and Vercel provide automatic SSL certificates for HTTPS.

### 5. Performance Optimization

- Enable caching on both backend and frontend
- Use CDN for static assets
- Monitor loading times and optimize

## Troubleshooting

### Common Issues

1. **Backend Deployment Fails**
   - Check requirements.txt for correct dependencies
   - Verify start command is correct
   - Check environment variables

2. **Frontend Cannot Connect to Backend**
   - Verify CORS origins include frontend domain
   - Check API URL in frontend environment variables
   - Ensure backend is running and accessible

3. **File Upload Issues**
   - Check upload directory permissions
   - Verify file size limits
   - Ensure sufficient disk space

4. **Database Issues**
   - Check database file permissions
   - Verify database migrations
   - Monitor database size

### Debug Commands

```bash
# Check backend logs (Render)
# Go to Render dashboard → Service → Logs

# Check frontend deployment (Vercel)
# Go to Vercel dashboard → Project → Logs

# Test API endpoints
curl https://api.lawmate.in/api/auth/check-auth

# Test frontend deployment
curl https://lawmate.in
```

## Security Considerations

1. **API Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Validate all inputs
   - Use CSRF protection

2. **Database Security**
   - Use parameterized queries
   - Implement proper access controls
   - Regular backups

3. **File Upload Security**
   - Validate file types
   - Scan for malware
   - Implement size limits
   - Store files securely

4. **Environment Security**
   - Never commit secrets to Git
   - Use strong secrets
   - Rotate keys periodically
   - Monitor access logs

## Scaling Considerations

When scaling beyond free tiers:

1. **Backend Scaling**
   - Move to PostgreSQL database
   - Use Redis for caching
   - Implement load balancing
   - Add CDN for static files

2. **Frontend Scaling**
   - Implement code splitting
   - Use lazy loading
   - Optimize bundle size
   - Add service workers

## Support

For deployment issues:
1. Check platform documentation (Render/Vercel)
2. Review application logs
3. Test locally first
4. Check community forums
5. Open GitHub issues for bugs

---

## Summary

Following this guide will deploy the Law Mate application with:
- ✅ Secure HTTPS access
- ✅ Custom domain support
- ✅ Automated deployments
- ✅ Environment management
- ✅ Monitoring capabilities
- ✅ Free hosting on both platforms

The deployed application will be accessible at your custom domain with all features fully functional.