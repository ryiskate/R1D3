"""
Script to delete task ID 23 from the projects_gamedevelopmenttask table
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.db import connection

def delete_task(task_id, table_name):
    """Delete a task from the specified table"""
    with connection.cursor() as cursor:
        try:
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
    task_id = 23
    table_name = "projects_gamedevelopmenttask"
    
    print(f"Attempting to delete task ID {task_id} from {table_name}...")
    delete_task(task_id, table_name)
    print("Task deletion process completed.")
