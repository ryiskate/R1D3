#!/usr/bin/env python
"""
Script to fix milestone foreign key constraint issues by:
1. Recreating the milestone table with proper foreign key constraints
2. Using direct SQL to bypass Django ORM for milestone status updates
3. Creating a custom view function that can be used to update milestones safely
"""
import os
import sys
import sqlite3
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Get the database path from Django settings
from django.conf import settings
db_path = settings.DATABASES['default']['NAME']

def fix_milestone_table():
    """Fix the milestone table by recreating it with proper foreign key constraints."""
    print(f"Fixing milestone table in: {db_path}")
    
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
            
            # Escape 'order' column name since it's a reserved SQL keyword
            if col_name == 'order':
                col_name = '"order"'
            
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
        
        # Build the insert statement with escaped column names
        escaped_columns = []
        for col in columns:
            if col == 'order':
                escaped_columns.append('"order"')
            else:
                escaped_columns.append(col)
        
        cols_str = ", ".join(escaped_columns)
        placeholders = ", ".join(["?" for _ in columns])
        
        insert_sql = f"INSERT INTO strategy_strategymilestone_new ({cols_str}) VALUES ({placeholders});"
        
        # Insert each row
        for milestone in milestones:
            # Check if the phase_id exists in the strategy_strategyphase table
            phase_id_index = columns.index("phase_id")
            phase_id = milestone[phase_id_index]
            cursor.execute("SELECT id FROM strategy_strategyphase WHERE id = ?;", (phase_id,))
            valid_phase = cursor.fetchone()
            
            if not valid_phase:
                # Phase doesn't exist, get a valid phase ID
                cursor.execute("SELECT id FROM strategy_strategyphase ORDER BY id LIMIT 1;")
                valid_phase = cursor.fetchone()
                
                if valid_phase:
                    # Replace the phase_id with a valid one
                    milestone_list = list(milestone)
                    milestone_list[phase_id_index] = valid_phase[0]
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
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_milestone_update_function():
    """Create a custom function to update milestone statuses safely."""
    print("\nCreating a custom milestone update function...")
    
    function_code = """
import os
import sqlite3
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators.csrf import login_required
from django.shortcuts import get_object_or_404
from strategy.models import StrategyMilestone

@csrf_exempt
@login_required
def update_milestone_status(request, milestone_id, status):
    \"\"\"
    Update a milestone's status using direct SQL to avoid foreign key constraint errors.
    This function can be called directly from JavaScript using AJAX.
    \"\"\"
    try:
        # Get the milestone
        milestone = get_object_or_404(StrategyMilestone, id=milestone_id)
        
        # Update the milestone status
        milestone.status = status
        
        # If setting to in_progress, update other milestones using direct SQL
        if status == 'in_progress' and milestone.status != 'in_progress':
            # Get the database path
            db_path = settings.DATABASES['default']['NAME']
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Temporarily disable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = OFF;")
            
            # Update all other in-progress milestones directly
            cursor.execute(\"\"\"
                UPDATE strategy_strategymilestone 
                SET status = 'not_started', updated_at = datetime('now') 
                WHERE status = 'in_progress' AND id != ?;
            \"\"\", [milestone_id])
            
            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Commit changes
            conn.commit()
            
            # Close connection
            conn.close()
        
        # Save the milestone
        milestone.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Milestone status updated successfully.',
            'milestone_id': milestone_id,
            'status': status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating milestone status: {str(e)}',
            'milestone_id': milestone_id,
            'status': status
        }, status=500)
"""
    
    # Write the function to a file
    function_file = "milestone_update_function.py"
    with open(function_file, "w") as f:
        f.write(function_code)
    
    print(f"\nCustom milestone update function written to: {function_file}")
    print("\nTo use this function:")
    print("1. Copy the function to your strategy/views.py file")
    print("2. Add a URL pattern to your strategy/urls.py file:")
    print("   path('milestone/<int:milestone_id>/update-status/<str:status>/', views.update_milestone_status, name='update_milestone_status'),")
    print("3. Update your templates to use this endpoint instead of the form submission")
    
    return True

def fix_milestone_status(milestone_id=None):
    """Fix milestone status issues by directly updating the database."""
    print("\nFixing milestone status issues...")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Get all in-progress milestones
        cursor.execute("SELECT id, title FROM strategy_strategymilestone WHERE status = 'in_progress';")
        in_progress = cursor.fetchall()
        
        if len(in_progress) > 1:
            print(f"Found {len(in_progress)} milestones with 'in_progress' status:")
            for m in in_progress:
                print(f"  - ID: {m[0]}, Title: {m[1]}")
            
            # Keep only one milestone as in_progress (either the specified one or the first one)
            keep_id = milestone_id if milestone_id else in_progress[0][0]
            
            print(f"\nKeeping milestone ID {keep_id} as 'in_progress' and setting others to 'not_started'...")
            
            # Update all other in-progress milestones
            cursor.execute("""
                UPDATE strategy_strategymilestone 
                SET status = 'not_started', updated_at = datetime('now') 
                WHERE status = 'in_progress' AND id != ?;
            """, [keep_id])
            
            print(f"Updated {cursor.rowcount} milestones to 'not_started' status.")
        else:
            print("No milestone status issues found.")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Commit changes
        conn.commit()
        
        # Close connection
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function to run the script."""
    print("Starting milestone foreign key constraint fix...")
    
    # Fix the milestone table
    if fix_milestone_table():
        print("\nMilestone table fixed successfully!")
    else:
        print("\nFailed to fix milestone table.")
        return
    
    # Fix milestone status issues
    if fix_milestone_status():
        print("\nMilestone status issues fixed successfully!")
    else:
        print("\nFailed to fix milestone status issues.")
    
    # Create the custom milestone update function
    create_milestone_update_function()
    
    print("\nAll fixes completed!")
    print("You should now be able to edit milestones without foreign key constraint errors.")

if __name__ == "__main__":
    main()
