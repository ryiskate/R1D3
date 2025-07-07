from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import StrategyMilestone, StrategyPhase


class MilestoneDebugView(LoginRequiredMixin, TemplateView):
    """
    Debug view to display all milestone-related context variables
    """
    template_name = 'strategy/debug_milestone.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add direct database query results
        # Get in-progress milestone directly from the database
        in_progress_milestones = StrategyMilestone.objects.filter(status='in_progress')
        if in_progress_milestones.exists():
            context['db_milestone'] = in_progress_milestones.first()
            context['db_phase'] = context['db_milestone'].phase
        else:
            context['db_milestone'] = None
            context['db_phase'] = None
        
        # Print debug info to console
        print("\n==== MILESTONE DEBUG VIEW ====\n")
        print(f"Strategy milestone from DB: {context.get('db_milestone')}")
        print(f"Strategy phase from DB: {context.get('db_phase')}")
        print(f"Strategy milestone from context: {context.get('strategy_in_progress_milestone')}")
        print(f"Strategy phase from context: {context.get('strategy_company_phase')}")
        print(f"Core milestone from context: {context.get('in_progress_milestone')}")
        print(f"Core phase from context: {context.get('company_phase')}")
        print("\n==== END MILESTONE DEBUG VIEW ====\n")
        
        return context
