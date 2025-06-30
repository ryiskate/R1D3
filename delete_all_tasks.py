"""
Script to delete all tasks from all task-related tables in the R1D3 system
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

def count_tasks_in_table(table_name):
    """Count the number of tasks in a table"""
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            return count
        except (OperationalError, ProgrammingError) as e:
            print(f"Error counting tasks in {table_name}: {e}")
            return 0

def delete_all_tasks_from_table(table_name):
    """Delete all tasks from the specified table"""
    with connection.cursor() as cursor:
        try:
            # Count tasks before deletion
            count_before = count_tasks_in_table(table_name)
            if count_before == 0:
                print(f"No tasks found in {table_name}")
                return 0
                
            # Delete all tasks
            cursor.execute(f"DELETE FROM {table_name}")
            affected_rows = cursor.rowcount
            print(f"Deleted {affected_rows} tasks from {table_name}")
            return affected_rows
        except (OperationalError, ProgrammingError) as e:
            print(f"Error deleting tasks from {table_name}: {e}")
            return 0

if __name__ == "__main__":
    print("Starting task deletion process...")
    
    # Get all task-related tables
    task_tables = list_all_task_tables()
    print(f"Found {len(task_tables)} task-related tables:")
    for table in task_tables:
        print(f"  - {table}")
    
    # Count tasks in each table
    total_tasks = 0
    table_counts = {}
    for table in task_tables:
        count = count_tasks_in_table(table)
        table_counts[table] = count
        total_tasks += count
        print(f"  {table}: {count} tasks")
    
    print(f"\nTotal tasks found: {total_tasks}")
    
    # Confirm deletion
    print("\nWARNING: This will delete ALL tasks from ALL tables!")
    print("Proceeding with deletion...")
    
    # Delete tasks from each table
    total_deleted = 0
    for table in task_tables:
        deleted = delete_all_tasks_from_table(table)
        total_deleted += deleted
    
    print(f"\nTask deletion process completed. Deleted {total_deleted} tasks in total.")
