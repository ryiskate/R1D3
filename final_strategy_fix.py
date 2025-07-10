#!/usr/bin/env python
"""
Final script to fix all remaining issues with the strategy tables.
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

print(f"Applying final fixes to strategy tables in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Add is_current column to strategy_strategyphase
    print("\n1. Adding is_current column to strategy_strategyphase...")
    
    # Check if the column exists
    cursor.execute("PRAGMA table_info(strategy_strategyphase);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'is_current' not in column_names:
        cursor.execute('''
        ALTER TABLE strategy_strategyphase 
        ADD COLUMN is_current bool NOT NULL DEFAULT 1;
        ''')
        print("  is_current column added successfully!")
    else:
        print("  is_current column already exists.")
    
    # 2. Check for any other missing columns that might be needed
    print("\n2. Checking for any other missing columns...")
    
    # Define all possible columns that might be needed
    additional_columns = {
        'slug': 'varchar(100)',
        'status': 'varchar(20)',
        'progress': 'integer',
        'start_date': 'date',
        'end_date': 'date',
        'is_completed': 'bool'
    }
    
    for col, type_ in additional_columns.items():
        if col not in column_names:
            print(f"  Adding '{col}' column...")
            try:
                default_value = "DEFAULT ''" if "varchar" in type_ else "DEFAULT 0"
                if "date" in type_:
                    default_value = "DEFAULT NULL"
                
                cursor.execute(f'''
                ALTER TABLE strategy_strategyphase 
                ADD COLUMN {col} {type_} {default_value};
                ''')
                print(f"  '{col}' column added successfully!")
            except sqlite3.OperationalError as e:
                print(f"  Error adding '{col}' column: {e}")
    
    # 3. Update existing records with default values
    print("\n3. Updating existing records with default values...")
    
    cursor.execute("UPDATE strategy_strategyphase SET is_current = 1 WHERE is_current IS NULL;")
    print("  Updated is_current with default value")
    
    # 4. Check if we have any records
    cursor.execute("SELECT COUNT(*) FROM strategy_strategyphase;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("\n4. No records found. Creating a sample phase...")
        
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
        
        # Now create a phase with all possible columns
        cursor.execute('''
        INSERT INTO strategy_strategyphase 
        (created_at, updated_at, name, description, order, vision_id, phase_type, 
         start_year, end_year, color, icon, is_active, is_current, slug, status, progress)
        VALUES (?, ?, 'Initial Phase', 'Getting started with our strategy.', 1, ?, 
                'standard', 2025, 2026, '#4e73df', 'fa-solid fa-flag', 1, 1, 
                'initial-phase', 'active', 0);
        ''', (datetime.now(), datetime.now(), vision_id[0]))
        
        print("  Sample phase created successfully!")
    
    # 5. Check and fix the projects_gamemilestone table
    print("\n5. Checking projects_gamemilestone table...")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects_gamemilestone';")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(projects_gamemilestone);")
        game_columns = [col[1] for col in cursor.fetchall()]
        
        if 'status' not in game_columns:
            print("  Adding missing 'status' column to projects_gamemilestone...")
            cursor.execute('''
            ALTER TABLE projects_gamemilestone 
            ADD COLUMN status varchar(20) NOT NULL DEFAULT 'not_started';
            ''')
            print("  Status column added successfully!")
        else:
            print("  Status column already exists in projects_gamemilestone.")
    else:
        print("  projects_gamemilestone table doesn't exist.")
    
    # 6. Make sure all migration records are properly set
    print("\n6. Ensuring migration records are properly set...")
    
    migrations_to_check = [
        ('strategy', '0001_initial'),
        ('strategy', '0002_remove_is_completed_add_status'),
        ('strategy', '0003_create_strategymilestone_table'),
        ('strategy', '0004_add_missing_columns')
    ]
    
    for app, name in migrations_to_check:
        cursor.execute("SELECT id FROM django_migrations WHERE app=? AND name=?;", (app, name))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO django_migrations (app, name, applied) 
            VALUES (?, ?, datetime('now'));
            ''', (app, name))
            print(f"  Added migration record: {app}.{name}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll fixes applied successfully!")
    print("Try accessing your strategy page now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
