#!/usr/bin/env python
"""
Simplified script to add strategy phases without optional columns.
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

print(f"Adding basic strategy phases to database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist. Please run the fix_is_current_column_v2.py script first.")
        sys.exit(1)
    
    # Get the vision ID
    cursor.execute("SELECT id FROM strategy_vision LIMIT 1;")
    vision_id = cursor.fetchone()
    
    if not vision_id:
        # Create a vision first
        print("No vision found. Creating a new vision...")
        cursor.execute('''
        INSERT INTO strategy_vision (created_at, updated_at, title, description, is_active)
        VALUES (?, ?, 'Company Vision', 'Our vision is to create innovative games and software.', 1);
        ''', (datetime.now(), datetime.now()))
        
        cursor.execute("SELECT id FROM strategy_vision ORDER BY id DESC LIMIT 1;")
        vision_id = cursor.fetchone()
    
    # Check existing phases
    cursor.execute("SELECT name FROM strategy_strategyphase;")
    existing_phases = [row[0] for row in cursor.fetchall()]
    print(f"Existing phases: {existing_phases}")
    
    # Check available columns in the table
    cursor.execute("PRAGMA table_info(strategy_strategyphase);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("Available columns in strategy_strategyphase:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Define the phases to create with only essential columns
    phases = [
        {
            'name': 'Phase 1: Indie Game Development',
            'description': 'Building a foundation in game development through education and indie projects.',
            'order': 2,
            'phase_type': 'indie_dev',
            'start_year': 2025,
            'end_year': 2027,
            'is_current': 0,
            'status': 'not_started'
        },
        {
            'name': 'Phase 2: Arcade Machines',
            'description': 'Expanding into physical gaming experiences through arcade machine development.',
            'order': 3,
            'phase_type': 'arcade',
            'start_year': 2027,
            'end_year': 2029,
            'is_current': 0,
            'status': 'not_started'
        },
        {
            'name': 'Phase 3: Theme Park Attractions',
            'description': 'Creating immersive physical experiences through theme park attractions.',
            'order': 4,
            'phase_type': 'theme_park',
            'start_year': 2029,
            'end_year': 2031,
            'is_current': 0,
            'status': 'not_started'
        }
    ]
    
    # Add phases that don't exist yet
    for phase in phases:
        if phase['name'] not in existing_phases:
            print(f"Adding phase: {phase['name']}")
            
            # Construct the SQL dynamically based on available columns
            columns_to_insert = []
            values_to_insert = []
            placeholders = []
            
            # Always include these essential columns
            essential_columns = {
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'name': phase['name'],
                'description': phase['description'],
                '"order"': phase['order'],
                'vision_id': vision_id[0],
                'phase_type': phase['phase_type'],
                'start_year': phase['start_year'],
                'end_year': phase['end_year']
            }
            
            # Add these columns if they exist in the table
            optional_columns = {
                'is_current': phase.get('is_current', 0),
                'status': phase.get('status', 'not_started'),
                'is_active': 1
            }
            
            # Combine all columns that exist in the table
            for col_name, value in essential_columns.items():
                col_name_clean = col_name.replace('"', '')
                if col_name_clean in column_names:
                    columns_to_insert.append(col_name)
                    values_to_insert.append(value)
                    placeholders.append('?')
            
            for col_name, value in optional_columns.items():
                if col_name in column_names:
                    columns_to_insert.append(col_name)
                    values_to_insert.append(value)
                    placeholders.append('?')
            
            # Construct and execute the SQL
            sql = f'''
            INSERT INTO strategy_strategyphase 
            ({', '.join(columns_to_insert)})
            VALUES ({', '.join(placeholders)});
            '''
            
            cursor.execute(sql, values_to_insert)
            print(f"  Phase '{phase['name']}' added successfully!")
        else:
            print(f"Phase '{phase['name']}' already exists. Skipping.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll phases added successfully!")
    print("Try accessing your strategy page now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
