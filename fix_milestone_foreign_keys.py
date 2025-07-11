#!/usr/bin/env python
"""
Script to fix foreign key constraints for strategy milestones.
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

print(f"Fixing milestone foreign keys in database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist.")
        sys.exit(1)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
    if not cursor.fetchone():
        print("Table 'strategy_strategymilestone' does not exist.")
        sys.exit(1)
    
    # Get all existing phase IDs
    cursor.execute("SELECT id FROM strategy_strategyphase;")
    phase_ids = [row[0] for row in cursor.fetchall()]
    
    if not phase_ids:
        print("No phases found in the database.")
        sys.exit(1)
    
    print(f"Found {len(phase_ids)} valid phases with IDs: {phase_ids}")
    
    # Find milestones with invalid phase references
    cursor.execute("""
    SELECT id, title, phase_id FROM strategy_strategymilestone 
    WHERE phase_id NOT IN (SELECT id FROM strategy_strategyphase);
    """)
    
    invalid_milestones = cursor.fetchall()
    
    if not invalid_milestones:
        print("No milestones with invalid phase references found. All foreign keys are valid.")
    else:
        print(f"Found {len(invalid_milestones)} milestones with invalid phase references:")
        
        # Get the first valid phase ID to reassign milestones to
        default_phase_id = phase_ids[0]
        print(f"Will reassign invalid milestones to phase ID: {default_phase_id}")
        
        for milestone_id, title, invalid_phase_id in invalid_milestones:
            print(f"  - Milestone '{title}' (ID: {milestone_id}) references non-existent phase ID: {invalid_phase_id}")
            
            # Update the milestone to reference a valid phase
            cursor.execute("""
            UPDATE strategy_strategymilestone 
            SET phase_id = ?, updated_at = ?
            WHERE id = ?;
            """, (default_phase_id, datetime.now(), milestone_id))
            
            print(f"    Updated milestone '{title}' to reference phase ID: {default_phase_id}")
        
        print(f"\nFixed {len(invalid_milestones)} milestones with invalid phase references.")
    
    # Check for any other potential foreign key issues
    print("\nChecking for other potential foreign key issues...")
    
    # Check for milestones with NULL phase_id
    cursor.execute("SELECT id, title FROM strategy_strategymilestone WHERE phase_id IS NULL;")
    null_phase_milestones = cursor.fetchall()
    
    if null_phase_milestones:
        print(f"Found {len(null_phase_milestones)} milestones with NULL phase_id:")
        
        for milestone_id, title in null_phase_milestones:
            print(f"  - Milestone '{title}' (ID: {milestone_id}) has NULL phase_id")
            
            # Update the milestone to reference a valid phase
            cursor.execute("""
            UPDATE strategy_strategymilestone 
            SET phase_id = ?, updated_at = ?
            WHERE id = ?;
            """, (default_phase_id, datetime.now(), milestone_id))
            
            print(f"    Updated milestone '{title}' to reference phase ID: {default_phase_id}")
    else:
        print("No milestones with NULL phase_id found.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nAll milestone foreign key issues have been fixed!")
    print("Try editing milestones now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
