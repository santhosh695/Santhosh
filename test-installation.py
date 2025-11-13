#!/usr/bin/env python3
"""
Law Mate - Installation Test Script

This script tests whether the installation was successful
by checking imports, dependencies, and basic functionality.
"""

import sys
import os

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_success(message):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")

def test_python_version():
    """Test Python version."""
    print_header("Python Version Test")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} is too old (requires 3.9+)")
        return False

def test_backend_dependencies():
    """Test backend dependencies."""
    print_header("Backend Dependencies Test")

    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'werkzeug'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print_success(f"{module} is installed")
        except ImportError:
            print_error(f"{module} is missing")
            missing_modules.append(module)

    if missing_modules:
        print_info(f"Missing modules: {', '.join(missing_modules)}")
        print_info("Run: pip install -r backend/requirements.txt")
        return False

    return True

def test_backend_imports():
    """Test backend imports."""
    print_header("Backend Import Test")

    # Add backend to path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    try:
        # Test basic imports
        from app import create_app
        print_success("Flask app import successful")

        from app.models import User, FIR, Complaint, LegalAct
        print_success("Model imports successful")

        from app.routes import auth_bp, fir_bp, legal_bp, public_bp
        print_success("Route imports successful")

        from app.services import ai_service, pdf_service, translation_service
        print_success("Service imports successful")

        return True

    except ImportError as e:
        print_error(f"Import error: {e}")
        return False

def test_backend_app_creation():
    """Test backend app creation."""
    print_header("Backend App Creation Test")

    try:
        from app import create_app

        # Create test app
        app = create_app('testing')
        print_success("Flask app created successfully")

        # Test app context
        with app.app_context():
            print_success("App context works")

        return True

    except Exception as e:
        print_error(f"App creation failed: {e}")
        return False

def test_frontend_dependencies():
    """Test frontend dependencies."""
    print_header("Frontend Dependencies Test")

    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
    package_json_path = os.path.join(frontend_path, 'package.json')
    node_modules_path = os.path.join(frontend_path, 'node_modules')

    if not os.path.exists(package_json_path):
        print_error("package.json not found")
        return False

    print_success("package.json exists")

    if not os.path.exists(node_modules_path):
        print_error("node_modules directory not found")
        print_info("Run: cd frontend && npm install")
        return False

    print_success("node_modules directory exists")

    # Check for key dependencies in package.json
    with open(package_json_path, 'r') as f:
        content = f.read()

    key_deps = ['react', 'react-dom', 'react-router-dom', 'axios']
    for dep in key_deps:
        if dep in content:
            print_success(f"{dep} found in package.json")
        else:
            print_error(f"{dep} missing from package.json")
            return False

    return True

def test_file_structure():
    """Test file structure."""
    print_header("File Structure Test")

    required_dirs = [
        'backend',
        'frontend',
        'backend/app',
        'backend/app/models',
        'backend/app/routes',
        'backend/app/services',
        'frontend/src',
        'frontend/public'
    ]

    required_files = [
        'backend/requirements.txt',
        'backend/run.py',
        'backend/config.py',
        'frontend/package.json',
        'frontend/src/index.js',
        'README.md'
    ]

    all_good = True

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_good = False

    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_good = False

    return all_good

def test_environment_files():
    """Test environment files."""
    print_header("Environment Files Test")

    env_files = [
        ('backend/.env', 'backend/.env.example'),
        ('frontend/.env', 'frontend/.env.example')
    ]

    all_good = True

    for env_file, env_example in env_files:
        if os.path.exists(env_file):
            print_success(f"{env_file} exists")
        elif os.path.exists(env_example):
            print_info(f"{env_example} exists (copy to {env_file})")
        else:
            print_error(f"Both {env_file} and {env_example} missing")
            all_good = False

    return all_good

def main():
    """Main test function."""
    print_header("Law Mate Installation Test")
    print_info("Testing your Law Mate installation...")

    tests = [
        ("Python Version", test_python_version),
        ("File Structure", test_file_structure),
        ("Environment Files", test_environment_files),
        ("Backend Dependencies", test_backend_dependencies),
        ("Backend Imports", test_backend_imports),
        ("Backend App Creation", test_backend_app_creation),
        ("Frontend Dependencies", test_frontend_dependencies),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print_error(f"{test_name} test failed with exception: {e}")

    print_header("Test Results")
    print_info(f"Tests passed: {passed}/{total}")

    if passed == total:
        print_success("🎉 All tests passed! Installation is successful!")
        print_info("\nNext steps:")
        print_info("1. Start backend: cd backend && python run.py")
        print_info("2. Start frontend: cd frontend && npm start")
        print_info("3. Open browser to http://localhost:3000")
        return 0
    else:
        print_error("Some tests failed. Please fix the issues above.")
        print_info("\nFor help, see INSTALLATION.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())