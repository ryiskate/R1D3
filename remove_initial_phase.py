#!/usr/bin/env python
"""
Script to remove the Initial Phase and transfer its milestones to Phase 1.
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

print(f"Removing Initial Phase from database: {db_path}")

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase';")
    if not cursor.fetchone():
        print("Table 'strategy_strategyphase' does not exist.")
        sys.exit(1)
    
    # Find the Initial Phase
    cursor.execute("SELECT id FROM strategy_strategyphase WHERE name = 'Initial Phase';")
    initial_phase = cursor.fetchone()
    
    if not initial_phase:
        print("Initial Phase not found. Nothing to remove.")
        sys.exit(0)
    
    initial_phase_id = initial_phase[0]
    print(f"Found Initial Phase with ID: {initial_phase_id}")
    
    # Find Phase 1
    cursor.execute("SELECT id FROM strategy_strategyphase WHERE name = 'Phase 1: Indie Game Development';")
    phase1 = cursor.fetchone()
    
    if not phase1:
        print("Phase 1 not found. Cannot transfer milestones.")
        sys.exit(1)
    
    phase1_id = phase1[0]
    print(f"Found Phase 1 with ID: {phase1_id}")
    
    # Check if there are milestones for Initial Phase
    cursor.execute("SELECT COUNT(*) FROM strategy_strategymilestone WHERE phase_id = ?;", (initial_phase_id,))
    milestone_count = cursor.fetchone()[0]
    
    if milestone_count > 0:
        print(f"Found {milestone_count} milestones to transfer from Initial Phase to Phase 1")
        
        # Update milestones to belong to Phase 1
        cursor.execute("""
        UPDATE strategy_strategymilestone 
        SET phase_id = ?, updated_at = ?
        WHERE phase_id = ?;
        """, (phase1_id, datetime.now(), initial_phase_id))
        
        print(f"Transferred {milestone_count} milestones to Phase 1")
    else:
        print("No milestones found for Initial Phase")
    
    # Update is_current flag for Phase 1
    cursor.execute("SELECT 1 FROM strategy_strategyphase WHERE id = ? AND is_current = 1;", (initial_phase_id,))
    was_current = cursor.fetchone()
    
    if was_current:
        print("Initial Phase was marked as current. Setting Phase 1 as current.")
        cursor.execute("UPDATE strategy_strategyphase SET is_current = 1, status = 'in_progress' WHERE id = ?;", (phase1_id,))
    
    # Delete the Initial Phase
    cursor.execute("DELETE FROM strategy_strategyphase WHERE id = ?;", (initial_phase_id,))
    print("Deleted Initial Phase")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nInitial Phase removed successfully!")
    print("Try accessing your strategy page now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
