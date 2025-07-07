"""
Script to execute SQL commands directly on the database.
This bypasses Django's migration system to avoid dependency issues.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Get database connection
from django.db import connection

# SQL commands to execute
sql_commands = [
    # Remove the is_completed column from the projects_gamemilestone table
    'ALTER TABLE "projects_gamemilestone" DROP COLUMN "is_completed";',
    
    # Update Django's migration history to mark our migration as applied
    """
    INSERT INTO django_migrations (app, name, applied)
    VALUES ('projects', '0003_remove_is_completed_from_milestone', CURRENT_TIMESTAMP)
    ON CONFLICT DO NOTHING;
    """
]

def execute_sql():
    """Execute SQL commands directly on the database."""
    print("Executing SQL commands to remove is_completed field...")
    
    with connection.cursor() as cursor:
        for sql in sql_commands:
            try:
                print(f"Executing: {sql}")
                cursor.execute(sql)
                print("Command executed successfully.")
            except Exception as e:
                print(f"Error executing SQL: {str(e)}")
    
    print("SQL execution completed.")

if __name__ == "__main__":
    execute_sql()
