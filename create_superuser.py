#!/usr/bin/env python
"""
Script to create a Django superuser non-interactively.
This is useful for creating an admin user in environments like PythonAnywhere.

Usage:
    python create_superuser.py username email password
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_superuser(username, email, password):
    """
    Create a superuser with the given username, email, and password.
    """
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        return False
    
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return False

def main():
    """Main function to run the script."""
    if len(sys.argv) != 4:
        print("Usage: python create_superuser.py username email password")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_superuser(username, email, password)

if __name__ == "__main__":
    main()
