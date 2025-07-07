"""
Direct database fix script for strategy milestone discrepancy.
This script bypasses Django's ORM and directly modifies the database schema.
"""
import os
import sqlite3
import json
from datetime import datetime

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

def execute_sql(conn, sql, params=None):
    """Execute SQL safely with proper error handling."""
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor
    except Exception as e:
        print(f"SQL Error: {e}")
        print(f"Query: {sql}")
        if params:
            print(f"Params: {params}")
        return None

def check_table_exists(conn, table_name):
    """Check if a table exists in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def check_column_exists(conn, table_name, column_name):
    """Check if a column exists in a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def fix_strategy_phase_table(conn):
    """Fix the strategy_strategyphase table."""
    print_header("FIXING STRATEGY PHASE TABLE")
    
    table_name = "strategy_strategyphase"
    
    # Check if table exists
    if not check_table_exists(conn, table_name):
        print(f"Table {table_name} does not exist. Creating it...")
        execute_sql(conn, """
        CREATE TABLE strategy_strategyphase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            name VARCHAR(100) NOT NULL,
            phase_type VARCHAR(20) NOT NULL,
            description TEXT NOT NULL,
            "order" INTEGER NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            is_current BOOL NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'not_started'
        )
        """)
        print(f"Table {table_name} created successfully.")
        return
    
    # Check if status column exists
    has_status = check_column_exists(conn, table_name, "status")
    has_is_completed = check_column_exists(conn, table_name, "is_completed")
    
    if not has_status:
        print(f"Adding status column to {table_name}...")
        execute_sql(conn, f"ALTER TABLE {table_name} ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'not_started'")
    
    # Copy data from is_completed to status
    if has_is_completed and has_status:
        print(f"Copying data from is_completed to status in {table_name}...")
        execute_sql(conn, f"""
        UPDATE {table_name}
        SET status = CASE WHEN is_completed = 1 THEN 'completed' ELSE 'not_started' END
        """)
    
    # Remove is_completed column (SQLite doesn't support DROP COLUMN directly)
    if has_is_completed:
        print(f"Removing is_completed column from {table_name}...")
        # Create a new table without is_completed
        execute_sql(conn, f"""
        CREATE TABLE {table_name}_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            name VARCHAR(100) NOT NULL,
            phase_type VARCHAR(20) NOT NULL,
            description TEXT NOT NULL,
            "order" INTEGER NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            is_current BOOL NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'not_started'
        )
        """)
        
        # Copy data from old table to new table
        execute_sql(conn, f"""
        INSERT INTO {table_name}_new (id, created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status)
        SELECT id, created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status
        FROM {table_name}
        """)
        
        # Drop old table
        execute_sql(conn, f"DROP TABLE {table_name}")
        
        # Rename new table to old table name
        execute_sql(conn, f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
    
    print(f"Table {table_name} fixed successfully.")

def fix_strategy_milestone_table(conn):
    """Fix the strategy_strategymilestone table."""
    print_header("FIXING STRATEGY MILESTONE TABLE")
    
    table_name = "strategy_strategymilestone"
    
    # Check if table exists
    if not check_table_exists(conn, table_name):
        print(f"Table {table_name} does not exist. Creating it...")
        execute_sql(conn, """
        CREATE TABLE strategy_strategymilestone (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            target_date DATE NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'not_started',
            completion_date DATE NULL,
            "order" INTEGER NOT NULL DEFAULT 0,
            phase_id INTEGER NOT NULL REFERENCES strategy_strategyphase(id)
        )
        """)
        print(f"Table {table_name} created successfully.")
        return
    
    # Check if status column exists
    has_status = check_column_exists(conn, table_name, "status")
    has_is_completed = check_column_exists(conn, table_name, "is_completed")
    
    if not has_status:
        print(f"Adding status column to {table_name}...")
        execute_sql(conn, f"ALTER TABLE {table_name} ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'not_started'")
    
    # Copy data from is_completed to status
    if has_is_completed and has_status:
        print(f"Copying data from is_completed to status in {table_name}...")
        execute_sql(conn, f"""
        UPDATE {table_name}
        SET status = CASE WHEN is_completed = 1 THEN 'completed' ELSE 'not_started' END
        """)
    
    # Remove is_completed column (SQLite doesn't support DROP COLUMN directly)
    if has_is_completed:
        print(f"Removing is_completed column from {table_name}...")
        # Create a new table without is_completed
        execute_sql(conn, f"""
        CREATE TABLE {table_name}_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            target_date DATE NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'not_started',
            completion_date DATE NULL,
            "order" INTEGER NOT NULL DEFAULT 0,
            phase_id INTEGER NOT NULL REFERENCES strategy_strategyphase(id)
        )
        """)
        
        # Copy data from old table to new table
        execute_sql(conn, f"""
        INSERT INTO {table_name}_new (id, created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id)
        SELECT id, created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id
        FROM {table_name}
        """)
        
        # Drop old table
        execute_sql(conn, f"DROP TABLE {table_name}")
        
        # Rename new table to old table name
        execute_sql(conn, f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
    
    print(f"Table {table_name} fixed successfully.")

def update_migrations(conn):
    """Update the django_migrations table to mark our migrations as applied."""
    print_header("UPDATING MIGRATIONS")
    
    # Check if migrations exist
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id FROM django_migrations
    WHERE app = 'strategy' AND name = '0001_initial'
    """)
    
    if not cursor.fetchone():
        print("Adding initial migration record...")
        execute_sql(conn, """
        INSERT INTO django_migrations (app, name, applied)
        VALUES ('strategy', '0001_initial', datetime('now'))
        """)
    
    cursor.execute("""
    SELECT id FROM django_migrations
    WHERE app = 'strategy' AND name = '0002_remove_is_completed_add_status'
    """)
    
    if not cursor.fetchone():
        print("Adding status migration record...")
        execute_sql(conn, """
        INSERT INTO django_migrations (app, name, applied)
        VALUES ('strategy', '0002_remove_is_completed_add_status', datetime('now'))
        """)
    
    print("Migrations updated successfully.")

def load_initial_data(conn):
    """Load initial data into the strategy tables."""
    print_header("LOADING INITIAL DATA")
    
    # Check if we already have phases
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM strategy_strategyphase")
    phase_count = cursor.fetchone()[0]
    
    if phase_count == 0:
        print("Loading phases...")
        phases = [
            ('Indie Game Development', 'indie_dev', 'Building a foundation in game development through education and indie projects.', 1, 2025, 2027, 1, 'in_progress'),
            ('Arcade Machine Development', 'arcade', 'Expanding into physical gaming experiences through arcade machine development.', 2, 2027, 2030, 0, 'not_started'),
            ('Theme Park Attractions', 'theme_park', 'Creating immersive physical experiences through theme park attractions.', 3, 2030, 2035, 0, 'not_started')
        ]
        
        for phase in phases:
            execute_sql(conn, """
            INSERT INTO strategy_strategyphase (created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status)
            VALUES (datetime('now'), datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)
            """, phase)
    
    # Load milestones from fixture file
    fixture_path = os.path.join('strategy', 'fixtures', 'initial_milestones.json')
    
    try:
        with open(fixture_path, 'r') as f:
            milestones_data = json.load(f)
        
        # Process each phase's milestones
        for phase_order, milestones in milestones_data.items():
            # Get phase ID
            cursor.execute("SELECT id FROM strategy_strategyphase WHERE \"order\" = ?", (int(phase_order),))
            result = cursor.fetchone()
            
            if not result:
                print(f"Phase with order {phase_order} not found. Skipping milestones.")
                continue
            
            phase_id = result[0]
            
            # Insert milestones
            for milestone in milestones:
                # Check if milestone already exists
                cursor.execute("SELECT id FROM strategy_strategymilestone WHERE title = ?", (milestone['title'],))
                if cursor.fetchone():
                    print(f"Milestone '{milestone['title']}' already exists. Skipping.")
                    continue
                
                completion_date = "datetime('now')" if milestone['status'] == 'completed' else "NULL"
                
                execute_sql(conn, f"""
                INSERT INTO strategy_strategymilestone
                (created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id)
                VALUES (datetime('now'), datetime('now'), ?, ?, NULL, ?, {completion_date}, ?, ?)
                """, (
                    milestone['title'],
                    milestone['description'],
                    milestone['status'],
                    milestone['order'],
                    phase_id
                ))
                print(f"Added milestone: {milestone['title']} (Status: {milestone['status']})")
        
        print("Initial data loaded successfully.")
    except Exception as e:
        print(f"Error loading initial data: {e}")
        import traceback
        traceback.print_exc()

def sync_with_game_milestones(conn):
    """Sync milestone statuses between game and strategy models."""
    print_header("SYNCING WITH GAME MILESTONES")
    
    # Get all game milestones
    cursor = conn.cursor()
    cursor.execute("SELECT title, status FROM projects_gamemilestone")
    game_milestones = cursor.fetchall()
    
    if not game_milestones:
        print("No game milestones found.")
        return
    
    print(f"Found {len(game_milestones)} game milestones.")
    
    # Update strategy milestones with matching titles
    for title, status in game_milestones:
        # Check if strategy milestone exists
        cursor.execute("SELECT id, status FROM strategy_strategymilestone WHERE title = ?", (title,))
        result = cursor.fetchone()
        
        if result:
            strategy_id, strategy_status = result
            
            # Update if status is different
            if strategy_status != status:
                completion_date = "datetime('now')" if status == 'completed' else "NULL"
                execute_sql(conn, f"""
                UPDATE strategy_strategymilestone 
                SET status = ?, completion_date = {completion_date}
                WHERE id = ?
                """, (status, strategy_id))
                print(f"Updated milestone '{title}' status from '{strategy_status}' to '{status}'")
        else:
            print(f"No matching strategy milestone found for '{title}'")
    
    print("Milestone sync completed.")

def check_results(conn):
    """Check the results of the fix."""
    print_header("CHECKING RESULTS")
    
    # Check strategy phases
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status FROM strategy_strategyphase ORDER BY \"order\"")
    phases = cursor.fetchall()
    
    print(f"Found {len(phases)} strategy phases:")
    for phase_id, name, status in phases:
        print(f"- {name} (Status: {status})")
        
        # Check milestones for this phase
        cursor.execute("""
        SELECT title, status FROM strategy_strategymilestone 
        WHERE phase_id = ? ORDER BY "order"
        """, (phase_id,))
        
        milestones = cursor.fetchall()
        print(f"  Found {len(milestones)} milestones:")
        for title, status in milestones:
            print(f"  - {title} (Status: {status})")
    
    # Check consistency with game milestones
    cursor.execute("SELECT title, status FROM projects_gamemilestone")
    game_milestones = cursor.fetchall()
    
    cursor.execute("SELECT title, status FROM strategy_strategymilestone")
    strategy_milestones = cursor.fetchall()
    
    # Convert to dictionaries for easy comparison
    game_dict = {title: status for title, status in game_milestones}
    strategy_dict = {title: status for title, status in strategy_milestones}
    
    # Find inconsistencies
    inconsistencies = 0
    for title, game_status in game_dict.items():
        if title in strategy_dict:
            strategy_status = strategy_dict[title]
            if game_status != strategy_status:
                inconsistencies += 1
                print(f"❌ Inconsistency: '{title}' - Game: {game_status}, Strategy: {strategy_status}")
    
    if inconsistencies == 0:
        print("✅ All milestone statuses are consistent between game and strategy models!")
    else:
        print(f"Found {inconsistencies} inconsistencies between game and strategy milestones.")

def fix_model_code():
    """Check and fix model code to ensure it doesn't reference is_completed."""
    print_header("CHECKING MODEL CODE")
    
    # Check if the model code has been updated
    model_path = os.path.join('strategy', 'models.py')
    
    try:
        with open(model_path, 'r') as f:
            model_code = f.read()
        
        if 'is_completed' in model_code:
            print("❌ Model code still references 'is_completed'. Please update the model code.")
        else:
            print("✅ Model code does not reference 'is_completed'.")
    except Exception as e:
        print(f"Error checking model code: {e}")

def main():
    """Main function to run the fix."""
    print_header("FIXING DATABASE SCHEMA")
    print(f"Database path: {db_path}")
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        
        # Fix model code
        fix_model_code()
        
        # Fix strategy phase table
        fix_strategy_phase_table(conn)
        
        # Fix strategy milestone table
        fix_strategy_milestone_table(conn)
        
        # Update migrations
        update_migrations(conn)
        
        # Load initial data
        load_initial_data(conn)
        
        # Sync with game milestones
        sync_with_game_milestones(conn)
        
        # Check results
        check_results(conn)
        
        # Close connection
        conn.close()
        
        print_header("FIX COMPLETED")
        print("The strategy milestone discrepancy has been resolved.")
        print("You can now run the development server and check the strategy dashboard.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
