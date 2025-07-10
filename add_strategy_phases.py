#!/usr/bin/env python
"""
Script to add all three strategy phases to the database.
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

print(f"Adding strategy phases to database: {db_path}")

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
    
    # Define the phases to create
    phases = [
        {
            'name': 'Initial Phase',
            'description': 'Getting started with our strategy.',
            'order': 1,
            'phase_type': 'indie_dev',
            'start_year': 2025,
            'end_year': 2026,
            'is_current': 1,
            'status': 'in_progress',
            'color': '#4e73df',
            'icon': 'fa-solid fa-flag'
        },
        {
            'name': 'Phase 1: Indie Game Development',
            'description': 'Building a foundation in game development through education and indie projects.',
            'order': 2,
            'phase_type': 'indie_dev',
            'start_year': 2025,
            'end_year': 2027,
            'is_current': 0,
            'status': 'not_started',
            'color': '#4e73df',
            'icon': 'fa-solid fa-gamepad'
        },
        {
            'name': 'Phase 2: Arcade Machines',
            'description': 'Expanding into physical gaming experiences through arcade machine development.',
            'order': 3,
            'phase_type': 'arcade',
            'start_year': 2027,
            'end_year': 2029,
            'is_current': 0,
            'status': 'not_started',
            'color': '#f6c23e',
            'icon': 'fa-solid fa-arcade-machine'
        },
        {
            'name': 'Phase 3: Theme Park Attractions',
            'description': 'Creating immersive physical experiences through theme park attractions.',
            'order': 4,
            'phase_type': 'theme_park',
            'start_year': 2029,
            'end_year': 2031,
            'is_current': 0,
            'status': 'not_started',
            'color': '#1cc88a',
            'icon': 'fa-solid fa-ferris-wheel'
        }
    ]
    
    # Add phases that don't exist yet
    for phase in phases:
        if phase['name'] not in existing_phases:
            print(f"Adding phase: {phase['name']}")
            cursor.execute('''
            INSERT INTO strategy_strategyphase 
            (created_at, updated_at, name, description, "order", vision_id, phase_type, 
             start_year, end_year, is_current, status, color, icon, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
            ''', (
                datetime.now(), 
                datetime.now(), 
                phase['name'], 
                phase['description'], 
                phase['order'], 
                vision_id[0], 
                phase['phase_type'], 
                phase['start_year'], 
                phase['end_year'], 
                phase['is_current'], 
                phase['status'], 
                phase['color'], 
                phase['icon']
            ))
        else:
            print(f"Phase '{phase['name']}' already exists. Skipping.")
    
    # Add some sample milestones for each phase
    print("\nAdding sample milestones...")
    
    # Get phase IDs
    cursor.execute("SELECT id, name FROM strategy_strategyphase;")
    phases = cursor.fetchall()
    phase_ids = {name: id for id, name in phases}
    
    # Check existing milestones
    cursor.execute("SELECT title FROM strategy_strategymilestone;")
    existing_milestones = [row[0] for row in cursor.fetchall()]
    
    # Define milestones for each phase
    milestones = [
        # Initial Phase
        {
            'title': 'Define Company Strategy',
            'description': 'Create a comprehensive strategy document outlining our growth plan.',
            'phase_id': phase_ids.get('Initial Phase'),
            'target_date': '2025-12-31',
            'status': 'completed',
            'completion_date': '2025-07-01',
            'order': 1
        },
        # Phase 1
        {
            'title': 'Hardware Integration Research',
            'description': 'Complete research on hardware integration for arcade machines.',
            'phase_id': phase_ids.get('Phase 1: Indie Game Development'),
            'target_date': '2026-06-30',
            'status': 'completed',
            'completion_date': '2026-05-15',
            'order': 1
        },
        {
            'title': 'Prototype First Arcade Cabinet',
            'description': 'Build a prototype arcade cabinet with custom controls.',
            'phase_id': phase_ids.get('Phase 1: Indie Game Development'),
            'target_date': '2026-12-31',
            'status': 'in_progress',
            'completion_date': None,
            'order': 2
        },
        # Phase 2
        {
            'title': 'Develop Arcade-Specific Game',
            'description': 'Create a game specifically designed for arcade machines.',
            'phase_id': phase_ids.get('Phase 2: Arcade Machines'),
            'target_date': '2027-09-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 1
        },
        {
            'title': 'Open First Arcade Location',
            'description': 'Establish our first physical arcade location featuring our machines.',
            'phase_id': phase_ids.get('Phase 2: Arcade Machines'),
            'target_date': '2028-06-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 2
        },
        # Phase 3
        {
            'title': 'Attraction Prototype',
            'description': 'Develop a prototype for an immersive 3D attraction.',
            'phase_id': phase_ids.get('Phase 3: Theme Park Attractions'),
            'target_date': '2029-12-31',
            'status': 'not_started',
            'completion_date': None,
            'order': 1
        },
        {
            'title': 'First Roller Coaster Design',
            'description': 'Complete the design for our first game-themed roller coaster.',
            'phase_id': phase_ids.get('Phase 3: Theme Park Attractions'),
            'target_date': '2030-06-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 2
        }
    ]
    
    # Add milestones that don't exist yet
    for milestone in milestones:
        if milestone['phase_id'] and milestone['title'] not in existing_milestones:
            print(f"Adding milestone: {milestone['title']}")
            
            # Format completion date or set to NULL
            completion_date = milestone['completion_date'] if milestone['completion_date'] else None
            
            cursor.execute('''
            INSERT INTO strategy_strategymilestone 
            (created_at, updated_at, title, description, phase_id, target_date, status, completion_date, "order")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (
                datetime.now(), 
                datetime.now(), 
                milestone['title'], 
                milestone['description'], 
                milestone['phase_id'], 
                milestone['target_date'], 
                milestone['status'], 
                completion_date, 
                milestone['order']
            ))
        elif milestone['phase_id']:
            print(f"Milestone '{milestone['title']}' already exists or phase not found. Skipping.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll phases and milestones added successfully!")
    print("Try accessing your strategy page now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
