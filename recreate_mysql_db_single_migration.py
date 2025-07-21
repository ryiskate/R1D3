#!/usr/bin/env python
"""
Script to recreate a MySQL database with a single migration.
This approach:
1. Creates a backup of the current database using mysqldump
2. Drops and recreates the database
3. Runs migrations to create the schema
4. Marks all migrations as applied
"""
import os
import sys
import subprocess
import datetime
import django
from django.db import connection
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def get_mysql_credentials():
    """Get MySQL credentials from Django settings."""
    db_settings = settings.DATABASES['default']
    credentials = {
        'host': db_settings.get('HOST', 'localhost'),
        'user': db_settings.get('USER', ''),
        'password': db_settings.get('PASSWORD', ''),
        'name': db_settings.get('NAME', ''),
    }
    
    # Only add port if it's not empty
    port = db_settings.get('PORT')
    if port:
        credentials['port'] = port
        
    return credentials

def backup_database(credentials):
    """Create a backup of the current database using mysqldump."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"db_backup_{timestamp}.sql"
    
    # Build mysqldump command
    cmd = [
        'mysqldump',
        f"--host={credentials['host']}",
        f"--user={credentials['user']}",
    ]
    
    # Add port only if specified
    if 'port' in credentials and credentials['port']:
        cmd.append(f"--port={credentials['port']}")
    
    if credentials['password']:
        cmd.append(f"--password={credentials['password']}")
    
    cmd.append(credentials['name'])
    
    print(f"Creating backup of database at: {backup_path}")
    
    # Execute mysqldump command
    with open(backup_path, 'w') as f:
        process = subprocess.Popen(cmd, stdout=f)
        process.wait()
    
    if process.returncode != 0:
        print("Error creating backup. Please check your MySQL credentials.")
        return None
    
    return backup_path

def drop_and_recreate_database(credentials):
    """Drop and recreate the database."""
    # Build MySQL command
    mysql_cmd = [
        'mysql',
        f"--host={credentials['host']}",
        f"--user={credentials['user']}",
    ]
    
    # Add port only if specified
    if 'port' in credentials and credentials['port']:
        mysql_cmd.append(f"--port={credentials['port']}")
    
    if credentials['password']:
        mysql_cmd.append(f"--password={credentials['password']}")
    
    # Drop and recreate database
    drop_cmd = mysql_cmd + ['-e', f"DROP DATABASE IF EXISTS {credentials['name']};"]
    create_cmd = mysql_cmd + ['-e', f"CREATE DATABASE {credentials['name']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"]
    
    print(f"Dropping database {credentials['name']}...")
    subprocess.run(drop_cmd)
    
    print(f"Creating database {credentials['name']}...")
    subprocess.run(create_cmd)

def run_migrations():
    """Run migrations to create the schema."""
    print("\nRunning migrations to create the schema...")
    os.system(f"python manage.py migrate --fake-initial")

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
    # Get MySQL credentials
    credentials = get_mysql_credentials()
    
    # Backup the current database
    backup_path = backup_database(credentials)
    if not backup_path:
        return
    
    # Close the Django connection
    connection.close()
    
    # Drop and recreate the database
    drop_and_recreate_database(credentials)
    
    # Run migrations to create the schema
    run_migrations()
    
    # Mark all migrations as applied
    migrations_applied = mark_all_migrations_applied()
    
    print(f"\nDatabase recreation completed:")
    print(f"  - Backup created at: {backup_path}")
    print(f"  - Marked {migrations_applied} migrations as applied")
    print("\nYou should now be able to run your application without migration errors.")
    print("\nNOTE: This script does NOT restore data from the backup.")
    print("If you need to restore specific data, you can use the backup file and import")
    print("selected tables or data using MySQL tools.")

def main():
    """Main function to run the script."""
    print("This script will recreate your MySQL database with a single migration.")
    print("WARNING: This is a destructive operation. All data will be lost.")
    print("The script will create a backup automatically, but it's always good to have an extra one.")
    
    confirm = input("Do you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    recreate_database()

if __name__ == "__main__":
    main()
