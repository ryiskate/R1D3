"""
Script to fix the strategy milestones and ensure consistency between the database and web interface.
This script will:
1. Update the StrategyMilestone model to use status instead of is_completed
2. Create a migration for the StrategyMilestone model
3. Apply the migration
4. Update the session-based milestones to match the database
"""
import os
import sys
import django
import json
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from strategy.models import StrategyMilestone, StrategyPhase
from projects.game_models import GameMilestone

def check_strategy_model():
    """Check if the StrategyMilestone model has been updated to use status field."""
    print("\n=== CHECKING STRATEGY MODEL ===")
    
    try:
        # Check if the model has a status field
        milestone = StrategyMilestone.objects.first()
        if hasattr(milestone, 'status'):
            print("✅ StrategyMilestone model has status field.")
        else:
            print("❌ StrategyMilestone model does not have status field.")
            
        # Check if the model still has is_completed field
        if hasattr(milestone, 'is_completed'):
            print("❌ StrategyMilestone model still has is_completed field.")
        else:
            print("✅ StrategyMilestone model no longer has is_completed field.")
    except Exception as e:
        print(f"Error checking StrategyMilestone model: {e}")

def create_migration():
    """Create a migration for the StrategyMilestone model."""
    print("\n=== CREATING MIGRATION ===")
    
    try:
        # Check if the migration already exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM django_migrations WHERE app='strategy' AND name LIKE '%remove_is_completed%';")
            existing_migration = cursor.fetchone()
            
            if existing_migration:
                print(f"Migration already exists: {existing_migration[0]}")
                return
        
        # Create a raw SQL migration
        migration_name = 'remove_is_completed_add_status'
        migration_path = os.path.join('strategy', 'migrations', f'0002_{migration_name}.py')
        
        migration_content = """# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategymilestone',
            name='status',
            field=models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started', max_length=20),
        ),
        migrations.RunSQL(
            "UPDATE strategy_strategymilestone SET status = CASE WHEN is_completed THEN 'completed' ELSE 'not_started' END;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(
            model_name='strategymilestone',
            name='is_completed',
        ),
    ]
"""
        
        # Create the migration file
        os.makedirs(os.path.dirname(migration_path), exist_ok=True)
        with open(migration_path, 'w') as f:
            f.write(migration_content)
            
        print(f"Created migration file: {migration_path}")
    except Exception as e:
        print(f"Error creating migration: {e}")

def apply_migration():
    """Apply the migration."""
    print("\n=== APPLYING MIGRATION ===")
    
    try:
        # Apply the migration using Django's management command
        from django.core.management import call_command
        call_command('migrate', 'strategy')
        
        print("Migration applied successfully.")
    except Exception as e:
        print(f"Error applying migration: {e}")

def update_fixture_file():
    """Update the initial_milestones.json fixture file to remove is_completed."""
    print("\n=== UPDATING FIXTURE FILE ===")
    
    fixture_path = os.path.join('strategy', 'fixtures', 'initial_milestones.json')
    
    try:
        # Load the fixture file
        with open(fixture_path, 'r') as f:
            milestones = json.load(f)
        
        # Update each milestone to remove is_completed
        for phase_id, phase_milestones in milestones.items():
            for milestone in phase_milestones:
                if 'is_completed' in milestone:
                    del milestone['is_completed']
        
        # Save the updated fixture file
        with open(fixture_path, 'w') as f:
            json.dump(milestones, f, indent=4)
            
        print(f"Updated fixture file: {fixture_path}")
    except Exception as e:
        print(f"Error updating fixture file: {e}")

def sync_game_milestones_with_strategy():
    """Sync GameMilestone status with StrategyMilestone status."""
    print("\n=== SYNCING GAME MILESTONES WITH STRATEGY MILESTONES ===")
    
    try:
        # Get all game milestones
        game_milestones = GameMilestone.objects.all()
        print(f"Found {game_milestones.count()} game milestones.")
        
        # Get all strategy milestones
        strategy_milestones = StrategyMilestone.objects.all()
        print(f"Found {strategy_milestones.count()} strategy milestones.")
        
        # Create a mapping of milestone titles to strategy milestone status
        strategy_milestone_status = {m.title: m.status for m in strategy_milestones}
        
        # Update game milestones based on strategy milestone status
        updates = 0
        for game_milestone in game_milestones:
            if game_milestone.title in strategy_milestone_status:
                strategy_status = strategy_milestone_status[game_milestone.title]
                if game_milestone.status != strategy_status:
                    print(f"Updating {game_milestone.title} status from {game_milestone.status} to {strategy_status}")
                    game_milestone.status = strategy_status
                    game_milestone.save()
                    updates += 1
        
        print(f"Updated {updates} game milestones to match strategy milestones.")
    except Exception as e:
        print(f"Error syncing game milestones with strategy milestones: {e}")

def sync_strategy_milestones_with_game():
    """Sync StrategyMilestone status with GameMilestone status."""
    print("\n=== SYNCING STRATEGY MILESTONES WITH GAME MILESTONES ===")
    
    try:
        # Get all game milestones
        game_milestones = GameMilestone.objects.all()
        print(f"Found {game_milestones.count()} game milestones.")
        
        # Get all strategy milestones
        strategy_milestones = StrategyMilestone.objects.all()
        print(f"Found {strategy_milestones.count()} strategy milestones.")
        
        # Create a mapping of milestone titles to game milestone status
        game_milestone_status = {m.title: m.status for m in game_milestones}
        
        # Update strategy milestones based on game milestone status
        updates = 0
        for strategy_milestone in strategy_milestones:
            if strategy_milestone.title in game_milestone_status:
                game_status = game_milestone_status[strategy_milestone.title]
                if strategy_milestone.status != game_status:
                    print(f"Updating {strategy_milestone.title} status from {strategy_milestone.status} to {game_status}")
                    strategy_milestone.status = game_status
                    strategy_milestone.save()
                    updates += 1
        
        print(f"Updated {updates} strategy milestones to match game milestones.")
    except Exception as e:
        print(f"Error syncing strategy milestones with game milestones: {e}")

def main():
    """Main function to run all the fixes."""
    print("=== FIXING STRATEGY MILESTONES ===")
    
    # Check the current state of the StrategyMilestone model
    check_strategy_model()
    
    # Create and apply the migration
    create_migration()
    apply_migration()
    
    # Update the fixture file
    update_fixture_file()
    
    # Sync milestones between game and strategy
    sync_game_milestones_with_strategy()
    sync_strategy_milestones_with_game()
    
    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
