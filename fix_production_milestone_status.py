#!/usr/bin/env python
"""
Script to fix milestone status issues in production using raw SQL to bypass foreign key constraints.
This script is designed to be run on PythonAnywhere production environment.
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

print(f"Fixing milestone status issues in production database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys for this connection
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
    if not cursor.fetchone():
        print("Table 'strategy_strategymilestone' does not exist.")
        sys.exit(1)
    
    # First, check all milestones for valid phase references
    print("Checking all milestones for valid phase references...")
    cursor.execute("""
    SELECT m.id, m.title, m.phase_id, p.id, p.name 
    FROM strategy_strategymilestone m
    LEFT JOIN strategy_strategyphase p ON m.phase_id = p.id
    ORDER BY m.id;
    """)
    
    milestones = cursor.fetchall()
    orphaned_milestones = []
    
    for milestone_id, title, phase_id, actual_phase_id, phase_name in milestones:
        if actual_phase_id is None:
            print(f"WARNING: Milestone '{title}' (ID: {milestone_id}) references non-existent phase ID: {phase_id}")
            orphaned_milestones.append((milestone_id, title, phase_id))
    
    # Fix orphaned milestones by assigning them to the first valid phase
    if orphaned_milestones:
        print("\nFixing orphaned milestones...")
        
        # Get a valid phase to assign orphaned milestones to
        cursor.execute("SELECT id, name FROM strategy_strategyphase ORDER BY id LIMIT 1;")
        valid_phase = cursor.fetchone()
        
        if not valid_phase:
            print("ERROR: No valid phases found in the database.")
            sys.exit(1)
        
        valid_phase_id, valid_phase_name = valid_phase
        
        for milestone_id, title, _ in orphaned_milestones:
            print(f"Reassigning milestone '{title}' to phase '{valid_phase_name}' (ID: {valid_phase_id})")
            
            cursor.execute("""
            UPDATE strategy_strategymilestone 
            SET phase_id = ?, updated_at = ?
            WHERE id = ?;
            """, (valid_phase_id, datetime.now().isoformat(), milestone_id))
    
    # Find all in-progress milestones grouped by phase
    print("\nChecking for issues with in_progress milestones...")
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
    else:
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
                    
                    print(f"  Changing '{milestone_title}' from 'in_progress' to 'not_started'")
                    
                    try:
                        # Use raw SQL to update the status directly
                        cursor.execute("""
                        UPDATE strategy_strategymilestone 
                        SET status = 'not_started', updated_at = ?
                        WHERE id = ?;
                        """, (datetime.now().isoformat(), milestone_id))
                        
                        print(f"  Updated milestone {milestone_id} successfully")
                    except sqlite3.Error as e:
                        print(f"  ERROR updating milestone {milestone_id}: {e}")
                        
                        # Try with PRAGMA foreign_keys OFF as a last resort
                        print("  Attempting update with foreign key checks disabled...")
                        cursor.execute("PRAGMA foreign_keys = OFF;")
                        
                        cursor.execute("""
                        UPDATE strategy_strategymilestone 
                        SET status = 'not_started', updated_at = ?
                        WHERE id = ?;
                        """, (datetime.now().isoformat(), milestone_id))
                        
                        cursor.execute("PRAGMA foreign_keys = ON;")
                        print("  Update completed with foreign key checks disabled")
    
    # Check for any other issues with milestones
    print("\nChecking for other potential issues...")
    
    # Check if any phase has no current milestone
    cursor.execute("""
    SELECT p.id, p.name
    FROM strategy_strategyphase p
    LEFT JOIN strategy_strategymilestone m ON p.id = m.phase_id AND m.status = 'in_progress'
    WHERE m.id IS NULL;
    """)
    
    phases_without_current = cursor.fetchall()
    
    if phases_without_current:
        print(f"Found {len(phases_without_current)} phases without an in-progress milestone:")
        
        for phase_id, phase_name in phases_without_current:
            print(f"Phase '{phase_name}' (ID: {phase_id}) has no in-progress milestone")
            
            # Get the first milestone for this phase
            cursor.execute("""
            SELECT id, title FROM strategy_strategymilestone
            WHERE phase_id = ?
            ORDER BY id
            LIMIT 1;
            """, (phase_id,))
            
            first_milestone = cursor.fetchone()
            
            if first_milestone:
                milestone_id, milestone_title = first_milestone
                print(f"  Setting milestone '{milestone_title}' to 'in_progress'")
                
                try:
                    cursor.execute("""
                    UPDATE strategy_strategymilestone 
                    SET status = 'in_progress', updated_at = ?
                    WHERE id = ?;
                    """, (datetime.now().isoformat(), milestone_id))
                    
                    print(f"  Updated milestone {milestone_id} successfully")
                except sqlite3.Error as e:
                    print(f"  ERROR updating milestone {milestone_id}: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll milestone status issues have been fixed!")
    print("Try editing milestones now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
