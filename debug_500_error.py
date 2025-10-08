#!/usr/bin/env python
"""
Script to debug 500 errors on PythonAnywhere login page.
This script:
1. Checks error logs
2. Tests database connection
3. Verifies authentication configuration
4. Provides detailed diagnostics
"""
import os
import sys
import django
import argparse
import traceback

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings
from django.core.management import call_command
import importlib

User = get_user_model()

def check_error_logs():
    """Check PythonAnywhere error logs."""
    print("\n=== How to Check Error Logs ===")
    print("1. Go to the PythonAnywhere dashboard")
    print("2. Click on the 'Web' tab")
    print("3. Scroll down to the 'Logs' section")
    print("4. Click on 'Error log' to see the most recent errors")
    print("\nCommon error patterns to look for:")
    print("- ImportError: Missing packages")
    print("- OperationalError: Database connection issues")
    print("- TemplateDoesNotExist: Missing template files")
    print("- AttributeError: Code compatibility issues")

def test_database_connection():
    """Test database connection."""
    print("\n=== Testing Database Connection ===")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✓ Database connection successful!")
                
                # Get database info
                db_settings = settings.DATABASES['default']
                db_engine = db_settings.get('ENGINE', 'unknown')
                db_name = db_settings.get('NAME', 'unknown')
                
                print(f"Database engine: {db_engine}")
                print(f"Database name: {db_name}")
                
                return True
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        print("\nPossible solutions:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Verify database credentials")
        print("3. Make sure the database exists")
        print("4. Check if mysqlclient package is installed")
        return False

def check_auth_configuration():
    """Check authentication configuration."""
    print("\n=== Checking Authentication Configuration ===")
    
    # Check if django-allauth is installed
    try:
        import allauth
        print("✓ django-allauth is installed")
    except ImportError:
        print("✗ django-allauth is NOT installed")
        print("  Run: pip install django-allauth")
    
    # Check if AUTHENTICATION_BACKENDS is properly configured
    auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
    if 'allauth.account.auth_backends.AuthenticationBackend' in auth_backends:
        print("✓ allauth authentication backend is configured")
    else:
        print("✗ allauth authentication backend is NOT configured")
        print("  Add 'allauth.account.auth_backends.AuthenticationBackend' to AUTHENTICATION_BACKENDS in settings.py")
    
    # Check if allauth is in INSTALLED_APPS
    installed_apps = getattr(settings, 'INSTALLED_APPS', [])
    allauth_apps = ['allauth', 'allauth.account', 'allauth.socialaccount']
    missing_apps = [app for app in allauth_apps if app not in installed_apps]
    
    if not missing_apps:
        print("✓ allauth apps are in INSTALLED_APPS")
    else:
        print(f"✗ Some allauth apps are missing from INSTALLED_APPS: {', '.join(missing_apps)}")
    
    # Check login settings
    print(f"LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Not set')}")
    print(f"LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Not set')}")

def check_templates():
    """Check if login templates exist."""
    print("\n=== Checking Login Templates ===")
    
    # Check for account templates
    template_dirs = []
    for template_config in settings.TEMPLATES:
        template_dirs.extend(template_config.get('DIRS', []))
    
    template_paths = [
        'account/login.html',
        'account/signup.html',
    ]
    
    for template_path in template_paths:
        found = False
        for template_dir in template_dirs:
            full_path = os.path.join(template_dir, template_path)
            if os.path.exists(full_path):
                print(f"✓ Template found: {template_path}")
                found = True
                break
        
        if not found:
            print(f"✗ Template not found: {template_path}")
            print(f"  Create this template or check template directories configuration")

def check_users():
    """Check if there are any users in the database."""
    print("\n=== Checking User Accounts ===")
    try:
        user_count = User.objects.count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        
        print(f"Total users in database: {user_count}")
        print(f"Superusers in database: {superuser_count}")
        
        if user_count == 0:
            print("✗ No users found in the database!")
            print("  Create a superuser with: python manage.py createsuperuser")
            return False
        
        if superuser_count == 0:
            print("✗ No superusers found in the database!")
            print("  Create a superuser with: python manage.py createsuperuser")
            return False
        
        # List all superusers
        superusers = User.objects.filter(is_superuser=True)
        print("\nSuperusers:")
        for user in superusers:
            print(f"- Username: {user.username}, Email: {user.email}, Active: {user.is_active}")
        
        return True
    except Exception as e:
        print(f"✗ Error checking users: {e}")
        return False

def check_migrations():
    """Check if migrations are applied."""
    print("\n=== Checking Migrations ===")
    try:
        call_command('showmigrations', no_color=True)
        return True
    except Exception as e:
        print(f"✗ Error checking migrations: {e}")
        return False

def check_dotenv_loading():
    """Check if .env file is being loaded."""
    print("\n=== Checking .env File Loading ===")
    
    # Check if python-dotenv is installed
    try:
        import dotenv
        print("✓ python-dotenv is installed")
    except ImportError:
        print("✗ python-dotenv is NOT installed")
        print("  Run: pip install python-dotenv")
        return False
    
    # Check if .env file exists
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        print("✓ .env file exists")
    else:
        print("✗ .env file does NOT exist")
        print("  Create a .env file with DATABASE_URL and other settings")
        return False
    
    # Check if DATABASE_URL is set in environment
    if 'DATABASE_URL' in os.environ:
        print("✓ DATABASE_URL is set in environment")
    else:
        print("✗ DATABASE_URL is NOT set in environment")
        print("  Make sure your WSGI file loads the .env file with:")
        print("  from dotenv import load_dotenv")
        print("  load_dotenv()")
        return False
    
    return True

def fix_common_issues():
    """Provide solutions for common issues."""
    print("\n=== Common Solutions for 500 Errors ===")
    
    print("1. Missing packages:")
    print("   pip install mysqlclient python-dotenv django-allauth django-crispy-forms")
    
    print("\n2. Database connection issues:")
    print("   - Check your DATABASE_URL format in .env file")
    print("   - Verify database credentials")
    print("   - Make sure the database exists")
    
    print("\n3. WSGI configuration:")
    print("   - Make sure your WSGI file loads the .env file")
    print("   - Check the path to your project in the WSGI file")
    
    print("\n4. Missing users:")
    print("   - Create a superuser with: python manage.py createsuperuser")
    
    print("\n5. Template issues:")
    print("   - Check if login templates exist")
    print("   - Verify template directories configuration")
    
    print("\n6. Migration issues:")
    print("   - Run migrations with: python manage.py migrate")

def main():
    """Main function to run all checks."""
    parser = argparse.ArgumentParser(description='Debug 500 errors on PythonAnywhere')
    parser.add_argument('--check-all', action='store_true', help='Run all checks')
    parser.add_argument('--check-db', action='store_true', help='Check database connection')
    parser.add_argument('--check-auth', action='store_true', help='Check authentication configuration')
    parser.add_argument('--check-templates', action='store_true', help='Check login templates')
    parser.add_argument('--check-users', action='store_true', help='Check user accounts')
    parser.add_argument('--check-migrations', action='store_true', help='Check migrations')
    parser.add_argument('--check-dotenv', action='store_true', help='Check .env file loading')
    parser.add_argument('--fix', action='store_true', help='Show common solutions')
    
    args = parser.parse_args()
    
    # If no specific checks are requested, run all checks
    if not any(vars(args).values()):
        args.check_all = True
    
    print("=== R1D3 500 Error Debugging Tool ===")
    
    check_error_logs()
    
    if args.check_all or args.check_db:
        test_database_connection()
    
    if args.check_all or args.check_auth:
        check_auth_configuration()
    
    if args.check_all or args.check_templates:
        check_templates()
    
    if args.check_all or args.check_users:
        check_users()
    
    if args.check_all or args.check_migrations:
        check_migrations()
    
    if args.check_all or args.check_dotenv:
        check_dotenv_loading()
    
    if args.check_all or args.fix:
        fix_common_issues()

if __name__ == "__main__":
    main()
