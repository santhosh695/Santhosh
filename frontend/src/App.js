import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, ProtectedRoute, PublicRoute } from './hooks/useAuth';
import { useTranslation } from 'react-i18next';
import { ToastContainer } from 'react-toastify';

// Import pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import FIRPage from './pages/FIRPage';
import LegalSearchPage from './pages/LegalSearchPage';
import ComplaintPage from './pages/ComplaintPage';

import 'react-toastify/dist/ReactToastify.css';

function App() {
  const { i18n } = useTranslation();

  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/register"
              element={
                <PublicRoute>
                  <RegisterPage />
                </PublicRoute>
              }
            />

            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Navigate to="/dashboard" replace />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/fir"
              element={
                <ProtectedRoute>
                  <FIRPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/legal-search"
              element={
                <ProtectedRoute>
                  <LegalSearchPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/complaint"
              element={
                <ProtectedRoute>
                  <ComplaintPage />
                </ProtectedRoute>
              }
            />
          </Routes>

          {/* Toast Notifications */}
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;