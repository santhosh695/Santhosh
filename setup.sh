#!/bin/bash

# Law Mate - Setup Script
# This script sets up the entire Law Mate project

echo "🚀 Setting up Law Mate - AI-Powered Legal Companion"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Backend Setup
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit backend/.env file with your configuration"
fi

# Create uploads directory
mkdir -p uploads

echo "✅ Backend setup complete"
echo ""

# Frontend Setup
echo "📦 Setting up Frontend..."
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit frontend/.env file with your configuration"
fi

echo "✅ Frontend setup complete"
echo ""

# Go back to root directory
cd ..

echo "🎉 Setup completed successfully!"
echo ""
echo "Next Steps:"
echo "1. Start the backend server:"
echo "   cd backend && source venv/bin/activate && python run.py"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd frontend && npm start"
echo ""
echo "3. Open your browser and navigate to:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo ""
echo "4. Test with default accounts:"
echo "   Police: police@test.gov.in / Police123!"
echo "   Public: citizen@test.com / Public123!"
echo ""
echo "📚 For more information, see README.md"