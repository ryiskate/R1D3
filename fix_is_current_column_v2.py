#!/usr/bin/env python
"""
Script to specifically fix the is_current column in the strategy_strategyphase table.
This script uses a direct approach to ensure the column is added correctly.
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

print(f"Fixing is_current column in strategy_strategyphase table in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist. Creating it...")
        
        # Create the table with all required columns
        cursor.execute('''
        CREATE TABLE strategy_strategyphase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            "order" INTEGER NOT NULL,
            vision_id INTEGER,
            phase_type VARCHAR(20) NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            is_current BOOLEAN NOT NULL DEFAULT 0,
            status VARCHAR(20) NOT NULL DEFAULT 'not_started'
        );
        ''')
        print("Table created successfully!")
        
        # Create a sample phase
        cursor.execute('''
        INSERT INTO strategy_strategyphase 
        (created_at, updated_at, name, description, "order", phase_type, start_year, end_year, is_current, status)
        VALUES (?, ?, 'Initial Phase', 'Getting started with our strategy.', 1, 
                'indie_dev', 2025, 2026, 1, 'in_progress');
        ''', (datetime.now(), datetime.now()))
        
        print("Sample phase created successfully!")
    else:
        # Table exists, check if is_current column exists
        cursor.execute("PRAGMA table_info(strategy_strategyphase);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("Current StrategyPhase columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        if 'is_current' not in column_names:
            print("\nThe is_current column is missing. Creating a new table with all columns...")
            
            # SQLite doesn't support adding NOT NULL columns with default values directly
            # So we need to create a new table and copy the data
            
            # 1. Rename the existing table
            cursor.execute("ALTER TABLE strategy_strategyphase RENAME TO strategy_strategyphase_old;")
            
            # 2. Create a new table with all required columns - note the quotes around "order"
            cursor.execute('''
            CREATE TABLE strategy_strategyphase (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                "order" INTEGER NOT NULL,
                vision_id INTEGER,
                phase_type VARCHAR(20) NOT NULL,
                start_year INTEGER NOT NULL,
                end_year INTEGER NOT NULL,
                is_current BOOLEAN NOT NULL DEFAULT 0,
                status VARCHAR(20) NOT NULL DEFAULT 'not_started',
                color VARCHAR(20),
                icon VARCHAR(50),
                is_active BOOLEAN DEFAULT 1
            );
            ''')
            
            # 3. Copy data from old table to new table - note the quotes around "order"
            cursor.execute('''
            INSERT INTO strategy_strategyphase 
            (id, created_at, updated_at, name, description, "order", vision_id, phase_type, 
             start_year, end_year, is_current, status, color, icon, is_active)
            SELECT 
                id, created_at, updated_at, name, description, "order", vision_id, phase_type, 
                start_year, end_year, 
                CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END as is_current,
                status, color, icon, is_active
            FROM strategy_strategyphase_old;
            ''')
            
            # 4. Drop the old table
            cursor.execute("DROP TABLE strategy_strategyphase_old;")
            
            print("Table recreated with is_current column successfully!")
            
            # 5. Check if we have any records
            cursor.execute("SELECT COUNT(*) FROM strategy_strategyphase;")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("No records found. Creating a sample phase...")
                
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
                
                cursor.execute('''
                INSERT INTO strategy_strategyphase 
                (created_at, updated_at, name, description, "order", vision_id, phase_type, 
                 start_year, end_year, is_current, status, color, icon, is_active)
                VALUES (?, ?, 'Initial Phase', 'Getting started with our strategy.', 1, ?, 
                        'indie_dev', 2025, 2026, 1, 'in_progress', '#4e73df', 'fa-solid fa-flag', 1);
                ''', (datetime.now(), datetime.now(), vision_id[0]))
                
                print("Sample phase created successfully!")
        else:
            print("\nThe is_current column already exists. No action needed.")
    
    # Verify the table structure
    cursor.execute("PRAGMA table_info(strategy_strategyphase);")
    columns = cursor.fetchall()
    
    print("\nVerified StrategyPhase columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nFix completed successfully!")
    print("Try accessing your strategy page now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
