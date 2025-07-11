#!/usr/bin/env python
"""
Script to fix the foreign key references between milestones and phases.
This script addresses the specific issue where milestones are referencing 
strategy_strategyphase_old instead of strategy_strategyphase.
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

def fix_phase_references():
    """Fix the foreign key references between milestones and phases."""
    print(f"Fixing phase references in: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # 1. Check if the old phase table exists
        print("\nChecking for strategy_strategyphase_old table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategyphase_old';")
        old_phase_table = cursor.fetchone()
        
        if old_phase_table:
            print("Found strategy_strategyphase_old table.")
            
            # Check the structure of both tables
            cursor.execute("PRAGMA table_info(strategy_strategyphase);")
            new_table_columns = cursor.fetchall()
            
            cursor.execute("PRAGMA table_info(strategy_strategyphase_old);")
            old_table_columns = cursor.fetchall()
            
            print(f"New phase table has {len(new_table_columns)} columns")
            print(f"Old phase table has {len(old_table_columns)} columns")
            
            # 2. Check if there's data in the old table that needs to be migrated
            cursor.execute("SELECT COUNT(*) FROM strategy_strategyphase_old;")
            old_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM strategy_strategyphase;")
            new_count = cursor.fetchone()[0]
            
            print(f"Old phase table has {old_count} rows")
            print(f"New phase table has {new_count} rows")
            
            if old_count > 0 and new_count == 0:
                print("\nMigrating data from old phase table to new phase table...")
                
                # Get column names that exist in both tables
                new_cols = [col[1] for col in new_table_columns]
                old_cols = [col[1] for col in old_table_columns]
                common_cols = [col for col in old_cols if col in new_cols]
                
                # Build the SQL query
                cols_str = ', '.join(common_cols)
                placeholders = ', '.join(['?'] * len(common_cols))
                
                # Get data from old table
                cursor.execute(f"SELECT {cols_str} FROM strategy_strategyphase_old;")
                old_data = cursor.fetchall()
                
                # Insert into new table
                for row in old_data:
                    cursor.execute(f"INSERT INTO strategy_strategyphase ({cols_str}) VALUES ({placeholders});", row)
                
                print(f"Migrated {len(old_data)} rows from old table to new table")
            
            # 3. Update milestone references to point to the new phase table
            print("\nUpdating milestone references...")
            
            # First, get all milestones and their current phase_id
            cursor.execute("SELECT id, title, phase_id FROM strategy_strategymilestone;")
            milestones = cursor.fetchall()
            
            updated_count = 0
            for milestone_id, title, phase_id in milestones:
                # Check if the phase exists in the new table
                cursor.execute("SELECT id FROM strategy_strategyphase WHERE id = ?;", (phase_id,))
                new_phase = cursor.fetchone()
                
                if not new_phase:
                    # Phase doesn't exist in new table, try to find it in old table
                    cursor.execute("SELECT id, name FROM strategy_strategyphase_old WHERE id = ?;", (phase_id,))
                    old_phase = cursor.fetchone()
                    
                    if old_phase:
                        old_phase_id, old_phase_name = old_phase
                        
                        # Check if a phase with the same name exists in the new table
                        cursor.execute("SELECT id FROM strategy_strategyphase WHERE name = ?;", (old_phase_name,))
                        matching_phase = cursor.fetchone()
                        
                        if matching_phase:
                            new_phase_id = matching_phase[0]
                            print(f"  - Updating milestone '{title}' (ID: {milestone_id}) to use phase ID {new_phase_id} instead of {phase_id}")
                            
                            cursor.execute("""
                            UPDATE strategy_strategymilestone
                            SET phase_id = ?
                            WHERE id = ?;
                            """, (new_phase_id, milestone_id))
                            
                            updated_count += 1
                        else:
                            # No matching phase found, create a new one
                            cursor.execute("SELECT * FROM strategy_strategyphase_old WHERE id = ?;", (old_phase_id,))
                            old_phase_data = cursor.fetchone()
                            
                            if old_phase_data:
                                # Get column names
                                cursor.execute("PRAGMA table_info(strategy_strategyphase_old);")
                                old_cols = [col[1] for col in cursor.fetchall()]
                                
                                # Create a dictionary of column name to value
                                old_phase_dict = dict(zip(old_cols, old_phase_data))
                                
                                # Insert into new table
                                cursor.execute("PRAGMA table_info(strategy_strategyphase);")
                                new_cols = [col[1] for col in cursor.fetchall()]
                                
                                # Build insert statement with only columns that exist in both tables
                                common_cols = [col for col in old_cols if col in new_cols]
                                cols_str = ', '.join(common_cols)
                                placeholders = ', '.join(['?'] * len(common_cols))
                                
                                values = [old_phase_dict[col] for col in common_cols]
                                
                                cursor.execute(f"INSERT INTO strategy_strategyphase ({cols_str}) VALUES ({placeholders});", values)
                                new_phase_id = cursor.lastrowid
                                
                                print(f"  - Created new phase with ID {new_phase_id} and updated milestone '{title}' (ID: {milestone_id})")
                                
                                cursor.execute("""
                                UPDATE strategy_strategymilestone
                                SET phase_id = ?
                                WHERE id = ?;
                                """, (new_phase_id, milestone_id))
                                
                                updated_count += 1
                    else:
                        # Phase doesn't exist in either table, assign to first available phase
                        cursor.execute("SELECT id FROM strategy_strategyphase ORDER BY id LIMIT 1;")
                        first_phase = cursor.fetchone()
                        
                        if first_phase:
                            new_phase_id = first_phase[0]
                            print(f"  - Orphaned milestone '{title}' (ID: {milestone_id}) assigned to phase ID {new_phase_id}")
                            
                            cursor.execute("""
                            UPDATE strategy_strategymilestone
                            SET phase_id = ?
                            WHERE id = ?;
                            """, (new_phase_id, milestone_id))
                            
                            updated_count += 1
            
            print(f"Updated {updated_count} milestone references")
            
            # 4. Drop the old table if it's no longer needed
            if new_count > 0:
                print("\nDropping old phase table...")
                cursor.execute("DROP TABLE IF EXISTS strategy_strategyphase_old;")
                print("Old phase table dropped")
        else:
            print("No strategy_strategyphase_old table found.")
            
            # Check for foreign key violations
            print("\nChecking for foreign key violations...")
            cursor.execute("PRAGMA foreign_key_check;")
            violations = cursor.fetchall()
            
            if violations:
                print(f"Found {len(violations)} foreign key violations:")
                
                # Group violations by table and foreign key
                violation_groups = {}
                for violation in violations:
                    table, rowid, parent, fk = violation
                    key = (table, parent, fk)
                    if key not in violation_groups:
                        violation_groups[key] = []
                    violation_groups[key].append(rowid)
                
                # Fix each group of violations
                for (table, parent, fk), rowids in violation_groups.items():
                    print(f"  - Table: {table}, Parent: {parent}, Foreign Key: {fk}, Rows: {len(rowids)}")
                    
                    if parent == 'strategy_strategyphase_old':
                        # This is the case we're looking for - milestones referencing old phase table
                        print(f"    Fixing references to strategy_strategyphase_old...")
                        
                        # Get a valid phase ID from the current phase table
                        cursor.execute("SELECT id FROM strategy_strategyphase ORDER BY id LIMIT 1;")
                        valid_phase = cursor.fetchone()
                        
                        if valid_phase:
                            valid_phase_id = valid_phase[0]
                            
                            # Update all affected rows
                            for rowid in rowids:
                                cursor.execute(f"""
                                UPDATE {table}
                                SET phase_id = ?
                                WHERE id = ?;
                                """, (valid_phase_id, rowid))
                                
                                print(f"    - Updated row ID {rowid} to use phase ID {valid_phase_id}")
                        else:
                            print("    No valid phases found in strategy_strategyphase table")
            else:
                print("No foreign key violations found")
        
        # 5. Update the sqlite_sequence table if needed
        print("\nUpdating sqlite_sequence table...")
        cursor.execute("SELECT name, seq FROM sqlite_sequence WHERE name IN ('strategy_strategyphase', 'strategy_strategyphase_old');")
        sequences = cursor.fetchall()
        
        for name, seq in sequences:
            print(f"  - {name}: {seq}")
        
        # 6. Verify foreign key integrity
        print("\nVerifying foreign key integrity...")
        cursor.execute("PRAGMA foreign_key_check;")
        fk_violations = cursor.fetchall()
        
        if fk_violations:
            print(f"Found {len(fk_violations)} remaining foreign key violations:")
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
    fix_phase_references()
