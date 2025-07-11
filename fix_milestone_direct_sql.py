#!/usr/bin/env python
"""
Script to fix milestone database issues using direct SQL with foreign key checks disabled.
This script is designed to be run directly on the production server.
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

def fix_milestone_database():
    """Fix milestone database issues using direct SQL with foreign key checks disabled."""
    print(f"Fixing milestone database issues in: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # 1. First, check the database schema
        print("\nChecking database schema...")
        
        cursor.execute("PRAGMA table_info(strategy_strategymilestone);")
        milestone_columns = cursor.fetchall()
        print(f"Milestone table has {len(milestone_columns)} columns:")
        for col in milestone_columns:
            print(f"  - {col[1]}: {col[2]}")
        
        cursor.execute("PRAGMA table_info(strategy_strategyphase);")
        phase_columns = cursor.fetchall()
        print(f"Phase table has {len(phase_columns)} columns:")
        for col in phase_columns:
            print(f"  - {col[1]}: {col[2]}")
        
        # 2. Check for orphaned milestones
        print("\nChecking for orphaned milestones...")
        cursor.execute("""
        SELECT m.id, m.title, m.phase_id
        FROM strategy_strategymilestone m
        LEFT JOIN strategy_strategyphase p ON m.phase_id = p.id
        WHERE p.id IS NULL;
        """)
        
        orphaned_milestones = cursor.fetchall()
        
        if orphaned_milestones:
            print(f"Found {len(orphaned_milestones)} orphaned milestones:")
            
            # Get a valid phase to assign orphaned milestones to
            cursor.execute("SELECT id, name FROM strategy_strategyphase ORDER BY id LIMIT 1;")
            valid_phase = cursor.fetchone()
            
            if valid_phase:
                valid_phase_id, valid_phase_name = valid_phase
                print(f"Will reassign orphaned milestones to phase: {valid_phase_name} (ID: {valid_phase_id})")
                
                for milestone_id, title, _ in orphaned_milestones:
                    print(f"  - Reassigning milestone '{title}' (ID: {milestone_id})")
                    
                    cursor.execute("""
                    UPDATE strategy_strategymilestone
                    SET phase_id = ?
                    WHERE id = ?;
                    """, (valid_phase_id, milestone_id))
            else:
                print("No valid phases found. Cannot fix orphaned milestones.")
        else:
            print("No orphaned milestones found.")
        
        # 3. Check for in-progress milestones
        print("\nChecking for in-progress milestones...")
        cursor.execute("""
        SELECT id, title, phase_id
        FROM strategy_strategymilestone
        WHERE status = 'in_progress';
        """)
        
        in_progress_milestones = cursor.fetchall()
        
        if in_progress_milestones:
            print(f"Found {len(in_progress_milestones)} in-progress milestones:")
            
            for milestone_id, title, phase_id in in_progress_milestones:
                cursor.execute("SELECT name FROM strategy_strategyphase WHERE id = ?;", (phase_id,))
                phase_name = cursor.fetchone()
                phase_name = phase_name[0] if phase_name else "Unknown"
                print(f"  - Milestone '{title}' (ID: {milestone_id}) in phase '{phase_name}' (ID: {phase_id})")
            
            if len(in_progress_milestones) > 1:
                # Keep only the first milestone as in-progress
                keep_milestone = in_progress_milestones[0]
                print(f"\nKeeping only milestone '{keep_milestone[1]}' (ID: {keep_milestone[0]}) as in-progress")
                
                # Set all others to not_started
                for milestone_id, title, _ in in_progress_milestones[1:]:
                    print(f"  - Setting milestone '{title}' (ID: {milestone_id}) to not_started")
                    
                    cursor.execute("""
                    UPDATE strategy_strategymilestone
                    SET status = 'not_started', updated_at = ?
                    WHERE id = ?;
                    """, (datetime.now().isoformat(), milestone_id))
        else:
            print("No in-progress milestones found.")
        
        # 4. Fix milestone 9 specifically (the one causing issues)
        print("\nFixing milestone 9 specifically...")
        cursor.execute("SELECT id, title, phase_id, status FROM strategy_strategymilestone WHERE id = 9;")
        milestone_9 = cursor.fetchone()
        
        if milestone_9:
            milestone_id, title, phase_id, status = milestone_9
            print(f"Milestone 9: '{title}', Phase ID: {phase_id}, Status: {status}")
            
            # Ensure it has a valid phase
            cursor.execute("SELECT id FROM strategy_strategyphase WHERE id = ?;", (phase_id,))
            valid_phase = cursor.fetchone()
            
            if not valid_phase:
                print("  - Phase ID is invalid, reassigning to a valid phase")
                
                cursor.execute("SELECT id FROM strategy_strategyphase ORDER BY id LIMIT 1;")
                new_phase_id = cursor.fetchone()[0]
                
                cursor.execute("""
                UPDATE strategy_strategymilestone
                SET phase_id = ?
                WHERE id = 9;
                """, (new_phase_id,))
                
                print(f"  - Reassigned to phase ID: {new_phase_id}")
            
            # Set status to not_started to avoid conflicts
            cursor.execute("""
            UPDATE strategy_strategymilestone
            SET status = 'not_started', updated_at = ?
            WHERE id = 9;
            """, (datetime.now().isoformat(),))
            
            print("  - Set status to 'not_started'")
        else:
            print("Milestone 9 not found.")
        
        # 5. Verify foreign key integrity
        print("\nVerifying foreign key integrity...")
        cursor.execute("PRAGMA foreign_key_check;")
        fk_violations = cursor.fetchall()
        
        if fk_violations:
            print(f"Found {len(fk_violations)} foreign key violations:")
            for violation in fk_violations:
                print(f"  - Table: {violation[0]}, Row ID: {violation[1]}, Parent: {violation[2]}, Foreign Key: {violation[3]}")
        else:
            print("No foreign key violations found.")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Commit changes
        conn.commit()
        print("\nChanges committed successfully.")
        
        # Close connection
        conn.close()
        
        print("\nDatabase fix completed!")
        print("You should now be able to edit milestone 9 without foreign key constraint errors.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_milestone_database()
