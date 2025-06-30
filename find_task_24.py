"""
Script to find task ID 24 in all task-related tables
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

def list_all_task_tables():
    """List all tables in the database that might contain tasks"""
    with connection.cursor() as cursor:
        # Get list of all tables in the database
        if connection.vendor == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        elif connection.vendor == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
        elif connection.vendor == 'mysql':
            cursor.execute("SHOW TABLES;")
        else:
            print(f"Unsupported database vendor: {connection.vendor}")
            return []
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # Filter for task-related tables
        task_tables = [table for table in tables if 'task' in table.lower()]
        return task_tables

def find_task_in_table(table_name, task_id):
    """Check if a task with the given ID exists in the specified table and print its details"""
    with connection.cursor() as cursor:
        try:
            # First check if the table has an id column
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'id' not in columns:
                print(f"Table {table_name} does not have an id column")
                return False
                
            # Check if the task exists
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", [task_id])
            row = cursor.fetchone()
            
            if row:
                print(f"Found task ID {task_id} in table {table_name}")
                # Print column names and values
                print("Task details:")
                for i, column in enumerate(columns):
                    if i < len(row):
                        print(f"  {column}: {row[i]}")
                return True
        except (OperationalError, ProgrammingError) as e:
            print(f"Error querying table {table_name}: {e}")
    
    return False

if __name__ == "__main__":
    task_id = 24
    print(f"Searching for task ID {task_id} in all task-related tables...")
    
    # Get all task-related tables
    task_tables = list_all_task_tables()
    print(f"Found {len(task_tables)} task-related tables:")
    
    # Search for the task in each table
    found = False
    for table in task_tables:
        print(f"\nChecking table {table}...")
        if find_task_in_table(table, task_id):
            found = True
    
    if not found:
        print(f"\nTask ID {task_id} not found in any task-related table")
