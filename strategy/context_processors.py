"""
Context processors for the strategy app.
These functions add variables to the template context for all templates.
"""
from .models import StrategyPhase, StrategyMilestone

def strategy_milestone_info(request):
    """
    Add strategy milestone info to the context.
    This includes the current in-progress milestone and company phase.
    """
    # Default values (fallback)
    in_progress_milestone = None
    company_phase = None
    
    try:
        # Find in-progress milestone in the strategy app
        strategy_milestones = StrategyMilestone.objects.filter(status='in_progress')
        
        if strategy_milestones.exists():
            # Get the first in-progress milestone
            in_progress_milestone = strategy_milestones.first()
            
            # Get the associated phase
            phase = in_progress_milestone.phase
            
            # Create a simple phase object for the template
            class CompanyPhase:
                def __init__(self, phase_obj):
                    self.id = phase_obj.id
                    self.name = phase_obj.name
                    self.phase_type = phase_obj.phase_type
                    self.order = phase_obj.order
            
            company_phase = CompanyPhase(phase)
    except Exception as e:
        print(f"Error in strategy_milestone_info context processor: {str(e)}")
    
    # Return context variables
    return {
        'strategy_in_progress_milestone': in_progress_milestone,
        'strategy_company_phase': company_phase
    }
