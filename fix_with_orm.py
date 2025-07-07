"""
Script to fix the strategy milestones issue using Django ORM.
This script will:
1. Load milestone data from the fixture file
2. Sync milestone statuses between game and strategy models
"""
import os
import django
import json
import sys
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Now import Django models
from django.db import transaction
from django.utils import timezone
from strategy.models import StrategyPhase, StrategyMilestone
from projects.game_models import GameMilestone

def load_phases():
    """Load strategy phases into the database."""
    print("\n=== LOADING PHASES ===")
    
    # Clear existing phases
    StrategyPhase.objects.all().delete()
    
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
    for phase_data in phases:
        phase = StrategyPhase.objects.create(
            name=phase_data['name'],
            phase_type=phase_data['phase_type'],
            description=phase_data['description'],
            order=phase_data['order'],
            start_year=phase_data['start_year'],
            end_year=phase_data['end_year'],
            is_current=phase_data['is_current'],
            status=phase_data['status']
        )
        print(f"Created phase: {phase.name}")
    
    print("Phases loaded successfully.")

def load_milestones():
    """Load milestones from fixture file."""
    print("\n=== LOADING MILESTONES ===")
    
    # Clear existing milestones
    StrategyMilestone.objects.all().delete()
    
    # Load fixture file
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
            for milestone_data in milestones:
                milestone = StrategyMilestone.objects.create(
                    title=milestone_data['title'],
                    description=milestone_data['description'],
                    status=milestone_data['status'],
                    order=milestone_data['order'],
                    phase=phase,
                    completion_date=timezone.now() if milestone_data['status'] == 'completed' else None
                )
                print(f"Added milestone: {milestone.title} (Status: {milestone.status})")
        
        print("Milestones loaded successfully.")
    except Exception as e:
        print(f"Error loading milestones: {e}")
        import traceback
        traceback.print_exc()

def sync_milestones():
    """Sync milestone statuses between game and strategy models."""
    print("\n=== SYNCING MILESTONES ===")
    
    # Get all game milestones
    game_milestones = GameMilestone.objects.all()
    
    if not game_milestones:
        print("No game milestones found.")
        return
    
    print(f"Found {game_milestones.count()} game milestones.")
    
    # Update strategy milestones with matching titles
    for game_milestone in game_milestones:
        try:
            strategy_milestone = StrategyMilestone.objects.get(title=game_milestone.title)
            
            # Update if status is different
            if strategy_milestone.status != game_milestone.status:
                old_status = strategy_milestone.status
                strategy_milestone.status = game_milestone.status
                
                # Update completion date if needed
                if game_milestone.status == 'completed' and not strategy_milestone.completion_date:
                    strategy_milestone.completion_date = timezone.now()
                
                strategy_milestone.save()
                print(f"Updated milestone '{game_milestone.title}' status from '{old_status}' to '{game_milestone.status}'")
        except StrategyMilestone.DoesNotExist:
            print(f"No matching strategy milestone found for '{game_milestone.title}'")
    
    print("Milestone sync completed.")

def check_results():
    """Check the results of the fix."""
    print("\n=== CHECKING RESULTS ===")
    
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
    
    # Find inconsistencies
    inconsistencies = 0
    for game_milestone in game_milestones:
        try:
            strategy_milestone = StrategyMilestone.objects.get(title=game_milestone.title)
            if game_milestone.status != strategy_milestone.status:
                inconsistencies += 1
                print(f"❌ Inconsistency: '{game_milestone.title}' - Game: {game_milestone.status}, Strategy: {strategy_milestone.status}")
        except StrategyMilestone.DoesNotExist:
            print(f"⚠️ Warning: No strategy milestone found for game milestone '{game_milestone.title}'")
    
    if inconsistencies == 0:
        print("✅ All milestone statuses are consistent between game and strategy models!")
    else:
        print(f"Found {inconsistencies} inconsistencies between game and strategy milestones.")

@transaction.atomic
def main():
    """Main function to run the fix."""
    print("=== FIXING STRATEGY MILESTONES ===")
    
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
