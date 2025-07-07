import os
import sys
import django
import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment - adjust this to your actual settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaR1D3.settings')
django.setup()

# Import Django models after setup
from django.db import connection

def check_migrations():
    """Check the current migration state"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('indie_news', 'projects', 'strategy') ORDER BY applied")
        rows = cursor.fetchall()
        
        print("Relevant migration records in the database:")
        print("-" * 80)
        print(f"{'App':<20} {'Migration Name':<50} {'Applied At'}")
        print("-" * 80)
        
        for row in rows:
            app, name, applied = row
            print(f"{app:<20} {name:<50} {applied}")

def fix_migration_order():
    """Fix the migration order by updating the timestamps"""
    with connection.cursor() as cursor:
        # First, check if the problematic migrations exist
        cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='indie_news' AND name='0002_indienewstask_team'")
        indie_news = cursor.fetchone()
        
        cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='projects' AND name='0015_team_arcadetask_team_educationtask_team_and_more'")
        projects = cursor.fetchone()
        
        if not indie_news or not projects:
            print("Could not find one or both of the problematic migrations!")
            return
        
        print(f"Found indie_news migration with ID {indie_news[0]} applied at {indie_news[3]}")
        print(f"Found projects migration with ID {projects[0]} applied at {projects[3]}")
        
        # Update the timestamps to fix the order
        # Make projects migration appear to be applied earlier
        now = datetime.datetime.now()
        projects_time = now - datetime.timedelta(minutes=5)  # 5 minutes earlier
        indie_news_time = now
        
        # Format timestamps for SQLite
        projects_timestamp = projects_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        indie_news_timestamp = indie_news_time.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        print(f"Setting projects migration timestamp to: {projects_timestamp}")
        print(f"Setting indie_news migration timestamp to: {indie_news_timestamp}")
        
        # Update the timestamps
        cursor.execute("UPDATE django_migrations SET applied = ? WHERE id = ?", 
                      [projects_timestamp, projects[0]])
        
        cursor.execute("UPDATE django_migrations SET applied = ? WHERE id = ?", 
                      [indie_news_timestamp, indie_news[0]])
        
        print("Migration timestamps updated successfully!")

if __name__ == "__main__":
    print("Before fixing:")
    check_migrations()
    
    fix_migration_order()
    
    print("\nAfter fixing:")
    check_migrations()
    
    print("\nNow you can run 'python manage.py migrate' to apply any pending migrations.")
