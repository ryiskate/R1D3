#!/usr/bin/env python
"""
Quick Database Seeding Script for R1D3
Simple script to create admin user and basic setup
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth.models import User


def create_admin():
    """Create admin user with default credentials"""
    
    # Default admin credentials
    username = 'admin'
    email = 'admin@r1d3.com'
    password = 'admin123'  # Simple default password
    
    if User.objects.filter(username=username).exists():
        print(f"Admin user '{username}' already exists.")
        return
    
    # Create superuser
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Admin',
        last_name='User'
    )
    
    print(f"✅ Created admin user:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Email: {email}")
    print("⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")


if __name__ == '__main__':
    print("🚀 Creating admin user...")
    create_admin()
    print("✅ Done!")
