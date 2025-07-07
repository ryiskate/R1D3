"""
Script to check the strategy milestones in the database vs. what's displayed on the strategy page.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models
from projects.game_models import GameMilestone, GameTask
from django.db import connection

def check_database_tables():
    """Check all tables in the database that might contain milestone information."""
    print("\n=== DATABASE TABLES ===")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in the database:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table[0]}")

def check_strategy_tables():
    """Check tables in the strategy app that might contain milestone information."""
    print("\n=== STRATEGY APP TABLES ===")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'strategy_%';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the strategy app.")
            return
        
        print(f"Found {len(tables)} tables in the strategy app:")
        for i, table in enumerate(tables, 1):
            table_name = table[0]
            print(f"{i}. {table_name}")
            
            # Check the structure of each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"   Columns: {', '.join(col[1] for col in columns)}")
            
            # Check the content of each table
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
            rows = cursor.fetchall()
            print(f"   Found {len(rows)} rows (showing up to 5):")
            for j, row in enumerate(rows, 1):
                print(f"   Row {j}: {row}")

def check_game_milestones():
    """Check the GameMilestone model in the database."""
    print("\n=== GAME MILESTONES ===")
    
    milestones = GameMilestone.objects.all().order_by('game__title', 'title')
    
    if not milestones:
        print("No milestones found in the database!")
        return
    
    print(f"Found {milestones.count()} milestones in total:")
    
    for i, m in enumerate(milestones, 1):
        print(f"{i}. {m.title} (Game: {m.game.title})")
        print(f"   Status: {m.status}")
        print(f"   Due date: {m.due_date}")
        print(f"   Description: {m.description[:50]}..." if m.description and len(m.description) > 50 else f"   Description: {m.description}")
        print()

def check_strategy_phase_milestones():
    """Check if there's a separate model for strategy phase milestones."""
    print("\n=== CHECKING FOR STRATEGY PHASE MILESTONES ===")
    
    # Check if the strategy app has models
    try:
        from strategy.models import CompanyPhase, PhaseMilestone
        
        print("Found CompanyPhase model in strategy app.")
        phases = CompanyPhase.objects.all().order_by('order')
        print(f"Found {phases.count()} company phases:")
        
        for i, phase in enumerate(phases, 1):
            print(f"{i}. {phase.name} (Order: {phase.order})")
            
            # Check milestones for this phase
            milestones = PhaseMilestone.objects.filter(phase=phase).order_by('order')
            print(f"   Found {milestones.count()} milestones for this phase:")
            
            for j, milestone in enumerate(milestones, 1):
                print(f"   {j}. {milestone.title}")
                print(f"      Status: {milestone.status}")
                print(f"      Description: {milestone.description[:50]}..." if milestone.description and len(milestone.description) > 50 else f"      Description: {milestone.description}")
    
    except ImportError:
        print("Could not import CompanyPhase or PhaseMilestone from strategy.models.")
        print("Checking if these models exist in the database...")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%phase%' OR name LIKE '%milestone%');")
            tables = cursor.fetchall()
            
            if not tables:
                print("No tables found related to phases or milestones.")
                return
            
            print(f"Found {len(tables)} tables related to phases or milestones:")
            for i, table in enumerate(tables, 1):
                table_name = table[0]
                print(f"{i}. {table_name}")
                
                # Check the structure of each table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print(f"   Columns: {', '.join(col[1] for col in columns)}")
                
                # Check the content of each table
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                print(f"   Found {len(rows)} rows (showing up to 5):")
                for j, row in enumerate(rows, 1):
                    print(f"   Row {j}: {row}")

if __name__ == "__main__":
    print("=== CHECKING STRATEGY MILESTONES ===")
    check_database_tables()
    check_strategy_tables()
    check_game_milestones()
    check_strategy_phase_milestones()
