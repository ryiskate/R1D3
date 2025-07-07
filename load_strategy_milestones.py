"""
Script to load strategy milestones from the fixture file into the database.
"""
import os
import django
import json
from django.db import connection
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def load_milestones():
    """Load milestones from fixture file into the database."""
    print("\n=== LOADING STRATEGY MILESTONES ===")
    
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
                cursor.execute("SELECT id FROM strategy_strategyphase WHERE \"order\" = ?", (int(phase_id),))
                result = cursor.fetchone()
                
                if not result:
                    print(f"No phase found with order {phase_id}. Creating phase...")
                    # Create the phase if it doesn't exist
                    if phase_id == "1":
                        name = "Indie Game Development"
                        phase_type = "indie_dev"
                        description = "Building a foundation in game development through education and indie projects."
                        start_year = 2025
                        end_year = 2027
                        is_current = True
                        status = "in_progress"
                    elif phase_id == "2":
                        name = "Arcade Machine Development"
                        phase_type = "arcade"
                        description = "Expanding into physical gaming experiences through arcade machine development."
                        start_year = 2027
                        end_year = 2030
                        is_current = False
                        status = "not_started"
                    elif phase_id == "3":
                        name = "Theme Park Attractions"
                        phase_type = "theme_park"
                        description = "Creating immersive physical experiences through theme park attractions."
                        start_year = 2030
                        end_year = 2035
                        is_current = False
                        status = "not_started"
                    
                    cursor.execute("""
                    INSERT INTO strategy_strategyphase 
                    (created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        timezone.now(),
                        timezone.now(),
                        name,
                        phase_type,
                        description,
                        int(phase_id),
                        start_year,
                        end_year,
                        is_current,
                        status
                    ))
                    
                    # Get the new phase ID
                    cursor.execute("SELECT id FROM strategy_strategyphase WHERE \"order\" = ?", (int(phase_id),))
                    result = cursor.fetchone()
                
                db_phase_id = result[0]
                
                for milestone in milestones:
                    # Check if milestone already exists
                    cursor.execute("SELECT id FROM strategy_strategymilestone WHERE title = ?;", (milestone['title'],))
                    existing_milestone = cursor.fetchone()
                    
                    if existing_milestone:
                        print(f"Milestone '{milestone['title']}' already exists. Updating...")
                        cursor.execute("""
                        UPDATE strategy_strategymilestone
                        SET status = ?, "order" = ?
                        WHERE id = ?;
                        """, (
                            milestone['status'],
                            milestone['order'],
                            existing_milestone[0]
                        ))
                    else:
                        print(f"Creating milestone '{milestone['title']}'...")
                        cursor.execute("""
                        INSERT INTO strategy_strategymilestone
                        (created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            timezone.now(),
                            timezone.now(),
                            milestone['title'],
                            milestone['description'],
                            None,  # target_date
                            milestone['status'],
                            timezone.now() if milestone['status'] == 'completed' else None,  # completion_date
                            milestone['order'],
                            db_phase_id
                        ))
        
        print("Milestones loaded successfully.")
    except Exception as e:
        print(f"Error loading milestones: {e}")

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

if __name__ == "__main__":
    load_milestones()
    sync_with_game_milestones()
