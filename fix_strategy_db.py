#!/usr/bin/env python
"""
Script to directly create the missing strategy_strategymilestone table in the database.
Run this script on your production server to fix the 500 error.
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

print(f"Attempting to fix database at: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
    if cursor.fetchone():
        print("Table 'strategy_strategymilestone' already exists.")
    else:
        # Create the missing table
        print("Creating 'strategy_strategymilestone' table...")
        cursor.execute('''
        CREATE TABLE "strategy_strategymilestone" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "title" varchar(200) NOT NULL,
            "description" text NOT NULL,
            "target_date" date NULL,
            "status" varchar(20) NOT NULL,
            "completion_date" date NULL,
            "order" integer NOT NULL,
            "phase_id" integer NOT NULL,
            FOREIGN KEY ("phase_id") REFERENCES "strategy_strategyphase" ("id")
        );
        ''')
        
        # Check if the migration record already exists
        cursor.execute("SELECT id FROM django_migrations WHERE app='strategy' AND name='0003_create_strategymilestone_sqlite';")
        if not cursor.fetchone():
            print("Adding migration record...")
            cursor.execute('''
            INSERT INTO django_migrations (app, name, applied) 
            VALUES ('strategy', '0003_create_strategymilestone_sqlite', datetime('now'));
            ''')
        
        print("Table created successfully!")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database fix completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
