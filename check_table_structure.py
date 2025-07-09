#!/usr/bin/env python
"""
Script to check the structure of the strategy_strategymilestone table
and verify it has all the required columns.
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

print(f"Checking table structure in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(strategy_strategymilestone);")
    columns = cursor.fetchall()
    
    print("Table structure for 'strategy_strategymilestone':")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if all required columns exist
    required_columns = ['id', 'created_at', 'updated_at', 'title', 'description', 
                        'target_date', 'status', 'completion_date', 'order', 'phase_id']
    
    existing_columns = [col[1] for col in columns]
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    if missing_columns:
        print(f"\nMissing columns: {', '.join(missing_columns)}")
        
        # Add missing columns
        for col in missing_columns:
            if col == 'status':
                cursor.execute('''
                ALTER TABLE strategy_strategymilestone 
                ADD COLUMN status varchar(20) NOT NULL DEFAULT 'not_started';
                ''')
                print(f"Added missing column: {col}")
            elif col == 'order':
                cursor.execute('''
                ALTER TABLE strategy_strategymilestone 
                ADD COLUMN "order" integer NOT NULL DEFAULT 0;
                ''')
                print(f"Added missing column: {col}")
            elif col == 'completion_date':
                cursor.execute('''
                ALTER TABLE strategy_strategymilestone 
                ADD COLUMN completion_date date NULL;
                ''')
                print(f"Added missing column: {col}")
            # Add other columns as needed
    else:
        print("\nAll required columns exist.")
    
    # Check for any data in the table
    cursor.execute("SELECT COUNT(*) FROM strategy_strategymilestone;")
    count = cursor.fetchone()[0]
    print(f"\nNumber of records in table: {count}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("\nCheck completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
