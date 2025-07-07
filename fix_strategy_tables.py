"""
Script to fix the strategy tables using raw SQL.
This will create the necessary tables and update the database directly,
bypassing Django's migration system.
"""
import os
import django
import json
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def check_tables():
    """Check if the strategy tables exist."""
    print("\n=== CHECKING TABLES ===")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'strategy_%';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No strategy tables found.")
            return False
        
        print(f"Found {len(tables)} strategy tables:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table[0]}")
        
        # Check specifically for StrategyMilestone table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
        if not cursor.fetchone():
            print("StrategyMilestone table not found.")
            return False
        
        return True

def create_strategy_tables():
    """Create the strategy tables using raw SQL."""
    print("\n=== CREATING STRATEGY TABLES ===")
    
    with connection.cursor() as cursor:
        # Create StrategyPhase table if it doesn't exist
        cursor.execute("""
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
        );
        """)
        
        # Create StrategyMilestone table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_strategymilestone (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            target_date DATE,
            status VARCHAR(20) NOT NULL DEFAULT 'not_started',
            completion_date DATE,
            "order" INTEGER NOT NULL DEFAULT 0,
            phase_id INTEGER NOT NULL REFERENCES strategy_strategyphase(id)
        );
        """)
        
        # Update django_migrations to mark these migrations as applied
        cursor.execute("""
        INSERT OR IGNORE INTO django_migrations (app, name, applied)
        VALUES ('strategy', '0001_initial', datetime('now'));
        """)
        
        cursor.execute("""
        INSERT OR IGNORE INTO django_migrations (app, name, applied)
        VALUES ('strategy', '0002_remove_is_completed_add_status', datetime('now'));
        """)
        
        print("Strategy tables created successfully.")

def load_initial_data():
    """Load initial data into the strategy tables."""
    print("\n=== LOADING INITIAL DATA ===")
    
    # Define the phases
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
    
    # Load phases into the database
    with connection.cursor() as cursor:
        # Clear existing data
        cursor.execute("DELETE FROM strategy_strategymilestone;")
        cursor.execute("DELETE FROM strategy_strategyphase;")
        
        # Insert phases
        for phase in phases:
            cursor.execute("""
            INSERT INTO strategy_strategyphase 
            (created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status)
            VALUES (datetime('now'), datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                phase['name'], 
                phase['phase_type'], 
                phase['description'], 
                phase['order'], 
                phase['start_year'], 
                phase['end_year'], 
                phase['is_current'], 
                phase['status']
            ))
    
    # Load milestones from fixture file
    fixture_path = os.path.join('strategy', 'fixtures', 'initial_milestones.json')
    
    try:
        # Load the fixture file
        with open(fixture_path, 'r') as f:
            milestones_data = json.load(f)
        
        with connection.cursor() as cursor:
            # For each phase, insert its milestones
            for phase_id, milestones in milestones_data.items():
                # Get the actual phase ID from the database
                cursor.execute(f"SELECT id FROM strategy_strategyphase WHERE \"order\" = ?;", (int(phase_id),))
                db_phase_id = cursor.fetchone()[0]
                
                for milestone in milestones:
                    cursor.execute("""
                    INSERT INTO strategy_strategymilestone
                    (created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id)
                    VALUES (datetime('now'), datetime('now'), ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        milestone['title'],
                        milestone['description'],
                        None,  # target_date
                        milestone['status'],
                        None if milestone['status'] != 'completed' else 'now',  # completion_date
                        milestone['order'],
                        db_phase_id
                    ))
        
        print("Initial data loaded successfully.")
    except Exception as e:
        print(f"Error loading initial data: {e}")

def sync_with_game_milestones():
    """Sync strategy milestones with game milestones."""
    print("\n=== SYNCING WITH GAME MILESTONES ===")
    
    try:
        # Import models after Django setup
        from projects.game_models import GameMilestone
        
        # Get all game milestones
        game_milestones = GameMilestone.objects.all()
        print(f"Found {game_milestones.count()} game milestones.")
        
        # For each game milestone, update the corresponding strategy milestone
        with connection.cursor() as cursor:
            for game_milestone in game_milestones:
                # Check if a strategy milestone with the same title exists
                cursor.execute("""
                SELECT id, status FROM strategy_strategymilestone WHERE title = ?;
                """, (game_milestone.title,))
                
                result = cursor.fetchone()
                if result:
                    strategy_milestone_id, strategy_status = result
                    
                    # Update the strategy milestone status if different
                    if strategy_status != game_milestone.status:
                        print(f"Updating {game_milestone.title} status from {strategy_status} to {game_milestone.status}")
                        cursor.execute("""
                        UPDATE strategy_strategymilestone SET status = ? WHERE id = ?;
                        """, (game_milestone.status, strategy_milestone_id))
                else:
                    print(f"No matching strategy milestone found for {game_milestone.title}")
        
        print("Sync completed successfully.")
    except Exception as e:
        print(f"Error syncing with game milestones: {e}")

def main():
    """Main function to run all the fixes."""
    print("=== FIXING STRATEGY TABLES ===")
    
    # Check if tables exist
    tables_exist = check_tables()
    
    # Create tables if they don't exist
    if not tables_exist:
        create_strategy_tables()
        load_initial_data()
    
    # Sync with game milestones
    sync_with_game_milestones()
    
    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
