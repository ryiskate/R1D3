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
    print("\n==== STRATEGY MILESTONE INFO CONTEXT PROCESSOR CALLED ====\n")
    print(f"Request path: {request.path}")
    
    # Default values (fallback)
    in_progress_milestone = None
    company_phase = None
    
    try:
        # Find in-progress milestone in the strategy app using raw SQL query for debugging
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, phase_id, status FROM strategy_strategymilestone WHERE status = 'in_progress'")
            rows = cursor.fetchall()
            print(f"Raw SQL query found {len(rows)} in-progress milestones:")
            for row in rows:
                print(f"  ID: {row[0]}, Title: {row[1]}, Phase ID: {row[2]}, Status: {row[3]}")
        
        # Now try the ORM approach
        print("Searching for in-progress strategy milestones via ORM...")
        strategy_milestones = StrategyMilestone.objects.filter(status='in_progress')
        print(f"ORM found {strategy_milestones.count()} in-progress strategy milestones")
        
        if strategy_milestones.exists():
            # Get the first in-progress milestone
            in_progress_milestone = strategy_milestones.first()
            print(f"Using in-progress milestone: {in_progress_milestone.title} (ID: {in_progress_milestone.id})")
            
            try:
                # Get the associated phase
                phase = in_progress_milestone.phase
                print(f"Associated phase: {phase.name} (ID: {phase.id}, Type: {phase.phase_type}, Order: {phase.order})")
                
                # Create a simple phase object for the template
                class CompanyPhase:
                    def __init__(self, phase_obj):
                        self.id = phase_obj.id
                        self.name = phase_obj.name
                        self.phase_type = phase_obj.phase_type
                        self.order = phase_obj.order
                
                company_phase = CompanyPhase(phase)
            except Exception as phase_error:
                print(f"Error getting phase for milestone: {str(phase_error)}")
                # Try to get the phase directly
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute(f"SELECT id, name, phase_type, order_column FROM strategy_strategyphase WHERE id = {in_progress_milestone.phase_id}")
                        phase_row = cursor.fetchone()
                        if phase_row:
                            print(f"Found phase via direct SQL: ID: {phase_row[0]}, Name: {phase_row[1]}, Type: {phase_row[2]}, Order: {phase_row[3]}")
                            
                            class CompanyPhase:
                                def __init__(self, id, name, phase_type, order):
                                    self.id = id
                                    self.name = name
                                    self.phase_type = phase_type
                                    self.order = order
                            
                            company_phase = CompanyPhase(phase_row[0], phase_row[1], phase_row[2], phase_row[3])
                except Exception as direct_phase_error:
                    print(f"Error getting phase directly: {str(direct_phase_error)}")
        else:
            print("No in-progress strategy milestones found")
    except Exception as e:
        print(f"Error in strategy_milestone_info context processor: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Print debug info about what we're returning
    if in_progress_milestone:
        print(f"Returning milestone: {in_progress_milestone.title}")
    else:
        print("Returning None for milestone")
    
    if company_phase:
        print(f"Returning phase: {company_phase.name} (Order: {company_phase.order})")
    else:
        print("Returning None for company_phase")
    
    print("==== END OF STRATEGY MILESTONE INFO CONTEXT PROCESSOR ====\n")
    
    # Return context variables
    return {
        'strategy_in_progress_milestone': in_progress_milestone,
        'strategy_company_phase': company_phase
    }
