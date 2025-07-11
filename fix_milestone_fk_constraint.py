#!/usr/bin/env python
"""
Script to fix the milestone foreign key constraint by recreating the table
with the correct foreign key reference to the current phase table.
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

def fix_milestone_fk_constraint():
    """Fix the milestone foreign key constraint by recreating the table."""
    print(f"Fixing milestone foreign key constraint in: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # 1. Get the current milestone table schema
        print("\nGetting current milestone table schema...")
        cursor.execute("PRAGMA table_info(strategy_strategymilestone);")
        milestone_columns = cursor.fetchall()
        
        print(f"Milestone table has {len(milestone_columns)} columns:")
        for col in milestone_columns:
            print(f"  - {col[1]}: {col[2]}")
        
        # 2. Get the foreign key info
        cursor.execute("PRAGMA foreign_key_list(strategy_strategymilestone);")
        fk_info = cursor.fetchall()
        
        print("\nForeign key constraints:")
        for fk in fk_info:
            print(f"  - ID: {fk[0]}, Seq: {fk[1]}, Table: {fk[2]}, From: {fk[3]}, To: {fk[4]}")
        
        # 3. Get all milestone data
        print("\nRetrieving all milestone data...")
        cursor.execute("SELECT * FROM strategy_strategymilestone;")
        milestones = cursor.fetchall()
        
        print(f"Found {len(milestones)} milestones")
        
        # 4. Get column names
        cursor.execute("PRAGMA table_info(strategy_strategymilestone);")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 5. Create a temporary table with the correct foreign key constraint
        print("\nCreating temporary milestone table with correct foreign key constraint...")
        
        # Build the create table statement
        create_table_sql = "CREATE TABLE strategy_strategymilestone_new ("
        
        for i, col in enumerate(milestone_columns):
            col_id, col_name, col_type, col_notnull, col_default, col_pk = col
            
            create_table_sql += f"\n    {col_name} {col_type}"
            
            if col_pk:
                create_table_sql += " PRIMARY KEY"
            
            if col_notnull:
                create_table_sql += " NOT NULL"
            
            if col_default is not None:
                create_table_sql += f" DEFAULT {col_default}"
            
            if i < len(milestone_columns) - 1:
                create_table_sql += ","
        
        # Add the correct foreign key constraint
        create_table_sql += ",\n    FOREIGN KEY (phase_id) REFERENCES strategy_strategyphase (id)"
        create_table_sql += "\n);"
        
        print(create_table_sql)
        
        # Execute the create table statement
        cursor.execute(create_table_sql)
        
        # 6. Copy data to the new table
        print("\nCopying milestone data to new table...")
        
        # Build the insert statement
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        
        insert_sql = f"INSERT INTO strategy_strategymilestone_new ({cols_str}) VALUES ({placeholders});"
        
        # Insert each row
        for milestone in milestones:
            # Check if the phase_id exists in the strategy_strategyphase table
            phase_id = milestone[columns.index("phase_id")]
            cursor.execute("SELECT id FROM strategy_strategyphase WHERE id = ?;", (phase_id,))
            valid_phase = cursor.fetchone()
            
            if not valid_phase:
                # Phase doesn't exist, get a valid phase ID
                cursor.execute("SELECT id FROM strategy_strategyphase ORDER BY id LIMIT 1;")
                valid_phase = cursor.fetchone()
                
                if valid_phase:
                    # Replace the phase_id with a valid one
                    milestone_list = list(milestone)
                    milestone_list[columns.index("phase_id")] = valid_phase[0]
                    milestone = tuple(milestone_list)
                    
                    print(f"  - Reassigning milestone ID {milestone[0]} to phase ID {valid_phase[0]}")
            
            # Insert the milestone
            cursor.execute(insert_sql, milestone)
        
        # 7. Drop the old table and rename the new one
        print("\nReplacing old milestone table with new one...")
        cursor.execute("DROP TABLE strategy_strategymilestone;")
        cursor.execute("ALTER TABLE strategy_strategymilestone_new RENAME TO strategy_strategymilestone;")
        
        # 8. Verify foreign key integrity
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
        print("You should now be able to edit milestones without foreign key constraint errors.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_milestone_fk_constraint()
