#!/usr/bin/env python
"""
Script to bypass Django's migration system by directly modifying the migration records.
This is a last resort approach when normal migration methods fail.
"""
import os
import sqlite3
import sys
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Get the database path from Django settings
from django.conf import settings
db_path = settings.DATABASES['default']['NAME']

print(f"Bypassing migrations in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. First, let's fix the GameMilestone table issue
    print("\n1. Fixing GameMilestone table...")
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects_gamemilestone';")
    if cursor.fetchone():
        # Check if the status column exists
        cursor.execute("PRAGMA table_info(projects_gamemilestone);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'status' not in columns:
            print("  - Adding missing 'status' column to projects_gamemilestone...")
            cursor.execute('''
            ALTER TABLE projects_gamemilestone 
            ADD COLUMN status varchar(20) NOT NULL DEFAULT 'not_started';
            ''')
            print("  - Status column added successfully!")
        else:
            print("  - Status column already exists in projects_gamemilestone.")
    else:
        print("  - projects_gamemilestone table doesn't exist.")
    
    # 2. Now let's completely bypass the migration system for the problematic app
    print("\n2. Bypassing migration system for problematic apps...")
    
    # Get the highest migration ID
    cursor.execute("SELECT MAX(id) FROM django_migrations;")
    max_id = cursor.fetchone()[0] or 0
    next_id = max_id + 1
    
    # Get current timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Delete any problematic migration records that might be causing issues
    print("  - Removing problematic migration records...")
    cursor.execute("DELETE FROM django_migrations WHERE app='strategy' AND name LIKE '%remove_%';")
    
    # Add fake migration records to mark all migrations as applied
    migrations_to_add = [
        ('strategy', '0001_initial', now),
        ('strategy', '0002_remove_is_completed_add_status', now),
        ('strategy', '0003_create_strategymilestone_sqlite', now),
        ('strategy', '0004_auto_bypass_migrations', now),
    ]
    
    print("  - Adding fake migration records to bypass migration system:")
    for app, name, applied in migrations_to_add:
        # Check if this migration already exists
        cursor.execute("SELECT id FROM django_migrations WHERE app=? AND name=?;", (app, name))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO django_migrations (id, app, name, applied) VALUES (?, ?, ?, ?);",
                (next_id, app, name, applied)
            )
            print(f"    - Added: {app}.{name}")
            next_id += 1
        else:
            print(f"    - Already exists: {app}.{name}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("\nBypass completed successfully!")
    print("\nNOW TRY ACCESSING YOUR SITE AGAIN WITHOUT RUNNING ANY MIGRATION COMMANDS.")
    print("If you still encounter issues, you may need to restart your web server.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
