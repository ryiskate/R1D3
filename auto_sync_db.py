#!/usr/bin/env python3
"""
Auto-sync database to GitHub when changes are detected
Usage: python auto_sync_db.py

This script watches the database file and automatically pushes changes to GitHub
Press Ctrl+C to stop
"""
import time
import os
import hashlib
import subprocess
from datetime import datetime

DB_FILE = 'db.sqlite3'
CHECK_INTERVAL = 5  # Check every 5 seconds

def get_file_hash(filepath):
    """Get MD5 hash of file to detect changes"""
    if not os.path.exists(filepath):
        return None
    
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_to_github():
    """Sync database to GitHub"""
    try:
        # Add the database file
        subprocess.run(['git', 'add', 'db.sqlite3'], check=True, capture_output=True)
        
        # Create commit with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"🔄 Auto-sync database: {timestamp}"
        
        result = subprocess.run(['git', 'commit', '-m', commit_message], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Push to remote
            subprocess.run(['git', 'push'], check=True, capture_output=True)
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Database synced to GitHub")
            return True
        else:
            # No changes to commit
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error syncing: {e}")
        return False

def auto_sync():
    """Watch database and auto-sync on changes"""
    print(f"👀 Watching {DB_FILE} for changes...")
    print(f"🔄 Will sync to GitHub every {CHECK_INTERVAL} seconds if changes detected")
    print("⏸️  Press Ctrl+C to stop\n")
    
    last_hash = get_file_hash(DB_FILE)
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            
            current_hash = get_file_hash(DB_FILE)
            
            if current_hash and current_hash != last_hash:
                print(f"📝 [{datetime.now().strftime('%H:%M:%S')}] Database changes detected...")
                if sync_to_github():
                    last_hash = current_hash
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Auto-sync stopped")

if __name__ == "__main__":
    auto_sync()
