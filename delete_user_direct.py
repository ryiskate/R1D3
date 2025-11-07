#!/usr/bin/env python3
"""
Delete a user directly from database (bypassing Django's cascade checks)
Usage: python delete_user_direct.py
"""
import sqlite3
import os
from pathlib import Path

def delete_user_direct():
    """Delete a user directly from the auth_user table"""
    # Get database path
    db_path = Path(__file__).parent / 'db.sqlite3'
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all users
    cursor.execute("SELECT id, username, is_superuser, is_staff FROM auth_user")
    users = cursor.fetchall()
    
    if not users:
        print("❌ No users found in database!")
        conn.close()
        return
    
    print("👥 Current users in database:\n")
    for user_id, username, is_super, is_staff in users:
        status = "🔑 Superuser" if is_super else ("👔 Staff" if is_staff else "👤 User")
        print(f"ID: {user_id} | {username} - {status}")
    
    print("\n" + "="*50)
    username = input("\nEnter username to delete (or 'cancel' to exit): ").strip()
    
    if username.lower() == 'cancel':
        print("❌ Cancelled")
        conn.close()
        return
    
    # Check if user exists
    cursor.execute("SELECT id FROM auth_user WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"\n❌ User '{username}' not found!")
        conn.close()
        return
    
    user_id = user[0]
    confirm = input(f"\n⚠️  Are you sure you want to delete '{username}' (ID: {user_id})? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        try:
            # Delete user directly
            cursor.execute("DELETE FROM auth_user WHERE id = ?", (user_id,))
            conn.commit()
            print(f"\n✅ User '{username}' deleted successfully!")
        except Exception as e:
            print(f"\n❌ Error deleting user: {e}")
            conn.rollback()
    else:
        print("❌ Deletion cancelled")
    
    conn.close()

if __name__ == "__main__":
    delete_user_direct()
