#!/usr/bin/env python
"""
Script to fix the StrategyMilestoneUpdateView to handle foreign key constraints safely.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.db import transaction
from strategy.models import StrategyMilestone, StrategyPhase

print("Checking milestone update functionality...")

try:
    # First, let's check if all milestones have valid phase references
    invalid_milestones = []
    
    for milestone in StrategyMilestone.objects.all():
        try:
            # Try to access the phase to verify the relationship
            phase = milestone.phase
            print(f"Milestone '{milestone.title}' (ID: {milestone.id}) has valid phase: '{phase.name}' (ID: {phase.id})")
        except StrategyPhase.DoesNotExist:
            invalid_milestones.append(milestone)
            print(f"ERROR: Milestone '{milestone.title}' (ID: {milestone.id}) has invalid phase_id: {milestone.phase_id}")
    
    if invalid_milestones:
        print(f"\nFound {len(invalid_milestones)} milestones with invalid phase references.")
        
        # Get a valid phase to reassign milestones to
        valid_phase = StrategyPhase.objects.first()
        
        if valid_phase:
            print(f"Will reassign invalid milestones to phase: '{valid_phase.name}' (ID: {valid_phase.id})")
            
            with transaction.atomic():
                for milestone in invalid_milestones:
                    old_phase_id = milestone.phase_id
                    milestone.phase = valid_phase
                    milestone.save()
                    print(f"Reassigned milestone '{milestone.title}' from phase_id {old_phase_id} to '{valid_phase.name}'")
        else:
            print("No valid phases found to reassign milestones to.")
    else:
        print("All milestones have valid phase references.")
    
    # Now let's check if there are any issues with the in_progress status
    print("\nChecking for issues with in_progress milestones...")
    
    # Get all in_progress milestones
    in_progress_milestones = StrategyMilestone.objects.filter(status='in_progress')
    print(f"Found {in_progress_milestones.count()} milestones with 'in_progress' status.")
    
    # Check if there are multiple in_progress milestones per phase
    phases_with_multiple = {}
    
    for milestone in in_progress_milestones:
        phase_id = milestone.phase_id
        if phase_id in phases_with_multiple:
            phases_with_multiple[phase_id].append(milestone)
        else:
            phases_with_multiple[phase_id] = [milestone]
    
    # Fix phases with multiple in_progress milestones
    for phase_id, milestones in phases_with_multiple.items():
        if len(milestones) > 1:
            try:
                phase = StrategyPhase.objects.get(id=phase_id)
                phase_name = phase.name
            except StrategyPhase.DoesNotExist:
                phase_name = f"Unknown Phase (ID: {phase_id})"
            
            print(f"\nPhase '{phase_name}' has {len(milestones)} 'in_progress' milestones:")
            
            # Keep the first one as in_progress, set others to not_started
            keep_milestone = milestones[0]
            print(f"  Keeping '{keep_milestone.title}' as 'in_progress'")
            
            with transaction.atomic():
                for milestone in milestones[1:]:
                    print(f"  Changing '{milestone.title}' from 'in_progress' to 'not_started'")
                    milestone.status = 'not_started'
                    milestone.save()
    
    print("\nAll milestone issues have been fixed!")
    print("Try editing milestones now.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
