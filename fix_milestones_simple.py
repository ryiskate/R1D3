"""
Simple script to fix the strategy milestones issue.
This script will:
1. Create necessary strategy tables if they don't exist
2. Load milestone data from the fixture file
3. Sync milestone statuses between game and strategy models
"""
import os
import django
import json
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import Django models
from django.db import connection
from django.utils import timezone

def execute_sql(sql, params=None):
    """Execute SQL safely with proper error handling."""
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"SQL Error: {e}")
        print(f"Query: {sql}")
        if params:
            print(f"Params: {params}")
        return None

def create_tables():
    """Create necessary tables for strategy app."""
    print("\n=== CREATING TABLES ===")
    
    # Create StrategyPhase table
    execute_sql("""
    CREATE TABLE IF NOT EXISTS strategy_strategyphase (
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
    
    # Create StrategyMilestone table
    execute_sql("""
    CREATE TABLE IF NOT EXISTS strategy_strategymilestone (
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
    
    # Update migrations table
    execute_sql("""
    INSERT OR IGNORE INTO django_migrations (app, name, applied)
    VALUES ('strategy', '0001_initial', ?)
    """, (timezone.now(),))
    
    execute_sql("""
    INSERT OR IGNORE INTO django_migrations (app, name, applied)
    VALUES ('strategy', '0002_remove_is_completed_add_status', ?)
    """, (timezone.now(),))
    
    print("Tables created successfully.")

def load_phases():
    """Load strategy phases into the database."""
    print("\n=== LOADING PHASES ===")
    
    # Clear existing phases
    execute_sql("DELETE FROM strategy_strategyphase")
    
    # Define phases
    phases = [
        {
            'name': 'Indie Game Development',
            'phase_type': 'indie_dev',
            'description': 'Building a foundation in game development through education and indie projects.',
            'order': 1,
            'start_year': 2025,
            'end_year': 2027,
            'is_current': True,
            'status': 'in_progress'
        },
        {
            'name': 'Arcade Machine Development',
            'phase_type': 'arcade',
            'description': 'Expanding into physical gaming experiences through arcade machine development.',
            'order': 2,
            'start_year': 2027,
            'end_year': 2030,
            'is_current': False,
            'status': 'not_started'
        },
        {
            'name': 'Theme Park Attractions',
            'phase_type': 'theme_park',
            'description': 'Creating immersive physical experiences through theme park attractions.',
            'order': 3,
            'start_year': 2030,
            'end_year': 2035,
            'is_current': False,
            'status': 'not_started'
        }
    ]
    
    # Insert phases
    for phase in phases:
        execute_sql("""
        INSERT INTO strategy_strategyphase 
        (created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timezone.now(),
            timezone.now(),
            phase['name'],
            phase['phase_type'],
            phase['description'],
            phase['order'],
            phase['start_year'],
            phase['end_year'],
            phase['is_current'],
            phase['status']
        ))
    
    print("Phases loaded successfully.")

def load_milestones():
    """Load milestones from fixture file."""
    print("\n=== LOADING MILESTONES ===")
    
    # Clear existing milestones
    execute_sql("DELETE FROM strategy_strategymilestone")
    
    # Load fixture file
    fixture_path = os.path.join('strategy', 'fixtures', 'initial_milestones.json')
    try:
        with open(fixture_path, 'r') as f:
            milestones_data = json.load(f)
        
        # Process each phase's milestones
        for phase_order, milestones in milestones_data.items():
            # Get phase ID
            phase_id_result = execute_sql(
                "SELECT id FROM strategy_strategyphase WHERE \"order\" = ?", 
                (int(phase_order),)
            )
            
            if not phase_id_result:
                print(f"Phase with order {phase_order} not found. Skipping milestones.")
                continue
            
            phase_id = phase_id_result[0][0]
            
            # Insert milestones
            for milestone in milestones:
                execute_sql("""
                INSERT INTO strategy_strategymilestone
                (created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timezone.now(),
                    timezone.now(),
                    milestone['title'],
                    milestone['description'],
                    None,  # target_date
                    milestone['status'],
                    timezone.now() if milestone['status'] == 'completed' else None,  # completion_date
                    milestone['order'],
                    phase_id
                ))
                print(f"Added milestone: {milestone['title']} (Status: {milestone['status']})")
        
        print("Milestones loaded successfully.")
    except Exception as e:
        print(f"Error loading milestones: {e}")

def sync_milestones():
    """Sync milestone statuses between game and strategy models."""
    print("\n=== SYNCING MILESTONES ===")
    
    # Get all game milestones
    game_milestones = execute_sql("""
    SELECT title, status FROM projects_gamemilestone
    """)
    
    if not game_milestones:
        print("No game milestones found.")
        return
    
    print(f"Found {len(game_milestones)} game milestones.")
    
    # Update strategy milestones with matching titles
    for title, status in game_milestones:
        # Check if strategy milestone exists
        strategy_milestone = execute_sql("""
        SELECT id, status FROM strategy_strategymilestone WHERE title = ?
        """, (title,))
        
        if strategy_milestone:
            strategy_id, strategy_status = strategy_milestone[0]
            
            # Update if status is different
            if strategy_status != status:
                execute_sql("""
                UPDATE strategy_strategymilestone SET status = ? WHERE id = ?
                """, (status, strategy_id))
                print(f"Updated milestone '{title}' status from '{strategy_status}' to '{status}'")
        else:
            print(f"No matching strategy milestone found for '{title}'")
    
    print("Milestone sync completed.")

def check_results():
    """Check the results of the fix."""
    print("\n=== CHECKING RESULTS ===")
    
    # Check strategy phases
    phases = execute_sql("SELECT id, name, status FROM strategy_strategyphase ORDER BY \"order\"")
    print(f"Found {len(phases)} strategy phases:")
    for phase_id, name, status in phases:
        print(f"- {name} (Status: {status})")
        
        # Check milestones for this phase
        milestones = execute_sql("""
        SELECT title, status FROM strategy_strategymilestone 
        WHERE phase_id = ? ORDER BY "order"
        """, (phase_id,))
        
        print(f"  Found {len(milestones)} milestones:")
        for title, status in milestones:
            print(f"  - {title} (Status: {status})")
    
    # Check consistency with game milestones
    game_milestones = execute_sql("SELECT title, status FROM projects_gamemilestone")
    strategy_milestones = execute_sql("SELECT title, status FROM strategy_strategymilestone")
    
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

def main():
    """Main function to run the fix."""
    print("=== FIXING STRATEGY MILESTONES ===")
    
    # Create tables
    create_tables()
    
    # Load phases
    load_phases()
    
    # Load milestones
    load_milestones()
    
    # Sync milestones
    sync_milestones()
    
    # Check results
    check_results()
    
    print("\n=== FIX COMPLETED ===")

if __name__ == "__main__":
    main()
