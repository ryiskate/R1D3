"""
Script to check if the strategy tables were created successfully.
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def check_tables():
    """Check if the strategy tables exist and their contents."""
    print("\n=== CHECKING STRATEGY TABLES ===")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'strategy_%';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No strategy tables found.")
            return
        
        print(f"Found {len(tables)} strategy tables:")
        for i, table in enumerate(tables, 1):
            table_name = table[0]
            print(f"{i}. {table_name}")
            
            # Check the structure of each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"   Columns: {', '.join(col[1] for col in columns)}")
            
            # Check the content of each table
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            print(f"   Found {len(rows)} rows")
            
            # Show the first few rows
            for j, row in enumerate(rows[:5], 1):
                print(f"   Row {j}: {row}")
            
            print()

def check_strategy_milestones():
    """Check the StrategyMilestone table specifically."""
    print("\n=== CHECKING STRATEGY MILESTONES ===")
    
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_strategymilestone';")
        if not cursor.fetchone():
            print("StrategyMilestone table not found.")
            return
        
        # Get all milestones
        cursor.execute("""
        SELECT sm.id, sm.title, sm.status, sm."order", sp.name as phase_name
        FROM strategy_strategymilestone sm
        JOIN strategy_strategyphase sp ON sm.phase_id = sp.id
        ORDER BY sp."order", sm."order";
        """)
        
        milestones = cursor.fetchall()
        print(f"Found {len(milestones)} strategy milestones:")
        
        current_phase = None
        for i, milestone in enumerate(milestones, 1):
            milestone_id, title, status, order, phase_name = milestone
            
            if phase_name != current_phase:
                current_phase = phase_name
                print(f"\n   Phase: {current_phase}")
            
            print(f"   {i}. {title} (Status: {status}, Order: {order})")

def check_game_milestones():
    """Check the GameMilestone table for comparison."""
    print("\n=== CHECKING GAME MILESTONES ===")
    
    with connection.cursor() as cursor:
        # Get all game milestones
        cursor.execute("""
        SELECT gm.id, gm.title, gm.status, g.title as game_title
        FROM projects_gamemilestone gm
        JOIN projects_gameproject g ON gm.game_id = g.id
        ORDER BY g.title, gm.title;
        """)
        
        milestones = cursor.fetchall()
        print(f"Found {len(milestones)} game milestones:")
        
        current_game = None
        for i, milestone in enumerate(milestones, 1):
            milestone_id, title, status, game_title = milestone
            
            if game_title != current_game:
                current_game = game_title
                print(f"\n   Game: {current_game}")
            
            print(f"   {i}. {title} (Status: {status})")

def check_milestone_consistency():
    """Check if there are any milestones with the same title but different status."""
    print("\n=== CHECKING MILESTONE CONSISTENCY ===")
    
    with connection.cursor() as cursor:
        # Get all milestones with the same title from both tables
        cursor.execute("""
        SELECT 
            gm.title as title,
            gm.status as game_status,
            sm.status as strategy_status
        FROM 
            projects_gamemilestone gm,
            strategy_strategymilestone sm
        WHERE 
            gm.title = sm.title
        ORDER BY 
            gm.title;
        """)
        
        milestones = cursor.fetchall()
        print(f"Found {len(milestones)} milestones with the same title in both tables:")
        
        inconsistencies = 0
        for i, milestone in enumerate(milestones, 1):
            title, game_status, strategy_status = milestone
            
            if game_status != strategy_status:
                inconsistencies += 1
                print(f"   ❌ {title}: Game status: {game_status}, Strategy status: {strategy_status}")
            else:
                print(f"   ✅ {title}: Status: {game_status}")
        
        if inconsistencies == 0:
            print("All milestone statuses are consistent between tables!")
        else:
            print(f"Found {inconsistencies} inconsistencies between game and strategy milestones.")

if __name__ == "__main__":
    check_tables()
    check_strategy_milestones()
    check_game_milestones()
    check_milestone_consistency()
