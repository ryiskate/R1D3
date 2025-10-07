#!/usr/bin/env python
"""
Script to debug login issues on PythonAnywhere for the R1D3 platform.
This script:
1. Checks if there are any users in the database
2. Verifies authentication settings
3. Tests login functionality
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

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

User = get_user_model()

def check_users():
    """Check if there are any users in the database."""
    user_count = User.objects.count()
    superuser_count = User.objects.filter(is_superuser=True).count()
    
    print(f"Total users in database: {user_count}")
    print(f"Superusers in database: {superuser_count}")
    
    if user_count == 0:
        print("WARNING: No users found in the database!")
        return False
    
    if superuser_count == 0:
        print("WARNING: No superusers found in the database!")
        return False
    
    # List all superusers
    superusers = User.objects.filter(is_superuser=True)
    print("\nSuperusers:")
    for user in superusers:
        print(f"- Username: {user.username}, Email: {user.email}")
    
    return True

def check_auth_settings():
    """Check authentication settings."""
    print("\nAuthentication Settings:")
    print(f"AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")
    print(f"ACCOUNT_ADAPTER: {getattr(settings, 'ACCOUNT_ADAPTER', 'Default')}")
    print(f"LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Default')}")
    print(f"LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Default')}")

def test_login(username, password):
    """Test login with provided credentials."""
    print(f"\nTesting login for user: {username}")
    user = authenticate(username=username, password=password)
    
    if user is not None:
        print("Authentication successful!")
        print(f"User: {user.username}")
        print(f"Is superuser: {user.is_superuser}")
        print(f"Is staff: {user.is_staff}")
        print(f"Is active: {user.is_active}")
        return True
    else:
        print("Authentication failed!")
        
        # Check if user exists
        try:
            user_obj = User.objects.get(username=username)
            print(f"User '{username}' exists in the database.")
            print(f"Is active: {user_obj.is_active}")
            
            if not user_obj.is_active:
                print("WARNING: User account is inactive!")
        except User.DoesNotExist:
            print(f"User '{username}' does not exist in the database.")
        
        return False

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

def reset_user_password(username, password):
    """Reset password for an existing user."""
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Password reset successful for user '{username}'.")
        return True
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")
        return False
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Debug login issues on PythonAnywhere')
    parser.add_argument('--check', action='store_true', help='Check users and authentication settings')
    parser.add_argument('--test-login', action='store_true', help='Test login with credentials')
    parser.add_argument('--create-admin', action='store_true', help='Create a superuser')
    parser.add_argument('--reset-password', action='store_true', help='Reset password for a user')
    parser.add_argument('--username', help='Username for login test or superuser creation')
    parser.add_argument('--email', help='Email for superuser creation')
    parser.add_argument('--password', help='Password for login test or superuser creation')
    
    args = parser.parse_args()
    
    if args.check:
        check_users()
        check_auth_settings()
    
    if args.test_login:
        username = args.username
        password = args.password
        
        if not username:
            username = input("Enter username: ")
        
        if not password:
            password = getpass("Enter password: ")
        
        test_login(username, password)
    
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
    
    if args.reset_password:
        username = args.username
        password = args.password
        
        if not username:
            username = input("Enter username: ")
        
        if not password:
            password = getpass("Enter new password: ")
        
        reset_user_password(username, password)

if __name__ == "__main__":
    main()
