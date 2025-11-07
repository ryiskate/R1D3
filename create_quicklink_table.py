#!/usr/bin/env python3
"""
Create the core_quicklink table if it doesn't exist
"""
import sqlite3
from pathlib import Path

def create_quicklink_table():
    """Create the quick link table"""
    db_path = Path(__file__).parent / 'db.sqlite3'
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creating core_quicklink table...")
    
    try:
        # Drop the table if it exists (to recreate with correct schema)
        cursor.execute("DROP TABLE IF EXISTS core_quicklink")
        
        # Create the table with correct schema
        cursor.execute("""
            CREATE TABLE core_quicklink (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                user_id INTEGER NOT NULL,
                name VARCHAR(200) NOT NULL,
                url VARCHAR(500) NOT NULL,
                icon VARCHAR(50) NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES auth_user(id)
            )
        """)
        
        conn.commit()
        print("✅ Table created successfully!")
        
        # Check if any quick links exist
        cursor.execute("SELECT COUNT(*) FROM core_quicklink")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\n📝 Adding default quick links...")
            from datetime import datetime
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get the first user ID
            cursor.execute("SELECT id FROM auth_user LIMIT 1")
            user_result = cursor.fetchone()
            if user_result:
                user_id = user_result[0]
                
                default_links = [
                    ('Dashboard', '/', 'fas fa-home', 1),
                    ('Tasks', '/R1D3-tasks/', 'fas fa-tasks', 2),
                    ('Games', '/games/', 'fas fa-gamepad', 3),
                ]
                
                for name, url, icon, position in default_links:
                    cursor.execute("""
                        INSERT INTO core_quicklink 
                        (created_at, updated_at, user_id, name, url, icon, position)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (now, now, user_id, name, url, icon, position))
                
                conn.commit()
                print(f"✅ Added {len(default_links)} default quick links for user ID {user_id}!")
            else:
                print("⚠️  No users found - skipping default quick links")
        else:
            print(f"ℹ️  Table already has {count} quick link(s)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_quicklink_table()
