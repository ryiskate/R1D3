"""
Comprehensive script to fix the strategy milestone discrepancy.
This script will:
1. Check migration status
2. Apply migrations if needed
3. Verify database schema
4. Load initial data
5. Sync with game milestones
"""
import os
import sys
import django
import sqlite3
import json
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import Django models
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.core.management import call_command
from strategy.models import StrategyPhase, StrategyMilestone
from projects.models import GameMilestone

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

def check_migration_status():
    """Check the status of migrations."""
    print_header("CHECKING MIGRATION STATUS")
    
    # Get applied migrations
    recorder = MigrationRecorder(connection)
    applied_migrations = recorder.applied_migrations()
    
    # Check strategy migrations
    strategy_migrations = [m for m in applied_migrations if m[0] == 'strategy']
    print(f"Applied strategy migrations: {len(strategy_migrations)}")
    for app, name in strategy_migrations:
        print(f"- {name}")
    
    # Check if our migration is applied
    status_migration = ('strategy', '0002_remove_is_completed_add_status')
    if status_migration in applied_migrations:
        print("✅ Status migration is applied.")
        return True
    else:
        print("❌ Status migration is not applied.")
        return False

def apply_migrations():
    """Apply migrations."""
    print_header("APPLYING MIGRATIONS")
    
    try:
        # Try applying migrations normally
        print("Attempting to apply migrations...")
        call_command('migrate', 'strategy')
        print("✅ Migrations applied successfully.")
        return True
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        
        # Try fake-applying the initial migration
        try:
            print("Attempting to fake-apply initial migration...")
            call_command('migrate', 'strategy', '0001_initial', fake=True)
            print("✅ Initial migration fake-applied successfully.")
            
            # Now try to apply the status migration
            print("Attempting to apply status migration...")
            call_command('migrate', 'strategy')
            print("✅ Status migration applied successfully.")
            return True
        except Exception as e2:
            print(f"❌ Error fake-applying migrations: {e2}")
            return False

def verify_database_schema():
    """Verify the database schema."""
    print_header("VERIFYING DATABASE SCHEMA")
    
    # Connect to the database
    db_path = connection.settings_dict['NAME']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    tables = ['strategy_strategyphase', 'strategy_strategymilestone']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            print(f"✅ Table '{table}' exists.")
        else:
            print(f"❌ Table '{table}' does not exist.")
            return False
    
    # Check columns in strategy_strategyphase
    cursor.execute("PRAGMA table_info(strategy_strategyphase)")
    columns = {col[1] for col in cursor.fetchall()}
    
    required_columns = {'id', 'created_at', 'updated_at', 'name', 'phase_type', 
                       'description', 'order', 'start_year', 'end_year', 
                       'is_current', 'status'}
    
    missing_columns = required_columns - columns
    if missing_columns:
        print(f"❌ Missing columns in strategy_strategyphase: {missing_columns}")
        return False
    
    if 'is_completed' in columns:
        print("❌ Deprecated column 'is_completed' still exists in strategy_strategyphase.")
        return False
    
    print("✅ strategy_strategyphase schema is correct.")
    
    # Check columns in strategy_strategymilestone
    cursor.execute("PRAGMA table_info(strategy_strategymilestone)")
    columns = {col[1] for col in cursor.fetchall()}
    
    required_columns = {'id', 'created_at', 'updated_at', 'title', 'description', 
                       'target_date', 'status', 'completion_date', 'order', 'phase_id'}
    
    missing_columns = required_columns - columns
    if missing_columns:
        print(f"❌ Missing columns in strategy_strategymilestone: {missing_columns}")
        return False
    
    if 'is_completed' in columns:
        print("❌ Deprecated column 'is_completed' still exists in strategy_strategymilestone.")
        return False
    
    print("✅ strategy_strategymilestone schema is correct.")
    
    # Close connection
    conn.close()
    
    return True

def fix_database_schema():
    """Fix the database schema if needed."""
    print_header("FIXING DATABASE SCHEMA")
    
    # Connect to the database
    db_path = connection.settings_dict['NAME']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    tables = ['strategy_strategyphase', 'strategy_strategymilestone']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"Creating table '{table}'...")
            
            if table == 'strategy_strategyphase':
                cursor.execute("""
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
                print(f"✅ Table '{table}' created.")
            
            elif table == 'strategy_strategymilestone':
                cursor.execute("""
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
                print(f"✅ Table '{table}' created.")
    
    # Check if status column exists in strategy_strategyphase
    cursor.execute("PRAGMA table_info(strategy_strategyphase)")
    columns = {col[1] for col in cursor.fetchall()}
    
    if 'status' not in columns:
        print("Adding 'status' column to strategy_strategyphase...")
        cursor.execute("ALTER TABLE strategy_strategyphase ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'not_started'")
        print("✅ Column 'status' added to strategy_strategyphase.")
    
    # Check if is_completed column exists in strategy_strategyphase
    if 'is_completed' in columns:
        print("Removing 'is_completed' column from strategy_strategyphase...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to create a new table
        cursor.execute("""
        CREATE TABLE strategy_strategyphase_new (
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
        cursor.execute("""
        INSERT INTO strategy_strategyphase_new 
        (id, created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status)
        SELECT id, created_at, updated_at, name, phase_type, description, "order", start_year, end_year, is_current, status
        FROM strategy_strategyphase
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE strategy_strategyphase")
        
        # Rename new table to old table name
        cursor.execute("ALTER TABLE strategy_strategyphase_new RENAME TO strategy_strategyphase")
        
        print("✅ Column 'is_completed' removed from strategy_strategyphase.")
    
    # Check if status column exists in strategy_strategymilestone
    cursor.execute("PRAGMA table_info(strategy_strategymilestone)")
    columns = {col[1] for col in cursor.fetchall()}
    
    if 'status' not in columns:
        print("Adding 'status' column to strategy_strategymilestone...")
        cursor.execute("ALTER TABLE strategy_strategymilestone ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'not_started'")
        print("✅ Column 'status' added to strategy_strategymilestone.")
    
    # Check if is_completed column exists in strategy_strategymilestone
    if 'is_completed' in columns:
        print("Removing 'is_completed' column from strategy_strategymilestone...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to create a new table
        cursor.execute("""
        CREATE TABLE strategy_strategymilestone_new (
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
        cursor.execute("""
        INSERT INTO strategy_strategymilestone_new 
        (id, created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id)
        SELECT id, created_at, updated_at, title, description, target_date, status, completion_date, "order", phase_id
        FROM strategy_strategymilestone
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE strategy_strategymilestone")
        
        # Rename new table to old table name
        cursor.execute("ALTER TABLE strategy_strategymilestone_new RENAME TO strategy_strategymilestone")
        
        print("✅ Column 'is_completed' removed from strategy_strategymilestone.")
    
    # Update migration record
    cursor.execute("""
    SELECT id FROM django_migrations
    WHERE app = 'strategy' AND name = '0001_initial'
    """)
    
    if not cursor.fetchone():
        print("Adding initial migration record...")
        cursor.execute("""
        INSERT INTO django_migrations (app, name, applied)
        VALUES ('strategy', '0001_initial', ?)
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),))
    
    cursor.execute("""
    SELECT id FROM django_migrations
    WHERE app = 'strategy' AND name = '0002_remove_is_completed_add_status'
    """)
    
    if not cursor.fetchone():
        print("Adding status migration record...")
        cursor.execute("""
        INSERT INTO django_migrations (app, name, applied)
        VALUES ('strategy', '0002_remove_is_completed_add_status', ?)
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),))
    
    # Commit changes
    conn.commit()
    
    # Close connection
    conn.close()
    
    print("✅ Database schema fixed.")

def load_initial_data():
    """Load initial data into the strategy tables."""
    print_header("LOADING INITIAL DATA")
    
    # Check if we already have phases
    phase_count = StrategyPhase.objects.count()
    print(f"Found {phase_count} existing phases.")
    
    if phase_count == 0:
        print("Creating default phases...")
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
        
        for phase_data in phases:
            phase = StrategyPhase.objects.create(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                **phase_data
            )
            print(f"Created phase: {phase.name}")
    
    # Load milestones from fixture file
    fixture_path = os.path.join('strategy', 'fixtures', 'initial_milestones.json')
    
    try:
        with open(fixture_path, 'r') as f:
            milestones_data = json.load(f)
        
        # Process each phase's milestones
        for phase_order, milestones in milestones_data.items():
            # Get phase
            try:
                phase = StrategyPhase.objects.get(order=int(phase_order))
            except StrategyPhase.DoesNotExist:
                print(f"Phase with order {phase_order} not found. Skipping milestones.")
                continue
            
            # Insert milestones
            for milestone in milestones:
                # Check if milestone already exists
                existing = StrategyMilestone.objects.filter(title=milestone['title'], phase=phase).first()
                
                if existing:
                    print(f"Milestone '{milestone['title']}' already exists. Updating...")
                    existing.description = milestone['description']
                    existing.order = milestone['order']
                    existing.status = milestone['status']
                    existing.save()
                else:
                    # Create new milestone
                    new_milestone = StrategyMilestone.objects.create(
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        title=milestone['title'],
                        description=milestone['description'],
                        order=milestone['order'],
                        status=milestone['status'],
                        phase=phase
                    )
                    print(f"Created milestone: {new_milestone.title} (Status: {new_milestone.status})")
        
        print("✅ Initial data loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading initial data: {e}")
        import traceback
        traceback.print_exc()

def sync_with_game_milestones():
    """Sync milestone statuses between game and strategy models."""
    print_header("SYNCING WITH GAME MILESTONES")
    
    # Get all game milestones
    game_milestones = GameMilestone.objects.all()
    
    if not game_milestones:
        print("No game milestones found.")
        return
    
    print(f"Found {game_milestones.count()} game milestones.")
    
    # Update strategy milestones with matching titles
    for game_milestone in game_milestones:
        # Check if strategy milestone exists
        strategy_milestones = StrategyMilestone.objects.filter(title=game_milestone.title)
        
        if strategy_milestones.exists():
            strategy_milestone = strategy_milestones.first()
            
            # Update if status is different
            if strategy_milestone.status != game_milestone.status:
                old_status = strategy_milestone.status
                strategy_milestone.status = game_milestone.status
                
                # Update completion date if completed
                if game_milestone.status == 'completed':
                    strategy_milestone.completion_date = datetime.now().date()
                
                strategy_milestone.save()
                print(f"Updated milestone '{strategy_milestone.title}' status from '{old_status}' to '{strategy_milestone.status}'")
        else:
            print(f"No matching strategy milestone found for '{game_milestone.title}'")
    
    # Check for strategy milestones not in game milestones
    strategy_milestones = StrategyMilestone.objects.all()
    game_milestone_titles = {m.title for m in game_milestones}
    
    for strategy_milestone in strategy_milestones:
        if strategy_milestone.title not in game_milestone_titles:
            print(f"Strategy milestone '{strategy_milestone.title}' has no matching game milestone.")
    
    print("✅ Milestone sync completed.")

def check_results():
    """Check the results of the fix."""
    print_header("CHECKING RESULTS")
    
    # Check strategy phases
    phases = StrategyPhase.objects.all().order_by('order')
    
    print(f"Found {phases.count()} strategy phases:")
    for phase in phases:
        print(f"- {phase.name} (Status: {phase.status})")
        
        # Check milestones for this phase
        milestones = StrategyMilestone.objects.filter(phase=phase).order_by('order')
        
        print(f"  Found {milestones.count()} milestones:")
        for milestone in milestones:
            print(f"  - {milestone.title} (Status: {milestone.status})")
    
    # Check consistency with game milestones
    game_milestones = GameMilestone.objects.all()
    strategy_milestones = StrategyMilestone.objects.all()
    
    # Convert to dictionaries for easy comparison
    game_dict = {m.title: m.status for m in game_milestones}
    strategy_dict = {m.title: m.status for m in strategy_milestones}
    
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
    print_header("FIXING STRATEGY MILESTONE DISCREPANCY")
    
    # Step 1: Check migration status
    migration_applied = check_migration_status()
    
    # Step 2: Apply migrations if needed
    if not migration_applied:
        migration_success = apply_migrations()
        if not migration_success:
            print("❌ Failed to apply migrations. Trying manual schema fix...")
            fix_database_schema()
    
    # Step 3: Verify database schema
    schema_correct = verify_database_schema()
    
    if not schema_correct:
        print("❌ Database schema is incorrect. Fixing...")
        fix_database_schema()
        
        # Verify again after fixing
        schema_correct = verify_database_schema()
        if not schema_correct:
            print("❌ Failed to fix database schema. Exiting.")
            return
    
    # Step 4: Load initial data
    load_initial_data()
    
    # Step 5: Sync with game milestones
    sync_with_game_milestones()
    
    # Step 6: Check results
    check_results()
    
    print_header("FIX COMPLETED SUCCESSFULLY")
    print("The strategy milestone discrepancy has been resolved.")
    print("You can now run the development server and check the strategy dashboard.")

if __name__ == "__main__":
    main()
