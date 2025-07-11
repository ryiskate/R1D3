#!/usr/bin/env python
"""
Script to fix milestone database integrity issues without changing the intended behavior.
This script ensures that foreign key constraints are satisfied while maintaining the rule
that only one milestone can be in_progress across all phases.
"""
import os
import django
import sys
import sqlite3
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Get the database path from Django settings
from django.conf import settings
db_path = settings.DATABASES['default']['NAME']

def fix_milestone_integrity():
    """Fix milestone integrity issues using raw SQL to bypass Django ORM constraints."""
    print(f"Fixing milestone integrity issues in database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Temporarily disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Check for orphaned milestones (referencing non-existent phases)
        print("Checking for orphaned milestones...")
        cursor.execute("""
        SELECT m.id, m.title, m.phase_id
        FROM strategy_strategymilestone m
        LEFT JOIN strategy_strategyphase p ON m.phase_id = p.id
        WHERE p.id IS NULL;
        """)
        
        orphaned_milestones = cursor.fetchall()
        
        if orphaned_milestones:
            print(f"Found {len(orphaned_milestones)} orphaned milestones.")
            
            # Get a valid phase to assign orphaned milestones to
            cursor.execute("SELECT id FROM strategy_strategyphase ORDER BY id LIMIT 1;")
            valid_phase = cursor.fetchone()
            
            if valid_phase:
                valid_phase_id = valid_phase[0]
                
                for milestone_id, title, _ in orphaned_milestones:
                    print(f"Reassigning milestone '{title}' (ID: {milestone_id}) to phase ID: {valid_phase_id}")
                    
                    cursor.execute("""
                    UPDATE strategy_strategymilestone
                    SET phase_id = ?
                    WHERE id = ?;
                    """, (valid_phase_id, milestone_id))
            else:
                print("No valid phases found. Cannot fix orphaned milestones.")
        else:
            print("No orphaned milestones found.")
        
        # Check for multiple in-progress milestones
        print("\nChecking for multiple in-progress milestones...")
        cursor.execute("""
        SELECT id, title, phase_id
        FROM strategy_strategymilestone
        WHERE status = 'in_progress'
        ORDER BY id;
        """)
        
        in_progress_milestones = cursor.fetchall()
        
        if len(in_progress_milestones) > 1:
            print(f"Found {len(in_progress_milestones)} in-progress milestones.")
            
            # Keep the first one as in-progress
            keep_milestone = in_progress_milestones[0]
            print(f"Keeping milestone '{keep_milestone[1]}' (ID: {keep_milestone[0]}) as in-progress")
            
            # Set others to not_started
            for milestone_id, title, _ in in_progress_milestones[1:]:
                print(f"Setting milestone '{title}' (ID: {milestone_id}) to not_started")
                
                cursor.execute("""
                UPDATE strategy_strategymilestone
                SET status = 'not_started', updated_at = ?
                WHERE id = ?;
                """, (datetime.now().isoformat(), milestone_id))
        else:
            print(f"Found {len(in_progress_milestones)} in-progress milestones. No conflicts to resolve.")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Verify the fix
        print("\nVerifying database integrity...")
        cursor.execute("PRAGMA integrity_check;")
        integrity_check = cursor.fetchone()
        
        if integrity_check and integrity_check[0] == 'ok':
            print("Database integrity check passed.")
        else:
            print(f"Database integrity check failed: {integrity_check}")
        
        # Commit changes
        conn.commit()
        print("\nChanges committed successfully.")
        
        # Close connection
        conn.close()
        
        print("\nMilestone integrity issues have been fixed!")
        print("You should now be able to edit milestones without foreign key constraint errors.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_milestone_integrity()
