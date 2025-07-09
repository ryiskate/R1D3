#!/usr/bin/env python
"""
Script to fix the missing status column in projects_gamemilestone table.
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

print(f"Fixing GameMilestone table in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects_gamemilestone';")
    if not cursor.fetchone():
        print("Table 'projects_gamemilestone' does not exist.")
        sys.exit(1)
    
    # Check if the status column exists
    cursor.execute("PRAGMA table_info(projects_gamemilestone);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("Current GameMilestone columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Add the status column if it doesn't exist
    if 'status' not in column_names:
        print("\nAdding missing 'status' column...")
        cursor.execute('''
        ALTER TABLE projects_gamemilestone 
        ADD COLUMN status varchar(20) NOT NULL DEFAULT 'not_started';
        ''')
        print("Status column added successfully!")
    else:
        print("\nThe 'status' column already exists.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("\nGameMilestone table fix completed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
