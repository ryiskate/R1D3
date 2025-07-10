#!/usr/bin/env python
"""
Script to add strategy milestones for each phase.
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

print(f"Adding strategy milestones to database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist. Please run the fix_is_current_column_v2.py script first.")
        sys.exit(1)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
    if not cursor.fetchone():
        print("Table 'strategy_strategymilestone' does not exist. Creating it...")
        cursor.execute('''
        CREATE TABLE strategy_strategymilestone (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            phase_id INTEGER NOT NULL,
            target_date DATE,
            status VARCHAR(20) NOT NULL,
            completion_date DATE,
            "order" INTEGER NOT NULL,
            FOREIGN KEY (phase_id) REFERENCES strategy_strategyphase (id)
        );
        ''')
        print("Table created successfully!")
    
    # Get phase IDs
    cursor.execute("SELECT id, name FROM strategy_strategyphase;")
    phases = cursor.fetchall()
    
    if not phases:
        print("No phases found. Please run the add_strategy_phases.py script first.")
        sys.exit(1)
    
    phase_ids = {name: id for id, name in phases}
    print(f"Found phases: {', '.join([name for _, name in phases])}")
    
    # Check existing milestones
    cursor.execute("SELECT title FROM strategy_strategymilestone;")
    existing_milestones = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(existing_milestones)} existing milestones")
    
    # Define milestones for each phase
    milestones = [
        # Initial Phase
        {
            'title': 'Define Company Strategy',
            'description': 'Create a comprehensive strategy document outlining our growth plan.',
            'phase_name': 'Initial Phase',
            'target_date': '2025-12-31',
            'status': 'completed',
            'completion_date': '2025-07-01',
            'order': 1
        },
        {
            'title': 'Establish Core Team',
            'description': 'Recruit and onboard the initial team members with key skills.',
            'phase_name': 'Initial Phase',
            'target_date': '2025-09-30',
            'status': 'completed',
            'completion_date': '2025-08-15',
            'order': 2
        },
        {
            'title': 'Secure Initial Funding',
            'description': 'Obtain seed funding to support the first year of operations.',
            'phase_name': 'Initial Phase',
            'target_date': '2025-11-30',
            'status': 'in_progress',
            'completion_date': None,
            'order': 3
        },
        
        # Phase 1: Indie Game Development
        {
            'title': 'Learn Game Development Tools',
            'description': 'Master essential game development tools and processes.',
            'phase_name': 'Phase 1: Indie Game Development',
            'target_date': '2026-03-31',
            'status': 'completed',
            'completion_date': '2026-02-28',
            'order': 1
        },
        {
            'title': 'Release First Indie Game',
            'description': 'Develop and publish our first indie game on Steam.',
            'phase_name': 'Phase 1: Indie Game Development',
            'target_date': '2026-09-30',
            'status': 'in_progress',
            'completion_date': None,
            'order': 2
        },
        {
            'title': 'Establish Game Development Blog',
            'description': 'Create and grow a development blog with tutorials and insights.',
            'phase_name': 'Phase 1: Indie Game Development',
            'target_date': '2026-06-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 3
        },
        {
            'title': 'Launch Game Development Education Platform',
            'description': 'Create an online platform for teaching game development skills.',
            'phase_name': 'Phase 1: Indie Game Development',
            'target_date': '2027-03-31',
            'status': 'not_started',
            'completion_date': None,
            'order': 4
        },
        {
            'title': 'Attend Major Game Industry Conference',
            'description': 'Participate in a major game industry conference to network and showcase our work.',
            'phase_name': 'Phase 1: Indie Game Development',
            'target_date': '2027-06-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 5
        },
        
        # Phase 2: Arcade Machines
        {
            'title': 'Hardware Integration Research',
            'description': 'Complete research on hardware integration for arcade machines.',
            'phase_name': 'Phase 2: Arcade Machines',
            'target_date': '2027-09-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 1
        },
        {
            'title': 'Prototype First Arcade Cabinet',
            'description': 'Build a prototype arcade cabinet with custom controls.',
            'phase_name': 'Phase 2: Arcade Machines',
            'target_date': '2028-03-31',
            'status': 'not_started',
            'completion_date': None,
            'order': 2
        },
        {
            'title': 'Develop Arcade-Specific Game',
            'description': 'Create a game specifically designed for arcade machines.',
            'phase_name': 'Phase 2: Arcade Machines',
            'target_date': '2028-09-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 3
        },
        {
            'title': 'Open First Arcade Location',
            'description': 'Establish our first physical arcade location featuring our machines.',
            'phase_name': 'Phase 2: Arcade Machines',
            'target_date': '2029-03-31',
            'status': 'not_started',
            'completion_date': None,
            'order': 4
        },
        
        # Phase 3: Theme Park Attractions
        {
            'title': 'Attraction Prototype',
            'description': 'Develop a prototype for an immersive 3D attraction.',
            'phase_name': 'Phase 3: Theme Park Attractions',
            'target_date': '2029-09-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 1
        },
        {
            'title': 'Simulator Technology Development',
            'description': 'Research and develop simulator technology for immersive experiences.',
            'phase_name': 'Phase 3: Theme Park Attractions',
            'target_date': '2030-03-31',
            'status': 'not_started',
            'completion_date': None,
            'order': 2
        },
        {
            'title': 'First Roller Coaster Design',
            'description': 'Complete the design for our first game-themed roller coaster.',
            'phase_name': 'Phase 3: Theme Park Attractions',
            'target_date': '2030-09-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 3
        },
        {
            'title': 'Themed Environment Prototype',
            'description': 'Create a prototype of a fully themed environment based on our games.',
            'phase_name': 'Phase 3: Theme Park Attractions',
            'target_date': '2031-03-31',
            'status': 'not_started',
            'completion_date': None,
            'order': 4
        },
        {
            'title': 'Theme Park Land Opening',
            'description': 'Open our first themed land within an existing theme park.',
            'phase_name': 'Phase 3: Theme Park Attractions',
            'target_date': '2031-09-30',
            'status': 'not_started',
            'completion_date': None,
            'order': 5
        }
    ]
    
    # Add milestones that don't exist yet
    added_count = 0
    skipped_count = 0
    
    for milestone in milestones:
        phase_id = phase_ids.get(milestone['phase_name'])
        
        if not phase_id:
            print(f"Phase '{milestone['phase_name']}' not found. Skipping milestone '{milestone['title']}'.")
            skipped_count += 1
            continue
        
        if milestone['title'] not in existing_milestones:
            print(f"Adding milestone: {milestone['title']} for phase {milestone['phase_name']}")
            
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
                phase_id, 
                milestone['target_date'], 
                milestone['status'], 
                completion_date, 
                milestone['order']
            ))
            added_count += 1
        else:
            print(f"Milestone '{milestone['title']}' already exists. Skipping.")
            skipped_count += 1
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"\nAdded {added_count} new milestones. Skipped {skipped_count} existing milestones.")
    print("Try accessing your strategy page now to see the milestones.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
