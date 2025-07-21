#!/usr/bin/env python
"""
Script to recreate the database with a single migration.
This approach:
1. Creates a backup of the current database
2. Creates a new database with the current schema
3. Copies essential data from the backup
4. Updates Django's migration records to mark all migrations as applied
"""
import os
import sys
import sqlite3
import shutil
import datetime
import django
from django.db import connection
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def backup_database():
    """Create a backup of the current database."""
    db_path = settings.DATABASES['default']['NAME']
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    
    print(f"Creating backup of database at: {backup_path}")
    shutil.copy2(db_path, backup_path)
    
    return backup_path

def get_table_schema(conn, table_name):
    """Get the CREATE TABLE statement for a table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    return result[0] if result else None

def get_all_tables(conn):
    """Get a list of all tables in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    return [row[0] for row in cursor.fetchall()]

def copy_table_data(source_conn, dest_conn, table_name):
    """Copy data from one table to another."""
    source_cursor = source_conn.cursor()
    dest_cursor = dest_conn.cursor()
    
    # Get column names
    source_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in source_cursor.fetchall()]
    
    if not columns:
        print(f"  No columns found for table {table_name}")
        return 0
    
    # Check if the destination table has the same columns
    dest_cursor.execute(f"PRAGMA table_info({table_name});")
    dest_columns = [col[1] for col in dest_cursor.fetchall()]
    
    # Find common columns
    common_columns = [col for col in columns if col in dest_columns]
    
    if not common_columns:
        print(f"  No common columns found for table {table_name}")
        return 0
    
    # Get data from source table
    source_cursor.execute(f"SELECT {', '.join(common_columns)} FROM {table_name};")
    rows = source_cursor.fetchall()
    
    if not rows:
        print(f"  No data found in table {table_name}")
        return 0
    
    # Insert data into destination table
    placeholders = ', '.join(['?' for _ in common_columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(common_columns)}) VALUES ({placeholders});"
    
    try:
        dest_cursor.executemany(insert_sql, rows)
        dest_conn.commit()
        return len(rows)
    except sqlite3.Error as e:
        print(f"  Error copying data for table {table_name}: {e}")
        return 0

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
    
    return applied

def recreate_database():
    """Recreate the database with the current schema."""
    # Backup the current database
    backup_path = backup_database()
    
    # Connect to the backup database
    backup_conn = sqlite3.connect(backup_path)
    
    # Get all tables from the backup
    tables = get_all_tables(backup_conn)
    print(f"Found {len(tables)} tables in the backup database")
    
    # Get the current database path
    db_path = settings.DATABASES['default']['NAME']
    
    # Close the Django connection
    connection.close()
    
    # Create a new empty database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Run migrations to create the schema
    print("\nRunning migrations to create the schema...")
    os.system(f"python manage.py migrate --fake-initial")
    
    # Connect to the new database
    new_conn = sqlite3.connect(db_path)
    
    # Copy data from the backup to the new database
    print("\nCopying data from backup to new database...")
    total_copied = 0
    for table in tables:
        try:
            rows_copied = copy_table_data(backup_conn, new_conn, table)
            if rows_copied > 0:
                print(f"  Copied {rows_copied} rows from table {table}")
                total_copied += rows_copied
        except Exception as e:
            print(f"  Error processing table {table}: {e}")
    
    # Close connections
    backup_conn.close()
    new_conn.close()
    
    # Reconnect Django
    connection.connect()
    
    # Mark all migrations as applied
    migrations_applied = mark_all_migrations_applied()
    
    print(f"\nDatabase recreation completed:")
    print(f"  - Backup created at: {backup_path}")
    print(f"  - Copied {total_copied} rows of data")
    print(f"  - Marked {migrations_applied} migrations as applied")
    print("\nYou should now be able to run your application without migration errors.")

def main():
    """Main function to run the script."""
    print("This script will recreate your database with a single migration.")
    print("WARNING: This is a destructive operation. Make sure you have a backup.")
    print("The script will create a backup automatically, but it's always good to have an extra one.")
    
    confirm = input("Do you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    recreate_database()

if __name__ == "__main__":
    main()
