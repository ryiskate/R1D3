#!/usr/bin/env python
"""
Script to add the missing phase_type column to the strategy_strategyphase table.
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

print(f"Adding missing phase_type column to strategy_strategyphase table in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist.")
        sys.exit(1)
    
    # Check if the phase_type column exists
    cursor.execute("PRAGMA table_info(strategy_strategyphase);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("Current StrategyPhase columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Add the phase_type column if it doesn't exist
    if 'phase_type' not in column_names:
        print("\nAdding missing 'phase_type' column...")
        cursor.execute('''
        ALTER TABLE strategy_strategyphase 
        ADD COLUMN phase_type varchar(50) NOT NULL DEFAULT 'standard';
        ''')
        print("Phase_type column added successfully!")
        
        # Update existing records to have a valid phase_type
        cursor.execute('''
        UPDATE strategy_strategyphase
        SET phase_type = 'standard'
        WHERE phase_type IS NULL;
        ''')
        print("Updated existing records with default phase_type value.")
    else:
        print("\nThe 'phase_type' column already exists.")
    
    # Let's check if there are any other missing columns by comparing with the model definition
    required_columns = {
        'id': 'integer',
        'created_at': 'datetime',
        'updated_at': 'datetime',
        'name': 'varchar',
        'description': 'text',
        'order': 'integer',
        'vision_id': 'integer',
        'phase_type': 'varchar'
    }
    
    missing_columns = {col: type_ for col, type_ in required_columns.items() if col not in column_names}
    
    if missing_columns:
        print("\nOther missing columns detected:")
        for col, type_ in missing_columns.items():
            print(f"  Adding missing '{col}' column ({type_})...")
            cursor.execute(f'''
            ALTER TABLE strategy_strategyphase 
            ADD COLUMN {col} {type_};
            ''')
            print(f"  {col} column added successfully!")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("\nStrategyPhase table fix completed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
