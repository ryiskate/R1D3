#!/usr/bin/env python3
"""
Add text-based ownership fields directly to database
"""
import os
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.conf import settings

def add_text_fields():
    """Add text fields to all task tables"""
    db_path = settings.DATABASES['default']['NAME']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = [
        'projects_gamedevelopmenttask',
        'projects_educationtask',
        'projects_socialmediatask',
        'projects_arcadetask',
        'projects_themeparktask',
        'projects_r1d3task',
        'projects_gametask',
        'indie_news_indienewstask',
    ]
    
    fields_to_add = [
        ('created_by_name', 'VARCHAR(100) DEFAULT ""'),
        ('assigned_to_name', 'VARCHAR(100) DEFAULT ""'),
    ]
    
    print("🔧 Adding text-based ownership fields to task tables...")
    
    for table in tables:
        print(f"\n📋 Processing table: {table}")
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"  ⚠️  Table {table} does not exist, skipping...")
            continue
        
        for field_name, field_type in fields_to_add:
            try:
                # Check if column already exists
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if field_name in columns:
                    print(f"  ✓ Field {field_name} already exists")
                else:
                    # Add the column
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type}")
                    print(f"  ✅ Added field: {field_name}")
            except Exception as e:
                print(f"  ❌ Error adding {field_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Text-based ownership fields added successfully!")
    print("\n📝 Next steps:")
    print("1. The fields are now in the database")
    print("2. You can start using them in forms and views")

if __name__ == "__main__":
    add_text_fields()
