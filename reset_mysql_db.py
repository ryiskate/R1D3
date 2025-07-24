#!/usr/bin/env python
"""
Script to reset MySQL database on PythonAnywhere and create a fresh schema.
This script:
1. Generates SQL commands to drop and recreate the database
2. Marks all migrations as applied
3. Provides instructions for running the commands in the MySQL console
"""
import os
import sys
import django
import argparse
from django.db import connection
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def generate_reset_sql(database_name):
    """Generate SQL commands to drop and recreate the database."""
    # Escape database name with backticks for MySQL
    escaped_db_name = f"`{database_name}`"
    
    sql_commands = [
        f"DROP DATABASE {escaped_db_name};",
        f"CREATE DATABASE {escaped_db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    ]
    
    return sql_commands

def mark_all_migrations_as_applied():
    """Mark all migrations as applied without running them."""
    from django.db.migrations.recorder import MigrationRecorder
    from django.apps import apps
    
    recorder = MigrationRecorder(connection)
    
    # Get all migration files
    for app_config in apps.get_app_configs():
        if app_config.models_module is None:
            continue
            
        app_label = app_config.label
        migrations_dir = os.path.join(app_config.path, 'migrations')
        
        if not os.path.isdir(migrations_dir):
            continue
            
        # Get all migration files
        migration_files = os.listdir(migrations_dir)
        for filename in migration_files:
            if filename.endswith('.py') and not filename.startswith('__'):
                migration_name = filename[:-3]  # Remove .py extension
                
                # Skip __init__.py and other non-migration files
                if migration_name == '__init__' or migration_name == '__pycache__':
                    continue
                    
                # Mark migration as applied if not already
                if not recorder.migration_qs.filter(app=app_label, name=migration_name).exists():
                    recorder.record_applied(app_label, migration_name)
                    print(f"Marked {app_label}.{migration_name} as applied")

def extract_database_info_from_url(database_url):
    """Extract database name from DATABASE_URL."""
    if not database_url or not database_url.startswith('mysql://'):
        return None
        
    # Parse the database URL
    # Format: mysql://username:password@host/database_name
    parts = database_url.split('/')
    if len(parts) < 4:
        return None
        
    database_name = parts[-1].split('?')[0]  # Remove any query parameters
    return database_name

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Reset MySQL database and mark migrations')
    parser.add_argument('--mark-migrations', action='store_true', help='Mark all migrations as applied')
    parser.add_argument('--database', help='Database name (default: from settings)')
    
    args = parser.parse_args()
    
    # Get database name from settings or argument
    database_name = args.database
    if not database_name:
        # Try to get from DATABASE_URL environment variable
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            database_name = extract_database_info_from_url(database_url)
        
        # If still not found, try to get from Django settings
        if not database_name and hasattr(settings, 'DATABASES') and 'default' in settings.DATABASES:
            database_settings = settings.DATABASES['default']
            if 'NAME' in database_settings:
                database_name = database_settings['NAME']
    
    if not database_name:
        print("Error: Could not determine database name.")
        print("Please specify with --database or set DATABASE_URL environment variable.")
        return
    
    if args.mark_migrations:
        print(f"Marking all migrations as applied...")
        mark_all_migrations_as_applied()
        print("All migrations have been marked as applied.")
    else:
        print(f"Generating SQL commands to reset database: {database_name}")
        sql_commands = generate_reset_sql(database_name)
        
        print("\n=== INSTRUCTIONS FOR RESETTING MYSQL DATABASE ===")
        print("1. Go to the PythonAnywhere dashboard")
        print("2. Click on the 'Databases' tab")
        print("3. Click on 'MySQL console'")
        print("4. Run these SQL commands:")
        print("\n```sql")
        for cmd in sql_commands:
            print(cmd)
        print("```\n")
        
        print("5. After resetting the database, run migrations:")
        print("   python manage.py migrate --fake-initial")
        
        print("6. Then mark all migrations as applied:")
        print("   python reset_mysql_db.py --mark-migrations")
        
        print("7. Finally, restart your web app:")
        print("   touch /var/www/R1D3_pythonanywhere_com_wsgi.py")
        print("===========================================")

if __name__ == "__main__":
    main()
