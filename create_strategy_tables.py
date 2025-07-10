#!/usr/bin/env python
"""
Script to create all missing strategy tables in the database.
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

print(f"Creating missing strategy tables in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check and create strategy_strategyphase table
    print("\n1. Checking strategy_strategyphase table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("  Creating strategy_strategyphase table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "strategy_strategyphase" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "name" varchar(200) NOT NULL,
            "description" text NULL,
            "order" integer NULL,
            "vision_id" integer NOT NULL REFERENCES "strategy_vision" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        ''')
        print("  Table created successfully!")
    else:
        print("  Table already exists.")
    
    # 2. Check and create strategy_strategymilestone table
    print("\n2. Checking strategy_strategymilestone table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
    if not cursor.fetchone():
        print("  Creating strategy_strategymilestone table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "strategy_strategymilestone" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "title" varchar(200) NOT NULL,
            "description" text NULL,
            "target_date" date NULL,
            "status" varchar(20) NOT NULL,
            "completion_date" date NULL,
            "order" integer NULL,
            "phase_id" integer NOT NULL REFERENCES "strategy_strategyphase" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        ''')
        print("  Table created successfully!")
    else:
        print("  Table already exists.")
    
    # 3. Check and create strategy_vision table
    print("\n3. Checking strategy_vision table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_vision';")
    if not cursor.fetchone():
        print("  Creating strategy_vision table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "strategy_vision" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "title" varchar(200) NOT NULL,
            "description" text NULL,
            "is_active" bool NOT NULL
        );
        ''')
        print("  Table created successfully!")
    else:
        print("  Table already exists.")
    
    # 4. Check and create strategy_goal table
    print("\n4. Checking strategy_goal table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_goal';")
    if not cursor.fetchone():
        print("  Creating strategy_goal table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "strategy_goal" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "title" varchar(200) NOT NULL,
            "description" text NULL,
            "order" integer NULL,
            "vision_id" integer NOT NULL REFERENCES "strategy_vision" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        ''')
        print("  Table created successfully!")
    else:
        print("  Table already exists.")
    
    # 5. Check and create strategy_objective table
    print("\n5. Checking strategy_objective table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_objective';")
    if not cursor.fetchone():
        print("  Creating strategy_objective table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "strategy_objective" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "title" varchar(200) NOT NULL,
            "description" text NULL,
            "order" integer NULL,
            "goal_id" integer NOT NULL REFERENCES "strategy_goal" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        ''')
        print("  Table created successfully!")
    else:
        print("  Table already exists.")
    
    # 6. Check and create strategy_keyresult table
    print("\n6. Checking strategy_keyresult table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_keyresult';")
    if not cursor.fetchone():
        print("  Creating strategy_keyresult table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "strategy_keyresult" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "created_at" datetime NOT NULL,
            "updated_at" datetime NOT NULL,
            "title" varchar(200) NOT NULL,
            "description" text NULL,
            "target_value" real NULL,
            "current_value" real NULL,
            "order" integer NULL,
            "objective_id" integer NOT NULL REFERENCES "strategy_objective" ("id") DEFERRABLE INITIALLY DEFERRED
        );
        ''')
        print("  Table created successfully!")
    else:
        print("  Table already exists.")
    
    # 7. Create a sample vision record if none exists
    print("\n7. Creating sample vision record if needed...")
    cursor.execute("SELECT COUNT(*) FROM strategy_vision;")
    if cursor.fetchone()[0] == 0:
        print("  No vision records found. Creating a sample vision...")
        cursor.execute('''
        INSERT INTO strategy_vision (created_at, updated_at, title, description, is_active)
        VALUES (datetime('now'), datetime('now'), 'Company Vision', 'Our vision is to create innovative games and software.', 1);
        ''')
        
        # Get the vision ID
        cursor.execute("SELECT id FROM strategy_vision ORDER BY id DESC LIMIT 1;")
        vision_id = cursor.fetchone()[0]
        
        # Create a sample phase
        cursor.execute('''
        INSERT INTO strategy_strategyphase (created_at, updated_at, name, description, order, vision_id)
        VALUES (datetime('now'), datetime('now'), 'Initial Phase', 'Getting started with our strategy.', 1, ?);
        ''', (vision_id,))
        
        print("  Sample vision and phase created successfully!")
    else:
        print("  Vision records already exist.")
    
    # 8. Fix projects_gamemilestone table
    print("\n8. Fixing projects_gamemilestone table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects_gamemilestone';")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(projects_gamemilestone);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'status' not in columns:
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
    
    # 9. Update migration records
    print("\n9. Updating migration records...")
    
    # Check and add migration records for strategy app
    migrations_to_add = [
        ('strategy', '0001_initial'),
        ('strategy', '0002_remove_is_completed_add_status'),
        ('strategy', '0003_create_strategymilestone_table')
    ]
    
    for app, name in migrations_to_add:
        cursor.execute("SELECT id FROM django_migrations WHERE app=? AND name=?;", (app, name))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO django_migrations (app, name, applied) 
            VALUES (?, ?, datetime('now'));
            ''', (app, name))
            print(f"  Added migration record: {app}.{name}")
        else:
            print(f"  Migration record already exists: {app}.{name}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll strategy tables created and fixed successfully!")
    print("Try accessing your strategy page now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
