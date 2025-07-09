#!/usr/bin/env python
"""
Script to fix migration history issues related to the 'team' field error.
"""
import os
import sqlite3
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Get the database path from Django settings
from django.conf import settings
db_path = settings.DATABASES['default']['NAME']

print(f"Fixing migration history in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for problematic migrations
    cursor.execute("SELECT id, app, name FROM django_migrations WHERE app='strategy' ORDER BY id;")
    migrations = cursor.fetchall()
    
    print("Current strategy migrations:")
    for migration in migrations:
        print(f"  {migration[0]}: {migration[1]}.{migration[2]}")
    
    # Check if our fix migration exists
    cursor.execute("SELECT id FROM django_migrations WHERE app='strategy' AND name='0003_create_strategymilestone_sqlite';")
    if not cursor.fetchone():
        print("\nAdding missing migration record...")
        cursor.execute('''
        INSERT INTO django_migrations (app, name, applied) 
        VALUES ('strategy', '0003_create_strategymilestone_sqlite', datetime('now'));
        ''')
        print("Migration record added.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("\nMigration history fix completed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
