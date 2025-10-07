#!/usr/bin/env python
"""
Script to fix login issues on PythonAnywhere production environment.
This script:
1. Checks for common production login issues
2. Verifies database connection
3. Checks for missing dependencies
4. Creates a superuser if needed
"""
import os
import sys
import django
import argparse
from getpass import getpass

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings
import importlib

User = get_user_model()

def check_database_connection():
    """Check if the database connection is working."""
    print("Checking database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("Database connection successful!")
                
                # Get database info
                db_settings = settings.DATABASES['default']
                db_engine = db_settings.get('ENGINE', 'unknown')
                db_name = db_settings.get('NAME', 'unknown')
                
                print(f"Database engine: {db_engine}")
                print(f"Database name: {db_name}")
                
                return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def check_required_packages():
    """Check if all required packages are installed."""
    required_packages = [
        'django',
        'mysqlclient',
        'dj_database_url',
        'python-dotenv',
        'django-allauth',
        'django-crispy-forms',
        'crispy-bootstrap5',
        'whitenoise',
    ]
    
    print("\nChecking required packages...")
    missing_packages = []
    
    for package in required_packages:
        package_name = package.replace('-', '_')
        try:
            importlib.import_module(package_name)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nMissing packages:")
        print(" ".join(missing_packages))
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_wsgi_file():
    """Check if the WSGI file is properly configured."""
    print("\nChecking WSGI file configuration...")
    
    # This is just a simulation since we can't directly access the PythonAnywhere WSGI file
    print("To properly check the WSGI file on PythonAnywhere:")
    print("1. Go to the PythonAnywhere dashboard")
    print("2. Click on the 'Web' tab")
    print("3. Click on 'WSGI configuration file' link")
    print("4. Verify it contains the following:")
    print("   - import os")
    print("   - import sys")
    print("   - from dotenv import load_dotenv")
    print("   - load_dotenv()")
    print("   - path = '/home/YOUR_USERNAME/R1D3'")
    print("   - if path not in sys.path: sys.path.append(path)")
    print("   - os.environ['DJANGO_SETTINGS_MODULE'] = 'company_system.settings'")
    print("   - from django.core.wsgi import get_wsgi_application")
    print("   - application = get_wsgi_application()")

def create_superuser(username, email, password):
    """Create a superuser with the given credentials."""
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        user = User.objects.get(username=username)
        
        # Make sure the user is a superuser and active
        if not user.is_superuser or not user.is_staff or not user.is_active:
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            print(f"Updated '{username}' to be an active superuser.")
        
        # Update password
        user.set_password(password)
        user.save()
        print(f"Password updated for '{username}'.")
        
        return user
    
    try:
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully!")
        return user
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return None

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\nChecking .env file...")
    
    env_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_path):
        print("WARNING: .env file not found!")
        print("Create a .env file with the following variables:")
        print("DATABASE_URL=mysql://username:password@hostname/database_name")
        print("DEBUG=False")
        print("ALLOWED_HOSTS=your-domain.pythonanywhere.com,localhost,127.0.0.1")
        return False
    
    print(".env file exists.")
    
    # Check if DATABASE_URL is set in environment
    if 'DATABASE_URL' not in os.environ:
        print("WARNING: DATABASE_URL not set in environment!")
        print("Make sure your WSGI file loads the .env file.")
        return False
    
    print("DATABASE_URL is set in environment.")
    return True

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Fix login issues on PythonAnywhere')
    parser.add_argument('--check-all', action='store_true', help='Run all checks')
    parser.add_argument('--check-db', action='store_true', help='Check database connection')
    parser.add_argument('--check-packages', action='store_true', help='Check required packages')
    parser.add_argument('--check-wsgi', action='store_true', help='Check WSGI configuration')
    parser.add_argument('--check-env', action='store_true', help='Check .env file')
    parser.add_argument('--create-admin', action='store_true', help='Create a superuser')
    parser.add_argument('--username', help='Username for superuser creation')
    parser.add_argument('--email', help='Email for superuser creation')
    parser.add_argument('--password', help='Password for superuser creation')
    
    args = parser.parse_args()
    
    if args.check_all or args.check_db:
        check_database_connection()
    
    if args.check_all or args.check_packages:
        check_required_packages()
    
    if args.check_all or args.check_wsgi:
        check_wsgi_file()
    
    if args.check_all or args.check_env:
        check_env_file()
    
    if args.create_admin:
        username = args.username
        email = args.email
        password = args.password
        
        if not username:
            username = input("Enter username for new superuser: ")
        
        if not email:
            email = input("Enter email for new superuser: ")
        
        if not password:
            password = getpass("Enter password for new superuser: ")
        
        create_superuser(username, email, password)

if __name__ == "__main__":
    main()
