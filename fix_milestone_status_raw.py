#!/usr/bin/env python
"""
Script to fix milestone status issues using raw SQL to bypass foreign key constraints.
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

print(f"Fixing milestone status issues in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
    if not cursor.fetchone():
        print("Table 'strategy_strategymilestone' does not exist.")
        sys.exit(1)
    
    # Find all in-progress milestones grouped by phase
    cursor.execute("""
    SELECT m.id, m.title, m.phase_id, p.name 
    FROM strategy_strategymilestone m
    JOIN strategy_strategyphase p ON m.phase_id = p.id
    WHERE m.status = 'in_progress'
    ORDER BY m.phase_id, m.id;
    """)
    
    in_progress_milestones = cursor.fetchall()
    
    if not in_progress_milestones:
        print("No in-progress milestones found.")
        sys.exit(0)
    
    print(f"Found {len(in_progress_milestones)} in-progress milestones:")
    
    # Group milestones by phase
    phases = {}
    for milestone_id, title, phase_id, phase_name in in_progress_milestones:
        if phase_id not in phases:
            phases[phase_id] = []
        phases[phase_id].append((milestone_id, title, phase_name))
    
    # For each phase with multiple in-progress milestones, keep only one
    for phase_id, milestones in phases.items():
        if len(milestones) > 1:
            print(f"\nPhase '{milestones[0][2]}' has {len(milestones)} in-progress milestones:")
            
            # Keep the first one as in-progress
            keep_milestone = milestones[0]
            print(f"  Keeping '{keep_milestone[1]}' as 'in_progress'")
            
            # Set others to not_started using raw SQL
            for milestone in milestones[1:]:
                milestone_id = milestone[0]
                milestone_title = milestone[1]
                
                print(f"  Changing '{milestone_title}' from 'in_progress' to 'not_started' using raw SQL")
                
                # Use raw SQL to update the status directly
                cursor.execute("""
                UPDATE strategy_strategymilestone 
                SET status = 'not_started', updated_at = ?
                WHERE id = ?;
                """, (datetime.now().isoformat(), milestone_id))
                
                print(f"  Updated milestone {milestone_id} successfully")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll milestone status issues have been fixed!")
    print("Try editing milestones now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
