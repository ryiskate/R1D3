#!/usr/bin/env python
"""
Script to fix the milestone update view issue in the strategy dashboard.
This script creates a patched version of the view that only updates milestones within the same phase.
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.db import transaction
from strategy.models import StrategyPhase, StrategyMilestone
from strategy.views import StrategyMilestoneUpdateView

def print_milestone_status():
    """Print the current status of all milestones grouped by phase."""
    print("\nCurrent milestone status:")
    phases = StrategyPhase.objects.all().order_by('id')
    
    for phase in phases:
        print(f"\nPhase: {phase.name} (ID: {phase.id})")
        milestones = StrategyMilestone.objects.filter(phase=phase).order_by('order')
        
        for milestone in milestones:
            print(f"  - {milestone.title} (ID: {milestone.id}): {milestone.status}")

def patch_milestone_update_view():
    """
    Patch the StrategyMilestoneUpdateView.post method to only update milestones
    within the same phase when setting a milestone to 'in_progress'.
    """
    original_post = StrategyMilestoneUpdateView.post
    
    def patched_post(self, request, *args, **kwargs):
        """
        Patched version of the post method that only updates milestones
        within the same phase when setting a milestone to 'in_progress'.
        """
        phase_id = kwargs.get('phase_id')
        milestone_id = kwargs.get('milestone_id')
        
        try:
            phase = StrategyPhase.objects.get(id=phase_id)
            milestone = StrategyMilestone.objects.get(id=milestone_id, phase=phase)
        except (StrategyPhase.DoesNotExist, StrategyMilestone.DoesNotExist):
            print(f"Error: Phase ID {phase_id} or Milestone ID {milestone_id} not found")
            return original_post(self, request, *args, **kwargs)
        
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        status = request.POST.get('status')
        
        # Check if we're setting this milestone to in_progress
        if status == 'in_progress' and milestone.status != 'in_progress':
            print(f"Setting milestone '{milestone.title}' to 'in_progress'")
            print(f"Will update other in-progress milestones ONLY in phase '{phase.name}'")
            
            # Set all other in-progress milestones IN THE SAME PHASE to not_started
            with transaction.atomic():
                in_progress_milestones = StrategyMilestone.objects.filter(
                    phase=phase,
                    status='in_progress'
                ).exclude(id=milestone_id)
                
                for other_milestone in in_progress_milestones:
                    print(f"  - Changing milestone '{other_milestone.title}' from 'in_progress' to 'not_started'")
                    other_milestone.status = 'not_started'
                    other_milestone.save()
        
        # Continue with the original method
        return original_post(self, request, *args, **kwargs)
    
    # Replace the original post method with our patched version
    StrategyMilestoneUpdateView.post = patched_post
    print("Successfully patched StrategyMilestoneUpdateView.post method")

def create_direct_fix_script():
    """Create a direct fix script that can be applied to the views.py file."""
    fix_script = """
# Find this block in strategy/views.py around line 510-525:

        # Check if we're setting this milestone to in_progress
        if status == 'in_progress' and milestone.status != 'in_progress':
            # Set all other in-progress milestones to not_started
            in_progress_milestones = StrategyMilestone.objects.filter(status='in_progress').exclude(id=milestone_id)
            for other_milestone in in_progress_milestones:
                other_milestone.status = 'not_started'
                other_milestone.save()
                messages.info(request, f"Milestone '{other_milestone.title}' was changed from 'In Progress' to 'Not Started'")

# Replace it with this code that only updates milestones in the same phase:

        # Check if we're setting this milestone to in_progress
        if status == 'in_progress' and milestone.status != 'in_progress':
            # Set all other in-progress milestones IN THE SAME PHASE to not_started
            in_progress_milestones = StrategyMilestone.objects.filter(
                phase_id=phase_id,
                status='in_progress'
            ).exclude(id=milestone_id)
            for other_milestone in in_progress_milestones:
                other_milestone.status = 'not_started'
                other_milestone.save()
                messages.info(request, f"Milestone '{other_milestone.title}' was changed from 'In Progress' to 'Not Started'")
"""
    
    print("\nDirect Fix Script:")
    print("=" * 80)
    print(fix_script)
    print("=" * 80)

def main():
    """Main function to run the script."""
    print("Milestone Update View Fix Script")
    print("=" * 40)
    
    # Print current milestone status
    print_milestone_status()
    
    # Patch the view
    patch_milestone_update_view()
    
    # Create direct fix script
    create_direct_fix_script()
    
    print("\nFix applied successfully!")
    print("You can now try editing milestones again.")
    print("If you want to make this fix permanent, update the strategy/views.py file using the Direct Fix Script above.")

if __name__ == "__main__":
    main()
