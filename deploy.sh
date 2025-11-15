#!/bin/bash

# Law Mate AI Legal Companion - Deployment Script
# This script deploys the application without any subscription features

echo "🚀 Deploying Law Mate AI Legal Companion..."

# Frontend deployment to Vercel
echo "📦 Building frontend..."
cd frontend

# Clean build
rm -rf build node_modules/.cache

# Install dependencies
npm install

# Build for production
npm run build

echo "✅ Frontend build completed"

cd ..

# Backend deployment (if using Render, the build happens automatically)
echo "🔧 Backend ready for Render deployment"

echo "🎉 Deployment ready!"
echo ""
echo "📋 Deployment Summary:"
echo "Frontend: Vercel (static build)"
echo "Backend: Render (Flask API)"
echo "No subscription or payment features included"
echo ""
echo "🌐 Project Links:"
echo "Frontend: https://law-mate-ai-legal-companion.vercel.app"
echo "Backend: https://law-mate-ai-legal-companion-backend.onrender.com"
echo ""
echo "📱 Features:"
echo "✅ Role-based authentication (Police/Citizen)"
echo "✅ FIR Management (Police only)"
echo "✅ Complaint Writing (Citizen only)"
echo "✅ Legal Search (All users)"
echo "✅ Multilingual support (EN, HI, TA, TE)"
echo "❌ No subscription plans"
echo "❌ No payment features"