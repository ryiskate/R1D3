"""
Script to find and delete specific tasks by ID across all models in the database
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.db import connection
from django.apps import apps

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
    """Check if a task with the given ID exists in the specified table"""
    with connection.cursor() as cursor:
        # Check if the table has an id column
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", [task_id])
            row = cursor.fetchone()
            if row:
                print(f"Found task ID {task_id} in table {table_name}")
                return True, table_name
        except Exception as e:
            print(f"Error querying table {table_name}: {e}")
    
    return False, None

def delete_task_from_table(table_name, task_id):
    """Delete a task from the specified table"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", [task_id])
            affected_rows = cursor.rowcount
            if affected_rows > 0:
                print(f"Successfully deleted task ID {task_id} from table {table_name}")
                return True
            else:
                print(f"No rows affected when trying to delete task ID {task_id} from {table_name}")
                return False
        except Exception as e:
            print(f"Error deleting from table {table_name}: {e}")
            return False

def find_and_delete_task(task_id):
    """Find a task in any table and delete it"""
    task_tables = list_all_task_tables()
    print(f"\nSearching for task ID {task_id} in {len(task_tables)} tables:")
    
    for table in task_tables:
        found, table_name = find_task_in_table(table, task_id)
        if found:
            confirm = input(f"Do you want to delete task ID {task_id} from table {table_name}? (y/n): ")
            if confirm.lower() == 'y':
                delete_task_from_table(table_name, task_id)
            else:
                print(f"Skipping deletion of task ID {task_id} from {table_name}")
            return True
    
    print(f"Task ID {task_id} not found in any table")
    return False

if __name__ == "__main__":
    task_ids = [92, 98]
    
    if len(sys.argv) > 1:
        task_ids = [int(arg) for arg in sys.argv[1:]]
    
    print(f"Starting search for tasks with IDs: {task_ids}")
    
    # First, list all task-related tables
    task_tables = list_all_task_tables()
    print(f"Found {len(task_tables)} task-related tables:")
    for table in task_tables:
        print(f"  - {table}")
    
    # Then search for and delete each task
    for task_id in task_ids:
        find_and_delete_task(task_id)
    
    print("\nTask search and deletion process completed.")
