"""
Context processors for the R1D3 system.
These functions add variables to the template context for all templates.
"""
from django.utils import timezone
from projects.game_models import GameMilestone
from types import SimpleNamespace

def get_phase_for_milestone(milestone_title):
    """
    Determine the appropriate company phase based on milestone title.
    This function maps milestone titles to their corresponding company phases.
    """
    # Print the milestone title for debugging
    print(f"Finding phase for milestone: {milestone_title}")
    
    # Phase 1: Indie Game Development milestones
    indie_milestones = [
        'Complete Game Development Course',
        'Release First Indie Game',
        'Build Game Portfolio',
        'Establish Online Presence'
    ]
    
    # Phase 2: Arcade Machine Development milestones
    arcade_milestones = [
        'Hardware Integration Research',
        'Prototype First Arcade Cabinet',
        'Develop Custom Controllers',
        'Launch First Arcade Location',
        'Open First Arcade Location'  # Added this milestone
    ]
    
    # Phase 3: Theme Park Attractions milestones
    theme_park_milestones = [
        'Theme Park Feasibility Study',
        'Attraction Prototype',
        'Land Acquisition',
        'First Attraction Launch'
    ]
    
    # Determine phase based on milestone title
    if milestone_title in indie_milestones:
        print(f"Milestone '{milestone_title}' mapped to Indie Game Development phase")
        return {
            'id': 1,
            'name': 'Indie Game Development',
            'phase_type': 'indie_dev',
            'phase_type_display': 'Indie Game Development',
            'order': 1
        }
    elif milestone_title in arcade_milestones:
        print(f"Milestone '{milestone_title}' mapped to Arcade Machine Development phase")
        return {
            'id': 2,
            'name': 'Arcade Machine Development',
            'phase_type': 'arcade',
            'phase_type_display': 'Arcade Machine Development',
            'order': 2
        }
    elif milestone_title in theme_park_milestones:
        print(f"Milestone '{milestone_title}' mapped to Theme Park Attractions phase")
        return {
            'id': 3,
            'name': 'Theme Park Attractions',
            'phase_type': 'theme_park',
            'phase_type_display': 'Theme Park Attractions',
            'order': 3
        }
    # Check for partial matches if no exact match was found
    elif 'theme park' in milestone_title.lower() or 'attraction' in milestone_title.lower():
        print(f"Milestone '{milestone_title}' partially matched to Theme Park Attractions phase")
        return {
            'id': 3,
            'name': 'Theme Park Attractions',
            'phase_type': 'theme_park',
            'phase_type_display': 'Theme Park Attractions',
            'order': 3
        }
    elif 'arcade' in milestone_title.lower() or 'cabinet' in milestone_title.lower():
        print(f"Milestone '{milestone_title}' partially matched to Arcade Machine Development phase")
        return {
            'id': 2,
            'name': 'Arcade Machine Development',
            'phase_type': 'arcade',
            'phase_type_display': 'Arcade Machine Development',
            'order': 2
        }
    elif 'indie' in milestone_title.lower() or 'game' in milestone_title.lower():
        print(f"Milestone '{milestone_title}' partially matched to Indie Game Development phase")
        return {
            'id': 1,
            'name': 'Indie Game Development',
            'phase_type': 'indie_dev',
            'phase_type_display': 'Indie Game Development',
            'order': 1
        }
    else:
        print(f"Milestone '{milestone_title}' not found in any phase, defaulting to Indie Game Development")
        # Default to phase 1 if milestone title doesn't match any known phase
        return {
            'id': 1,
            'name': 'Indie Game Development',
            'phase_type': 'indie_dev',
            'phase_type_display': 'Indie Game Development',
            'order': 1
        }

def breadcrumbs_processor(request):
    """
    Add empty breadcrumbs list to context if not already present.
    Views can populate this list with breadcrumb items.
    
    Each breadcrumb item should be a dictionary with 'title' and 'url' keys.
    The last item in the list will be marked as active (no link).
    
    Example:
    breadcrumbs = [
        {'title': 'Dashboard', 'url': '/dashboard/'},
        {'title': 'Tasks', 'url': '/tasks/'},
        {'title': 'Task Title', 'url': None}  # Last item has no URL
    ]
    """
    return {
        'breadcrumbs': getattr(request, 'breadcrumbs', [])
    }

def milestone_info(request):
    """
    Add milestone info to the context.
    This includes the current in-progress milestone and company phase.
    """
    print("\n==== MILESTONE INFO CONTEXT PROCESSOR CALLED ====\n")
    print(f"Request path: {request.path}")
    
    # Create timestamp for cache busting
    import time
    import uuid
    timestamp = time.time()
    random_id = uuid.uuid4().hex[:8]
    
    # Default milestone and phase data (fallback values)
    milestone_title = 'Release First Indie Game'
    game_title = 'PeacefulFarm'
    phase_name = 'Indie Game Development'
    phase_type = 'indie_dev'
    phase_order = 1
    
    try:
        # Try to get the actual in-progress milestone from the database
        from projects.game_models import GameTask, GameMilestone
        
        # First check if there's an in-progress milestone in the strategy app
        print("Searching for in-progress strategy milestones...")
        try:
            from strategy.models import StrategyMilestone
            strategy_milestones = StrategyMilestone.objects.filter(status='in_progress')
            
            if strategy_milestones.exists():
                # Get the first in-progress strategy milestone
                strategy_milestone = strategy_milestones.first()
                milestone_title = strategy_milestone.title
                game_title = "Strategy"
                print(f"Found in-progress strategy milestone: {milestone_title}")
                
                # Get phase info based on milestone title
                phase_info = get_phase_for_milestone(milestone_title)
                phase_name = phase_info['name']
                phase_type = phase_info['phase_type']
                phase_order = phase_info['order']
                print(f"Phase determined from strategy milestone: {phase_name} (Type: {phase_type})")
                
                # Try to get the phase directly from the database
                try:
                    from strategy.models import StrategyPhase
                    phase = strategy_milestone.phase
                    phase_name = phase.name
                    phase_type = phase.phase_type
                    phase_order = phase.order
                    print(f"Phase retrieved from database: {phase_name} (Type: {phase_type})")
                except Exception as e:
                    print(f"Error getting phase from database: {str(e)}")
                    # Keep the phase info from get_phase_for_milestone
                
                # Return early with the strategy milestone data
                return {
                    'milestone_title': milestone_title,
                    'game_title': game_title,
                    'phase_name': phase_name,
                    'phase_type': phase_type,
                    'phase_order': phase_order,
                    'background_style': "background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);",
                    'timestamp': timestamp,
                    'random_id': random_id,
                    'in_progress_milestone': strategy_milestone,
                    'company_phase': CompanyPhase(phase_name, phase_type, phase_order),
                    'debug_info': {
                        'milestone': milestone_title,
                        'phase': phase_name,
                        'timestamp': timestamp,
                        'random_id': random_id
                    }
                }
        except Exception as e:
            print(f"Error checking strategy milestones: {str(e)}")
        
        # If no strategy milestone is in progress, check game milestones
        print("Searching for in-progress game milestones...")
        in_progress_milestones = GameMilestone.objects.filter(status='in_progress')
        
        if in_progress_milestones.exists():
            # Get the first in-progress milestone
            in_progress_milestone = in_progress_milestones.first()
            milestone_title = in_progress_milestone.title
            game_title = in_progress_milestone.game.title
            print(f"Found in-progress milestone directly: {milestone_title}")
            
            # Get phase info based on milestone title
            phase_info = get_phase_for_milestone(milestone_title)
            phase_name = phase_info['name']
            phase_type = phase_info['phase_type']
            phase_order = phase_info['order']
            print(f"Phase determined from milestone: {phase_name} (Type: {phase_type})")
        else:
            # If no non-completed milestones found, fall back to task-based detection
            print("No non-completed milestones found, checking tasks...")
            
            # Find tasks with 'in_progress' status
            in_progress_tasks = GameTask.objects.filter(status='in_progress')
            
            if in_progress_tasks.exists():
                # Get the first in-progress task
                in_progress_task = in_progress_tasks.first()
                print(f"Found in-progress task: {in_progress_task.title}")
                
                if in_progress_task and in_progress_task.milestone:
                    # Get milestone info from the in-progress task
                    milestone_title = in_progress_task.milestone.title
                    game_title = in_progress_task.game.title if in_progress_task.game else 'Unknown Game'
                    print(f"Associated milestone: {milestone_title}")
                    
                    # Update the milestone to be in progress
                    try:
                        milestone = in_progress_task.milestone
                        if milestone.status != 'in_progress':
                            milestone.status = 'in_progress'
                            milestone.save()
                            print(f"Updated milestone {milestone.title} to in-progress state")
                            print(f"Updated milestone status to in_progress")
                    except Exception as e:
                        print(f"Could not update milestone status: {str(e)}")
                    
                    # Get phase info based on milestone title
                    phase_info = get_phase_for_milestone(milestone_title)
                    phase_name = phase_info['name']
                    phase_type = phase_info['phase_type']
                    phase_order = phase_info['order']
                    print(f"Phase determined from milestone: {phase_name} (Type: {phase_type})")
                else:
                    print("In-progress task has no milestone, checking other sources")
                    
                    # Check if the task has company_section set to arcade
                    if in_progress_task and in_progress_task.company_section == 'arcade':
                        phase_name = 'Arcade Machine Development'
                        phase_type = 'arcade'
                        phase_order = 2
                        print(f"Using arcade phase based on task company section")
            else:
                print("No in-progress tasks found, using default values")
    except Exception as e:
        # If there's an error, use the default values
        print(f"Error fetching milestone data: {str(e)}")
        print("Using default milestone and phase data")
    
    # Set the background color based on the phase_type
    if phase_type == 'indie_dev':
        # Blue gradient for indie dev phase
        background_style = "background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);"
    elif phase_type == 'arcade':
        # Green gradient for arcade phase
        background_style = "background: linear-gradient(135deg, #1cc88a 0%, #13855c 100%);"
    elif phase_type == 'theme_park':
        # Purple gradient for theme park phase
        background_style = "background: linear-gradient(135deg, #6f42c1 0%, #4e2c8e 100%);"
    else:
        # Default blue gradient
        background_style = "background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);"
    
    # Print debug info
    print(f"Using milestone: {milestone_title}")
    print(f"Using phase: {phase_name} ({phase_type})")
    print(f"Background style: {background_style}")
    print(f"Timestamp: {timestamp}, ID: {random_id}")
    print("==== END OF MILESTONE INFO CONTEXT PROCESSOR ====\n")
    
    # Create a phase object for the template
    class CompanyPhase:
        def __init__(self, name, phase_type, order):
            self.name = name
            self.phase_type = phase_type
            self.order = order
    
    # Create phase object
    phase_obj = CompanyPhase(phase_name, phase_type, phase_order)
    
    # Get the actual milestone object if it exists
    in_progress_milestone = None
    try:
        # Try to find the milestone by title and status
        from projects.game_models import GameMilestone
        milestone_objects = GameMilestone.objects.filter(status='in_progress')
        if milestone_objects.exists():
            in_progress_milestone = milestone_objects.first()
    except Exception as e:
        print(f"Error getting milestone object: {str(e)}")
    
    # Return context variables
    return {
        'milestone_title': milestone_title,
        'game_title': game_title,
        'phase_name': phase_name,
        'phase_type': phase_type,
        'phase_order': phase_order,
        'background_style': background_style,
        'timestamp': timestamp,
        'random_id': random_id,
        'in_progress_milestone': in_progress_milestone,
        'company_phase': phase_obj,
        'debug_info': {
            'milestone': milestone_title,
            'phase': phase_name,
            'timestamp': timestamp,
            'random_id': random_id
        }
    }
