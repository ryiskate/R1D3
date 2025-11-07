#!/usr/bin/env python3
"""
Check existing users in the database
Usage: python check_users.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth.models import User

def check_users():
    """Display all users in the database"""
    users = User.objects.all()
    
    if not users:
        print("❌ No users found in database!")
        print("\n💡 Create a superuser with: python manage.py createsuperuser")
        return
    
    print(f"👥 Found {users.count()} user(s) in database:\n")
    
    for user in users:
        status = []
        if user.is_superuser:
            status.append("🔑 Superuser")
        if user.is_staff:
            status.append("👔 Staff")
        if user.is_active:
            status.append("✅ Active")
        else:
            status.append("❌ Inactive")
        
        print(f"Username: {user.username}")
        print(f"Email: {user.email or 'Not set'}")
        print(f"Status: {' | '.join(status)}")
        print(f"Last login: {user.last_login or 'Never'}")
        print("-" * 50)

if __name__ == "__main__":
    check_users()
