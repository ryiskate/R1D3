#!/usr/bin/env python3
"""
Fix migration inconsistencies by faking migrations to match current database state
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def fix_migrations():
    """Fix migration history"""
    print("🔧 Fixing migration history...")
    
    try:
        # Fake all migrations to match current database state
        print("\n1. Faking all migrations...")
        call_command('migrate', '--fake', verbosity=2)
        
        print("\n✅ Migration history fixed!")
        print("\n📝 Now you can run: python manage.py makemigrations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try running: python manage.py migrate --fake")

if __name__ == "__main__":
    fix_migrations()
