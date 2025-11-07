#!/usr/bin/env python3
"""
Fix migration history by clearing it and re-faking all applied migrations
"""
import sqlite3
from pathlib import Path

def fix_migration_history():
    """Clear and rebuild migration history"""
    db_path = Path(__file__).parent / 'db.sqlite3'
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Fixing migration history...")
    
    try:
        # Clear all migration history
        cursor.execute("DELETE FROM django_migrations")
        conn.commit()
        print("✅ Cleared migration history")
        
        # Now fake all migrations in correct order
        print("\n📝 Re-faking migrations in correct order...")
        
        migrations_order = [
            ('contenttypes', '0001_initial'),
            ('auth', '0001_initial'),
            ('contenttypes', '0002_remove_content_type_name'),
            ('auth', '0002_alter_permission_name_max_length'),
            ('auth', '0003_alter_user_email_max_length'),
            ('auth', '0004_alter_user_username_opts'),
            ('auth', '0005_alter_user_last_login_null'),
            ('auth', '0006_require_contenttypes_0002'),
            ('auth', '0007_alter_validators_add_error_messages'),
            ('auth', '0008_alter_user_username_max_length'),
            ('auth', '0009_alter_user_last_name_max_length'),
            ('auth', '0010_alter_group_name_max_length'),
            ('auth', '0011_update_proxy_permissions'),
            ('auth', '0012_alter_user_first_name_max_length'),
            ('strategy', '0001_initial'),
            ('projects', '0001_initial'),
        ]
        
        for app, migration in migrations_order:
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, datetime('now'))",
                (app, migration)
            )
            print(f"  ✓ Faked {app}.{migration}")
        
        conn.commit()
        print("\n✅ Migration history fixed!")
        print("\n📝 Next step:")
        print("Run: python manage.py migrate")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_migration_history()
