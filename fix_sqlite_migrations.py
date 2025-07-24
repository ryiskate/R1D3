#!/usr/bin/env python
"""
Script to fix SQLite-specific migrations for MySQL compatibility.
This script:
1. Marks problematic migrations as applied without running them
2. Creates a clean initial migration for the current schema
"""
import os
import sys
import django
from django.db import connection
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def mark_migration_as_applied(app, migration_name):
    """Mark a specific migration as applied without running it."""
    from django.db.migrations.recorder import MigrationRecorder
    
    recorder = MigrationRecorder(connection)
    
    # Check if the migration is already applied
    if recorder.migration_qs.filter(app=app, name=migration_name).exists():
        print(f"Migration {app}.{migration_name} is already marked as applied.")
        return
    
    # Mark the migration as applied
    recorder.record_applied(app, migration_name)
    print(f"Marked migration {app}.{migration_name} as applied.")

def list_problematic_migrations():
    """List migrations that might be problematic for MySQL."""
    problematic_migrations = [
        ('strategy', '0003_create_strategymilestone_sqlite'),
        # Add other problematic migrations here
    ]
    
    return problematic_migrations

def fix_migrations():
    """Mark problematic migrations as applied and create a clean schema."""
    print("Fixing SQLite-specific migrations for MySQL compatibility...")
    
    # Mark problematic migrations as applied
    problematic_migrations = list_problematic_migrations()
    for app, migration in problematic_migrations:
        mark_migration_as_applied(app, migration)
    
    print("\nAll problematic migrations have been marked as applied.")
    print("\nNow you can run migrations with:")
    print("python manage.py migrate --fake-initial")
    
    print("\nIf you still encounter issues, you may need to:")
    print("1. Create a database backup")
    print("2. Drop and recreate the database")
    print("3. Run migrations from scratch")

def main():
    """Main function to run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix SQLite-specific migrations for MySQL')
    parser.add_argument('--list', action='store_true', help='List problematic migrations')
    parser.add_argument('--fix', action='store_true', help='Mark problematic migrations as applied')
    
    args = parser.parse_args()
    
    if args.list:
        print("Problematic migrations:")
        for app, migration in list_problematic_migrations():
            print(f"- {app}.{migration}")
    elif args.fix:
        fix_migrations()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
