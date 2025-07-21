#!/usr/bin/env python
"""
Script to generate SQL commands for resetting a PythonAnywhere MySQL database
and mark all migrations as applied.

This script:
1. Prints SQL commands to reset the database (to be run in PythonAnywhere's MySQL console)
2. Marks all migrations as applied in Django's migration records
"""
import os
import sys
import django
from django.db import connection
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def get_database_name():
    """Get the database name from Django settings."""
    return settings.DATABASES['default']['NAME']

def print_reset_sql_commands():
    """Print SQL commands to reset the database."""
    db_name = get_database_name()
    
    print("\n=== SQL COMMANDS TO RUN IN PYTHONANYWHERE MYSQL CONSOLE ===")
    print("-- These commands will reset your database")
    print("-- Copy and paste them into the MySQL console")
    print(f"DROP DATABASE `{db_name}`;")
    print(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("-- After running these commands, return to the bash console")
    print("-- and run 'python manage.py migrate --fake-initial'")
    print("-- Then run this script again with the --mark-migrations flag")
    print("==========================================================\n")

def mark_all_migrations_applied():
    """Mark all migrations as applied in Django's migration records."""
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.recorder import MigrationRecorder
    
    # Get all migrations
    loader = MigrationLoader(connection)
    recorder = MigrationRecorder(connection)
    
    # Clear existing migration records
    recorder.migration_qs.all().delete()
    
    # Mark all migrations as applied
    applied = 0
    for (app_label, migration_name) in loader.disk_migrations.keys():
        if migration_name != '__first__':
            recorder.record_applied(app_label, migration_name)
            applied += 1
    
    print(f"Marked {applied} migrations as applied")
    print("\nYour database should now be ready to use.")
    print("Restart your web app with:")
    print("touch /var/www/R1D3_pythonanywhere_com_wsgi.py")

def main():
    """Main function to run the script."""
    if len(sys.argv) > 1 and sys.argv[1] == '--mark-migrations':
        print("Marking all migrations as applied...")
        mark_all_migrations_applied()
    else:
        db_name = get_database_name()
        print(f"Database name: {db_name}")
        print("\nThis script will help you reset your PythonAnywhere MySQL database.")
        print("It will generate SQL commands for you to run in the MySQL console.")
        print("\nFollow these steps:")
        print("1. Run this script to get the SQL commands")
        print("2. Go to the PythonAnywhere MySQL console and run the commands")
        print("3. Run 'python manage.py migrate --fake-initial'")
        print("4. Run this script again with the --mark-migrations flag")
        print("5. Restart your web app")
        
        print_reset_sql_commands()

if __name__ == "__main__":
    main()
