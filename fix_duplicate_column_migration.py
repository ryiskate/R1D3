#!/usr/bin/env python
"""
Script to fix the duplicate column migration issue by:
1. Identifying the table with the duplicate team_id column
2. Checking if the column exists
3. Updating the migration record to mark it as applied
"""
import os
import sys
import sqlite3
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        return any(col[1] == column_name for col in columns)

def list_tables_with_column(column_name):
    """List all tables that have a specific column."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        tables_with_column = []
        for table in tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue
                
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            if any(col[1] == column_name for col in columns):
                tables_with_column.append(table_name)
        
        return tables_with_column

def fix_migration_record(app_label, migration_name):
    """Mark a migration as applied in the migration records."""
    from django.db.migrations.recorder import MigrationRecorder
    
    recorder = MigrationRecorder(connection)
    recorder.record_applied(app_label, migration_name)
    print(f"Marked migration {app_label}.{migration_name} as applied")

def find_problematic_migration():
    """Find the migration that's trying to add the duplicate team_id column."""
    from django.db.migrations.loader import MigrationLoader
    
    loader = MigrationLoader(connection)
    migrations = loader.disk_migrations
    
    for (app_label, migration_name), migration in migrations.items():
        for operation in migration.operations:
            if hasattr(operation, 'name') and operation.name == 'team_id':
                return app_label, migration_name
    
    return None, None

def main():
    """Main function to run the script."""
    print("Checking for tables with team_id column...")
    tables_with_team_id = list_tables_with_column('team_id')
    
    if not tables_with_team_id:
        print("No tables found with team_id column. This is unexpected.")
        return
    
    print(f"Found {len(tables_with_team_id)} tables with team_id column:")
    for table in tables_with_team_id:
        print(f"  - {table}")
    
    # Try to find the problematic migration
    app_label, migration_name = find_problematic_migration()
    
    if app_label and migration_name:
        print(f"\nFound problematic migration: {app_label}.{migration_name}")
        
        confirm = input(f"Do you want to mark this migration as applied? (y/n): ")
        if confirm.lower() == 'y':
            fix_migration_record(app_label, migration_name)
            print("\nMigration record updated. Try running migrations again.")
        else:
            print("\nNo changes made to migration records.")
    else:
        print("\nCould not automatically find the problematic migration.")
        print("You may need to manually inspect your migration files.")
        
        # Offer to fix a specific migration
        app_label = input("Enter the app label for the problematic migration (e.g., 'projects'): ")
        migration_name = input("Enter the migration name (e.g., '0012_add_team_id'): ")
        
        if app_label and migration_name:
            confirm = input(f"Do you want to mark {app_label}.{migration_name} as applied? (y/n): ")
            if confirm.lower() == 'y':
                fix_migration_record(app_label, migration_name)
                print("\nMigration record updated. Try running migrations again.")
            else:
                print("\nNo changes made to migration records.")

if __name__ == "__main__":
    main()
