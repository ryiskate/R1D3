#!/usr/bin/env python3
"""
Push database changes to GitHub
Usage: python sync_db_push.py
"""
import subprocess
import sys
from datetime import datetime

def sync_db_push():
    """Push database changes to GitHub"""
    try:
        # Add the database file
        print("📦 Adding database to git...")
        subprocess.run(['git', 'add', 'db.sqlite3'], check=True)
        
        # Create commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"🔄 Database sync: {timestamp}"
        
        print(f"💾 Committing changes: {commit_message}")
        result = subprocess.run(['git', 'commit', '-m', commit_message], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 or "nothing to commit" in result.stdout:
            # Push to remote
            print("📤 Pushing to GitHub...")
            subprocess.run(['git', 'push'], check=True)
            print("✅ Database synced successfully!")
        else:
            print("ℹ️  No changes to sync")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error syncing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_db_push()
