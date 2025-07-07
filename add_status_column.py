import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
print('Setting up Django environment...')
django.setup()
print('Django setup complete.')

from django.db import connection
print('Imported connection from django.db')

print('Adding status column to projects_gamemilestone table...')

try:
    with connection.cursor() as cursor:
        # Check if the status column already exists
        cursor.execute("PRAGMA table_info(projects_gamemilestone)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'status' not in column_names:
            print('Status column does not exist. Adding it now...')
            # Add the status column
            cursor.execute("ALTER TABLE projects_gamemilestone ADD COLUMN status varchar(20) DEFAULT 'not_started'")
            print('Status column added successfully.')
            
            # Update the status values based on is_completed
            cursor.execute("UPDATE projects_gamemilestone SET status = 'completed' WHERE is_completed = 1")
            cursor.execute("UPDATE projects_gamemilestone SET status = 'in_progress' WHERE is_completed = 0")
            print('Status values updated based on is_completed field.')
        else:
            print('Status column already exists.')
            
    print('Operation completed successfully.')
except Exception as e:
    print(f'Error: {e}')
