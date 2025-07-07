"""
Script to fix Django migration dependency issues by manipulating the django_migrations table.
This script works with MySQL databases (like those on PythonAnywhere).
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaR1D3.settings')

try:
    django.setup()
except ModuleNotFoundError:
    # Try alternative settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'r1d3.settings'
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
        projects_team = cursor.fetchone()
        
        cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='strategy' AND name='0001_initial'")
        strategy_initial = cursor.fetchone()
        
        cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='projects' AND name='0001_initial'")
        projects_initial = cursor.fetchone()
        
        if not indie_news:
            print("Could not find indie_news.0002_indienewstask_team migration!")
        else:
            print(f"Found indie_news.0002_indienewstask_team with ID {indie_news[0]} applied at {indie_news[3]}")
        
        if not projects_team:
            print("Could not find projects.0015_team_arcadetask_team_educationtask_team_and_more migration!")
        else:
            print(f"Found projects.0015_team... with ID {projects_team[0]} applied at {projects_team[3]}")
        
        if not strategy_initial:
            print("Could not find strategy.0001_initial migration!")
        else:
            print(f"Found strategy.0001_initial with ID {strategy_initial[0]} applied at {strategy_initial[3]}")
        
        if not projects_initial:
            print("Could not find projects.0001_initial migration!")
        else:
            print(f"Found projects.0001_initial with ID {projects_initial[0]} applied at {projects_initial[3]}")
        
        # Update the timestamps to fix the order
        now = datetime.now()
        
        # Create timestamps with proper ordering
        # strategy.0001_initial should be first
        # projects.0001_initial should be second
        # projects.0015_team... should be third
        # indie_news.0002_indienewstask_team should be fourth
        
        if strategy_initial:
            strategy_time = now - timedelta(minutes=30)
            print(f"Setting strategy.0001_initial timestamp to: {strategy_time}")
            cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                          [strategy_time, strategy_initial[0]])
        
        if projects_initial:
            projects_initial_time = now - timedelta(minutes=25)
            print(f"Setting projects.0001_initial timestamp to: {projects_initial_time}")
            cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                          [projects_initial_time, projects_initial[0]])
        
        if projects_team:
            projects_team_time = now - timedelta(minutes=20)
            print(f"Setting projects.0015_team... timestamp to: {projects_team_time}")
            cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                          [projects_team_time, projects_team[0]])
        
        if indie_news:
            indie_news_time = now - timedelta(minutes=15)
            print(f"Setting indie_news.0002_indienewstask_team timestamp to: {indie_news_time}")
            cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                          [indie_news_time, indie_news[0]])
        
        print("Migration timestamps updated successfully!")

if __name__ == "__main__":
    print("Before fixing:")
    check_migrations()
    
    fix_migration_order()
    
    print("\nAfter fixing:")
    check_migrations()
    
    print("\nNow you can run 'python manage.py migrate' to apply any pending migrations.")
