import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'r1d3.settings')
django.setup()

# Import Django models after setup
from django.db import connection

# Query the django_migrations table
with connection.cursor() as cursor:
    cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY app, applied")
    rows = cursor.fetchall()
    
    print("Migration records in the database:")
    print("-" * 80)
    print(f"{'App':<20} {'Migration Name':<50} {'Applied At'}")
    print("-" * 80)
    
    for row in rows:
        app, name, applied = row
        print(f"{app:<20} {name:<50} {applied}")
    
    # Specifically check the problematic migrations
    print("\n\nChecking problematic migrations:")
    print("-" * 80)
    cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app='indie_news' AND name='0002_indienewstask_team'")
    indie_news = cursor.fetchone()
    if indie_news:
        print(f"indie_news.0002_indienewstask_team applied at: {indie_news[2]}")
    else:
        print("indie_news.0002_indienewstask_team not found in migration history")
    
    cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app='projects' AND name='0015_team_arcadetask_team_educationtask_team_and_more'")
    projects = cursor.fetchone()
    if projects:
        print(f"projects.0015_team_arcadetask_team_educationtask_team_and_more applied at: {projects[2]}")
    else:
        print("projects.0015_team_arcadetask_team_educationtask_team_and_more not found in migration history")
