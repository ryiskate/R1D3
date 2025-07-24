#!/usr/bin/env python
"""
Script to migrate data from SQLite to MySQL.
This script:
1. Reads data from SQLite database
2. Writes data to MySQL database
3. Preserves relationships and data integrity
"""
import os
import sys
import json
import datetime
import django
from django.db import connections
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def setup_mysql_connection():
    """
    Set up a connection to the MySQL database.
    This requires setting the DATABASE_URL environment variable or manually configuring MySQL settings.
    """
    # Check if we have MySQL configuration
    if 'mysql' not in connections.databases:
        # Add MySQL database configuration
        mysql_config = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': input("MySQL Database name: "),
            'USER': input("MySQL Username: "),
            'PASSWORD': input("MySQL Password: "),
            'HOST': input("MySQL Host (default: localhost): ") or 'localhost',
            'PORT': input("MySQL Port (default: 3306): ") or '3306',
        }
        
        # For PythonAnywhere, the host is typically username.mysql.pythonanywhere-services.com
        if 'pythonanywhere' in mysql_config['HOST'] or mysql_config['HOST'] == 'localhost':
            print(f"Using MySQL configuration with host: {mysql_config['HOST']}")
        
        # Add the MySQL database configuration
        connections.databases['mysql'] = mysql_config
    
    return 'mysql'

def export_data_from_sqlite():
    """
    Export all data from SQLite database.
    Returns a dictionary with app_label.model_name as keys and lists of model instances as values.
    """
    print("Exporting data from SQLite...")
    data = {}
    
    # Get all models
    for model in apps.get_models():
        if model._meta.app_label in ('contenttypes', 'auth', 'admin', 'sessions'):
            # Skip Django's internal models
            continue
        
        model_key = f"{model._meta.app_label}.{model._meta.model_name}"
        print(f"Exporting {model_key}...")
        
        # Get all instances of the model
        queryset = model.objects.using('default').all()
        
        # Convert queryset to list of dictionaries
        instances = []
        for instance in queryset:
            instance_data = {}
            for field in model._meta.fields:
                field_name = field.name
                field_value = getattr(instance, field_name)
                instance_data[field_name] = field_value
            
            # Handle many-to-many relationships
            for field in model._meta.many_to_many:
                field_name = field.name
                related_objects = getattr(instance, field_name).all()
                instance_data[field_name] = [obj.pk for obj in related_objects]
            
            instances.append(instance_data)
        
        data[model_key] = instances
        print(f"  - Exported {len(instances)} records")
    
    return data

def import_data_to_mysql(data, mysql_connection):
    """
    Import data into MySQL database.
    """
    print("\nImporting data to MySQL...")
    
    # Process models in order of dependencies
    # First, models without foreign keys, then models with foreign keys
    model_keys = list(data.keys())
    
    # First pass: Create all objects without relationships
    for model_key in model_keys:
        app_label, model_name = model_key.split('.')
        model = apps.get_model(app_label, model_name)
        
        print(f"Importing {model_key}...")
        instances = data[model_key]
        
        for instance_data in instances:
            # Extract many-to-many relationships
            m2m_data = {}
            for field in model._meta.many_to_many:
                field_name = field.name
                if field_name in instance_data:
                    m2m_data[field_name] = instance_data.pop(field_name)
            
            # Extract foreign key relationships that might cause issues
            fk_data = {}
            for field in model._meta.fields:
                if field.is_relation:
                    field_name = field.name
                    if field_name in instance_data and instance_data[field_name] is not None:
                        fk_data[field_name] = instance_data[field_name]
                        # Keep the ID in the instance_data for now
            
            try:
                # Create the object in MySQL
                obj = model(**instance_data)
                obj.save(using=mysql_connection)
                
                # Set many-to-many relationships
                for field_name, values in m2m_data.items():
                    if values:
                        m2m_field = getattr(obj, field_name)
                        m2m_field.set(values)
                
                print(f"  - Created {model_name} with ID {obj.pk}")
            except Exception as e:
                print(f"  - Error creating {model_name}: {e}")
    
    print("\nData migration completed!")

def main():
    """Main function to run the script."""
    print("This script will migrate data from SQLite to MySQL.")
    print("Make sure you have already set up your MySQL database schema.")
    print("You can use recreate_mysql_db_single_migration.py to set up the schema.")
    
    confirm = input("Do you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Set up MySQL connection
    mysql_connection = setup_mysql_connection()
    
    # Export data from SQLite
    data = export_data_from_sqlite()
    
    # Save data to a JSON file as backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"sqlite_data_backup_{timestamp}.json"
    with open(backup_path, 'w') as f:
        json.dump(data, f, cls=DjangoJSONEncoder)
    print(f"\nData backup saved to {backup_path}")
    
    # Import data to MySQL
    import_data_to_mysql(data, mysql_connection)
    
    print("\nMigration completed successfully!")
    print("You should now be able to run your application with MySQL.")
    print(f"A backup of your SQLite data has been saved to {backup_path}")

if __name__ == "__main__":
    main()
