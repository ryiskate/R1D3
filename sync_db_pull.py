#!/usr/bin/env python3
"""
Pull database changes from GitHub
Usage: python sync_db_pull.py
"""
import subprocess
import sys

def sync_db_pull():
    """Pull database changes from GitHub"""
    try:
        print("📥 Pulling latest changes from GitHub...")
        subprocess.run(['git', 'pull'], check=True)
        print("✅ Database updated successfully!")
        print("\n⚠️  Important: Restart the Django server to use the updated database")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pulling database: {e}")
        print("\n💡 Tip: Make sure you've committed any local changes first")
        sys.exit(1)

if __name__ == "__main__":
    sync_db_pull()
