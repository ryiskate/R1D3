"""
Script to delete specific tasks from legacy task tables
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.db import connection

def delete_task_from_table(table_name, task_id):
    """Delete a task from the specified table"""
    with connection.cursor() as cursor:
        try:
            # First check if the task exists
            cursor.execute(f"SELECT id FROM {table_name} WHERE id = %s", [task_id])
            row = cursor.fetchone()
            if not row:
                print(f"Task ID {task_id} not found in table {table_name}")
                return False
                
            # Delete the task
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

if __name__ == "__main__":
    # Task IDs to delete and their corresponding tables
    tasks_to_delete = [
        (92, "projects_gametask"),
        (98, "projects_r1d3task")  # We'll try this table for task 98
    ]
    
    print("Starting task deletion process...")
    
    for task_id, table_name in tasks_to_delete:
        print(f"\nAttempting to delete task ID {task_id} from {table_name}...")
        delete_task_from_table(table_name, task_id)
    
    print("\nTask deletion process completed.")
