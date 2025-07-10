#!/usr/bin/env python
"""
Script to add all missing columns to the strategy_strategyphase table.
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

print(f"Adding missing columns to strategy_strategyphase table in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist.")
        sys.exit(1)
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(strategy_strategyphase);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("Current StrategyPhase columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Define all columns that should exist in the table
    required_columns = {
        'id': 'integer',
        'created_at': 'datetime',
        'updated_at': 'datetime',
        'name': 'varchar(200)',
        'description': 'text',
        'order': 'integer',
        'vision_id': 'integer',
        'phase_type': 'varchar(50)',
        'start_year': 'integer',
        'end_year': 'integer',
        'color': 'varchar(20)',
        'icon': 'varchar(50)',
        'is_active': 'bool'
    }
    
    # Add missing columns
    missing_columns = {col: type_ for col, type_ in required_columns.items() if col not in column_names}
    
    if missing_columns:
        print("\nAdding missing columns:")
        for col, type_ in missing_columns.items():
            print(f"  Adding '{col}' column ({type_})...")
            
            # Default values for different column types
            default_value = ""
            if "integer" in type_:
                default_value = "DEFAULT 0"
            elif "varchar" in type_ or "text" in type_:
                default_value = "DEFAULT ''"
            elif "bool" in type_:
                default_value = "DEFAULT 0"
            elif "datetime" in type_ or "date" in type_:
                default_value = "DEFAULT NULL"
            
            try:
                cursor.execute(f'''
                ALTER TABLE strategy_strategyphase 
                ADD COLUMN {col} {type_} {default_value};
                ''')
                print(f"  '{col}' column added successfully!")
            except sqlite3.OperationalError as e:
                print(f"  Error adding '{col}' column: {e}")
    else:
        print("\nNo missing columns detected.")
    
    # Update existing records with sensible defaults
    print("\nUpdating existing records with default values...")
    
    # Set default values for specific columns
    updates = [
        ("UPDATE strategy_strategyphase SET phase_type = 'standard' WHERE phase_type IS NULL OR phase_type = '';", "phase_type"),
        ("UPDATE strategy_strategyphase SET start_year = 2025 WHERE start_year IS NULL OR start_year = 0;", "start_year"),
        ("UPDATE strategy_strategyphase SET end_year = 2026 WHERE end_year IS NULL OR end_year = 0;", "end_year"),
        ("UPDATE strategy_strategyphase SET color = '#4e73df' WHERE color IS NULL OR color = '';", "color"),
        ("UPDATE strategy_strategyphase SET icon = 'fa-solid fa-flag' WHERE icon IS NULL OR icon = '';", "icon"),
        ("UPDATE strategy_strategyphase SET is_active = 1 WHERE is_active IS NULL;", "is_active")
    ]
    
    for sql, col in updates:
        try:
            cursor.execute(sql)
            print(f"  Updated '{col}' with default values")
        except sqlite3.OperationalError as e:
            print(f"  Error updating '{col}': {e}")
    
    # Check if we have any records
    cursor.execute("SELECT COUNT(*) FROM strategy_strategyphase;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("\nNo records found. Creating a sample phase...")
        
        # First check if we have a vision
        cursor.execute("SELECT id FROM strategy_vision LIMIT 1;")
        vision_id = cursor.fetchone()
        
        if not vision_id:
            # Create a vision first
            cursor.execute('''
            INSERT INTO strategy_vision (created_at, updated_at, title, description, is_active)
            VALUES (?, ?, 'Company Vision', 'Our vision is to create innovative games and software.', 1);
            ''', (datetime.now(), datetime.now()))
            
            cursor.execute("SELECT id FROM strategy_vision ORDER BY id DESC LIMIT 1;")
            vision_id = cursor.fetchone()
        
        # Now create a phase
        cursor.execute('''
        INSERT INTO strategy_strategyphase 
        (created_at, updated_at, name, description, order, vision_id, phase_type, start_year, end_year, color, icon, is_active)
        VALUES (?, ?, 'Initial Phase', 'Getting started with our strategy.', 1, ?, 'standard', 2025, 2026, '#4e73df', 'fa-solid fa-flag', 1);
        ''', (datetime.now(), datetime.now(), vision_id[0]))
        
        print("  Sample phase created successfully!")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("\nStrategyPhase table fix completed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
