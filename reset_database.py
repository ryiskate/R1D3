#!/usr/bin/env python3
"""
Reset the database - backup old one and create fresh
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def reset_database():
    """Backup old database and create fresh one"""
    db_path = Path(__file__).parent / 'db.sqlite3'
    
    if db_path.exists():
        # Create backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = Path(__file__).parent / f'db_backup_{timestamp}.sqlite3'
        
        print(f"📦 Backing up existing database to: {backup_path.name}")
        shutil.copy2(db_path, backup_path)
        
        # Delete old database
        db_path.unlink()
        print("🗑️  Deleted old database")
    else:
        print("ℹ️  No existing database found")
    
    print("✅ Database reset complete!")
    print("\n📝 Next steps:")
    print("1. Run: python manage.py migrate")
    print("2. Run: python manage.py createsuperuser")
    print("3. Run: python run_server.py")

if __name__ == "__main__":
    confirm = input("⚠️  This will backup and delete your current database. Continue? (yes/no): ").strip().lower()
    if confirm == 'yes':
        reset_database()
    else:
        print("❌ Cancelled")
