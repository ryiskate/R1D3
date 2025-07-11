from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from core.mixins import BreadcrumbMixin
from .models import Vision, Goal, Objective, KeyResult, StrategyPhase, StrategyMilestone
from .forms import VisionForm, GoalForm, ObjectiveForm, KeyResultForm, StrategyPhaseForm, StrategyMilestoneForm


class StrategyDashboardView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """
    Dashboard view for strategy section - redirects to company strategy
    """
    template_name = 'strategy/company_strategy.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get phases from the database
        db_phases = StrategyPhase.objects.all().order_by('order')
        
        # Convert phases to dictionaries for template
        phases = []
        for phase_obj in db_phases:
            phase = {
                'id': phase_obj.id,
                'name': phase_obj.name,
                'phase_type': phase_obj.phase_type,
                'description': phase_obj.description,
                'order': phase_obj.order,
                'is_current': phase_obj.status == 'in_progress',
                'status': phase_obj.status,
                'milestones': []
            }
            phases.append(phase)
        
        # Initialize variables for tracking phase status
        has_in_progress_milestone = False
        in_progress_phase_id = None
        
        # Initialize session storage if needed
        if 'user_milestones' not in self.request.session:
            self.request.session['user_milestones'] = {}
        
        # Load milestones for each phase from the database
        for phase in phases:
            # Get milestones from database
            db_milestones = StrategyMilestone.objects.filter(phase_id=phase['id']).order_by('order')
            
            # Convert to dictionaries for template
            milestones = []
            for m in db_milestones:
                milestone_dict = {
                    'id': m.id,
                    'title': m.title,
                    'description': m.description,
                    'order': m.order,
                    'status': m.status,
                    'is_completed': m.status == 'completed'  # For backward compatibility
                }
                
                if m.completion_date:
                    milestone_dict['completion_date'] = m.completion_date.isoformat()
                    
                milestones.append(milestone_dict)
            
            # Update session storage
            self.request.session['user_milestones'][str(phase['id'])] = milestones
            self.request.session.modified = True
            
            # Add milestones to phase
            phase['milestones'] = milestones
            
            # Check if this phase has an in-progress milestone
            for milestone in milestones:
                if milestone['status'] == 'in_progress':
                    has_in_progress_milestone = True
                    in_progress_phase_id = phase['id']
                    phase['is_current'] = True
        
        # Mark the first phase as current if no phase has an in-progress milestone
        if not has_in_progress_milestone and phases:
            phases[0]['is_current'] = True
        
        # Calculate progress for each phase
        for phase in phases:
            milestones = phase.get('milestones', [])
            total_milestones = len(milestones)
            
            if total_milestones > 0:
                completed_milestones = sum(1 for m in milestones if m['status'] == 'completed')
                progress_percentage = int((completed_milestones / total_milestones) * 100)
            else:
                completed_milestones = 0
                progress_percentage = 0
                
            phase['completed_milestones'] = completed_milestones
            phase['total_milestones'] = total_milestones
            phase['progress_percentage'] = progress_percentage
            
            # Set phase status based on milestone completion
            if completed_milestones == total_milestones and total_milestones > 0:
                phase['status'] = 'completed'
            elif has_in_progress_milestone and phase['id'] == in_progress_phase_id:
                phase['status'] = 'in_progress'
            else:
                phase['status'] = 'not_started'
        
        # Mark the phase with in-progress milestone as current
        if has_in_progress_milestone and in_progress_phase_id:
            for phase in phases:
                if phase['id'] == in_progress_phase_id:
                    phase['is_current'] = True
                    break
        # If no phase has an in-progress milestone, keep phase 1 as current (default)
        elif not has_in_progress_milestone:
            phases[0]['is_current'] = True
        
        # Add phases to context
        context['phases'] = phases
        
        # Find the current in-progress milestone and its phase for the blue banner
        in_progress_milestone = None
        company_phase = None
        
        for phase in phases:
            for milestone in phase['milestones']:
                if milestone['status'] == 'in_progress':
                    in_progress_milestone = milestone
                    company_phase = phase
                    break
            if in_progress_milestone:
                break
        
        # Add the in-progress milestone and its phase to the context for the blue banner
        context['in_progress_milestone'] = in_progress_milestone
        context['company_phase'] = company_phase
        
        return context


class VisionListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    List all company visions
    """
    model = Vision
    template_name = 'strategy/vision_list.html'
    context_object_name = 'visions'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': 'Visions', 'url': None}
        ]


class VisionDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """
    View details of a specific vision
    """
    model = Vision
    template_name = 'strategy/vision_detail.html'
    context_object_name = 'vision'
    
    def get_breadcrumbs(self):
        vision = self.get_object()
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': 'Visions', 'url': reverse('strategy:vision_list')},
            {'title': vision.title, 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goals'] = self.object.goals.all()
        return context


class VisionCreateView(BreadcrumbMixin, LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a new company vision
    """
    model = Vision
    form_class = VisionForm
    template_name = 'strategy/vision_form.html'
    success_url = reverse_lazy('strategy:vision_list')
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': 'Visions', 'url': reverse('strategy:vision_list')},
            {'title': 'New Vision', 'url': None}
        ]
    
    def test_func(self):
        # Only allow staff members to create visions
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, "Vision created successfully!")
        return super().form_valid(form)


class GoalListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    List all strategic goals
    """
    model = Goal
    template_name = 'strategy/goal_list.html'
    context_object_name = 'goals'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': 'Goals', 'url': None}
        ]


class GoalDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """
    View details of a specific goal
    """
    model = Goal
    template_name = 'strategy/goal_detail.html'
    context_object_name = 'goal'
    
    def get_breadcrumbs(self):
        goal = self.get_object()
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': 'Goals', 'url': reverse('strategy:goal_list')},
            {'title': goal.title, 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objectives'] = self.object.objectives.all()
        return context


class ObjectiveListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    List all objectives (OKRs)
    """
    model = Objective
    template_name = 'strategy/objective_list.html'
    context_object_name = 'objectives'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': 'Objectives', 'url': None}
        ]
    
    def get_queryset(self):
        return Objective.objects.filter(is_completed=False)


class CompanyStrategyView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """
    View for displaying the company's growth strategy roadmap
    """
    template_name = 'strategy/company_strategy.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        # Redirect to the dashboard view since they're now the same
        from django.shortcuts import redirect
        return redirect('strategy:dashboard')
        
    def get(self, request, *args, **kwargs):
        # Redirect to the dashboard view since they're now the same
        from django.shortcuts import redirect
        return redirect('strategy:dashboard')


class StrategyPhaseDetailView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """
    Detail view for a strategy phase
    """
    template_name = 'strategy/phase_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the phase ID from the URL
        phase_id = int(self.kwargs.get('pk'))
        
        # Get the phase from the database
        try:
            phase_obj = StrategyPhase.objects.get(id=phase_id)
        except StrategyPhase.DoesNotExist:
            # If phase not found, redirect to the company strategy page
            return redirect('strategy:dashboard')
        
        # Convert phase to dictionary for template
        phase = {
            'id': phase_obj.id,
            'name': phase_obj.name,
            'phase_type': phase_obj.phase_type,
            'description': phase_obj.description,
            'order': phase_obj.order,
            'is_current': phase_obj.status == 'in_progress',
            'status': phase_obj.status,
            'milestones': []
        }
        
        # Get milestones from the database
        db_milestones = StrategyMilestone.objects.filter(phase=phase_obj).order_by('order')
        
        # Convert milestones to dictionaries for template
        all_milestones = []
        for m in db_milestones:
            milestone_dict = {
                'id': m.id,
                'title': m.title,
                'description': m.description,
                'order': m.order,
                'status': m.status,
                'is_completed': m.status == 'completed'  # For backward compatibility
            }
            
            if m.completion_date:
                milestone_dict['completion_date'] = m.completion_date.isoformat()
                
            all_milestones.append(milestone_dict)
        
        # Update session storage for consistency
        if 'user_milestones' not in self.request.session:
            self.request.session['user_milestones'] = {}
            
        self.request.session['user_milestones'][str(phase_id)] = all_milestones
        self.request.session.modified = True
        
        phase['milestones'] = all_milestones
        context['phase'] = phase
        context['milestones'] = all_milestones
        
        # Calculate completed milestones and progress percentage
        completed_milestones = sum(1 for m in all_milestones if m['status'] == 'completed')
        context['completed_milestones'] = completed_milestones
        
        total_milestones = len(all_milestones)
        if total_milestones > 0:
            progress_percentage = int((completed_milestones / total_milestones) * 100)
        else:
            progress_percentage = 0
        context['progress_percentage'] = progress_percentage
        
        return context
    
    def get_breadcrumbs(self):
        # Get the phase ID from the URL
        phase_id = self.kwargs.get('pk')
        
        try:
            # Get phase name from database
            phase = StrategyPhase.objects.get(id=phase_id)
            phase_name = phase.name
        except StrategyPhase.DoesNotExist:
            phase_name = 'Strategy Phase'
        
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': phase_name, 'url': None}
        ]



class PhaseEditRedirectView(LoginRequiredMixin, View):
    """
    Redirect view for phase edit URLs - phases are hardcoded and should not be editable
    """
    def get(self, request, *args, **kwargs):
        phase_id = kwargs.get('pk')
        messages.info(request, 'Phase editing has been disabled. Phases are hardcoded in the system.')
        return redirect('strategy:phase_detail', pk=phase_id)

    def post(self, request, *args, **kwargs):
        phase_id = kwargs.get('pk')
        messages.info(request, 'Phase editing has been disabled. Phases are hardcoded in the system.')
        return redirect('strategy:phase_detail', pk=phase_id)


class PhaseCreateRedirectView(LoginRequiredMixin, View):
    """
    Redirect view for phase create URLs - phases are hardcoded and should not be created
    """
    def get(self, request, *args, **kwargs):
        messages.info(request, 'Phase creation has been disabled. Phases are hardcoded in the system.')
        return redirect('strategy:company_strategy')

    def post(self, request, *args, **kwargs):
        messages.info(request, 'Phase creation has been disabled. Phases are hardcoded in the system.')
        return redirect('strategy:company_strategy')


class StrategyMilestoneUpdateView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """
    Update view for strategy milestones
    """
    template_name = 'strategy/milestone_form.html'
    
    def get(self, request, *args, **kwargs):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Get the phase and milestone from the database
        try:
            phase = StrategyPhase.objects.get(id=phase_id)
            milestone = StrategyMilestone.objects.get(id=milestone_id, phase=phase)
        except (StrategyPhase.DoesNotExist, StrategyMilestone.DoesNotExist):
            messages.error(request, 'Strategy phase or milestone not found.')
            return redirect('strategy:dashboard')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Update Strategy Milestone'
        context['submit_text'] = 'Update Milestone'
        context['is_update'] = True
        
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Get the phase and milestone from the database
        try:
            phase = StrategyPhase.objects.get(id=phase_id)
            milestone = StrategyMilestone.objects.get(id=milestone_id, phase=phase)
        except (StrategyPhase.DoesNotExist, StrategyMilestone.DoesNotExist):
            messages.error(self.request, 'Strategy phase or milestone not found.')
            return redirect('strategy:dashboard')
        
        # Convert phase to dictionary for template
        context['phase'] = {
            'id': phase.id,
            'name': phase.name,
            'phase_type': phase.phase_type,
            'description': phase.description
        }
        
        # Convert milestone to dictionary for template
        context['milestone'] = {
            'id': milestone.id,
            'title': milestone.title,
            'description': milestone.description,
            'order': milestone.order,
            'status': milestone.status,
            'completion_date': milestone.completion_date.isoformat() if milestone.completion_date else None
        }
        
        context['form_action'] = reverse('strategy:milestone_update', kwargs={'phase_id': phase_id, 'milestone_id': milestone_id})
        
        # Also update the session storage for consistency
        if 'user_milestones' in self.request.session:
            phase_id_str = str(phase_id)
            if phase_id_str in self.request.session['user_milestones']:
                # Find and update the milestone in session
                for i, m in enumerate(self.request.session['user_milestones'][phase_id_str]):
                    if m['id'] == milestone_id:
                        self.request.session['user_milestones'][phase_id_str][i] = context['milestone']
                        self.request.session.modified = True
                        break
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Get the phase and milestone from the database
        try:
            phase = StrategyPhase.objects.get(id=phase_id)
            milestone = StrategyMilestone.objects.get(id=milestone_id, phase=phase)
        except (StrategyPhase.DoesNotExist, StrategyMilestone.DoesNotExist):
            messages.error(request, 'Strategy phase or milestone not found.')
            return redirect('strategy:dashboard')
        
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        status = request.POST.get('status')
        
        # Validate form data
        if not title or not description or not order or not status:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('strategy:milestone_update', phase_id=phase_id, milestone_id=milestone_id)
        
        # Check if we're setting this milestone to in_progress
        if status == 'in_progress' and milestone.status != 'in_progress':
            # Set all other in-progress milestones to not_started
            in_progress_milestones = StrategyMilestone.objects.filter(status='in_progress').exclude(id=milestone_id)
            for other_milestone in in_progress_milestones:
                other_milestone.status = 'not_started'
                other_milestone.save()
                messages.info(request, f"Milestone '{other_milestone.title}' was changed from 'In Progress' to 'Not Started'")
        
        # Update completion date if status is changing to/from completed
        if status == 'completed' and milestone.status != 'completed':
            milestone.completion_date = timezone.now().date()
        elif status != 'completed' and milestone.status == 'completed':
            milestone.completion_date = None
        
        # Update the milestone in the database
        milestone.title = title
        milestone.description = description
        milestone.order = int(order)
        milestone.status = status
        milestone.save()
        
        # Also update the session storage for consistency
        if 'user_milestones' in request.session:
            phase_id_str = str(phase_id)
            if phase_id_str in request.session['user_milestones']:
                # Find and update the milestone in session
                for i, m in enumerate(request.session['user_milestones'][phase_id_str]):
                    if m['id'] == milestone_id:
                        session_milestone = {
                            'id': milestone.id,
                            'title': milestone.title,
                            'description': milestone.description,
                            'order': milestone.order,
                            'status': milestone.status
                        }
                        
                        if milestone.completion_date:
                            session_milestone['completion_date'] = milestone.completion_date.isoformat()
                            
                        request.session['user_milestones'][phase_id_str][i] = session_milestone
                        request.session.modified = True
                        break
        
        # Show success message
        messages.success(request, f'Milestone "{title}" updated successfully!')
        
        # Redirect to the phase detail page
        return redirect('strategy:phase_detail', pk=phase_id)
    
    def get_breadcrumbs(self):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        try:
            # Get phase name from database
            phase = StrategyPhase.objects.get(id=phase_id)
            phase_name = phase.name
        except StrategyPhase.DoesNotExist:
            phase_name = 'Strategy Phase'
        
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': phase_name, 'url': reverse('strategy:phase_detail', kwargs={'pk': phase_id})},
            {'title': 'Update Milestone', 'url': None}
        ]


class StrategyMilestoneDeleteView(BreadcrumbMixin, LoginRequiredMixin, View):
    """
    Delete view for strategy milestones
    """
    def get(self, request, *args, **kwargs):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Delete the milestone from the database
        try:
            phase = StrategyPhase.objects.get(id=phase_id)
            milestone = StrategyMilestone.objects.get(id=milestone_id, phase=phase)
            milestone_title = milestone.title
            milestone.delete()
            
            # Also delete from session for consistency
            if 'user_milestones' in request.session:
                if str(phase_id) in request.session['user_milestones']:
                    request.session['user_milestones'][str(phase_id)] = [
                        m for m in request.session['user_milestones'][str(phase_id)] 
                        if m['id'] != milestone_id
                    ]
                    request.session.modified = True
            
            messages.success(request, f'Strategy milestone "{milestone_title}" deleted successfully!')
        except (StrategyPhase.DoesNotExist, StrategyMilestone.DoesNotExist):
            messages.error(request, 'Strategy phase or milestone not found.')
        
        return redirect('strategy:phase_detail', pk=phase_id)
    
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
    def get_breadcrumbs(self):
        phase_id = int(self.kwargs.get('phase_id'))
        
        try:
            # Get phase name from database
            phase = StrategyPhase.objects.get(id=phase_id)
            phase_name = phase.name
        except StrategyPhase.DoesNotExist:
            phase_name = 'Strategy Phase'
        
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': phase_name, 'url': reverse('strategy:phase_detail', kwargs={'pk': phase_id})},
            {'title': 'Delete Milestone', 'url': None}
        ]


class StrategyMilestoneDeleteView(BreadcrumbMixin, LoginRequiredMixin, DeleteView):
    model = StrategyMilestone
    template_name = 'strategy/strategy_milestone_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('strategy:strategy_milestones')
        context['is_update'] = False
        context['form_title'] = 'Create Strategy Milestone'
        context['submit_text'] = 'Create Milestone'
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Get the phase ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        
        try:
            phase = StrategyPhase.objects.get(id=phase_id)
        except StrategyPhase.DoesNotExist:
            messages.error(request, 'Strategy phase not found.')
            return redirect('strategy:dashboard')
        
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        status = request.POST.get('status')
        
        # Validate form data
        if not title or not description or not order or not status:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('strategy:milestone_create', phase_id=phase_id)
        
        # Check if another milestone is already in progress
        if status == 'in_progress':
            # Set all other in-progress milestones to not_started
            in_progress_milestones = StrategyMilestone.objects.filter(status='in_progress')
            for milestone in in_progress_milestones:
                milestone.status = 'not_started'
                milestone.save()
                messages.info(request, f"Milestone '{milestone.title}' was changed from 'In Progress' to 'Not Started'")
        
        # Create a new milestone in the database
        completion_date = None
        if status == 'completed':
            completion_date = timezone.now().date()
            
        new_milestone = StrategyMilestone.objects.create(
            title=title,
            description=description,
            phase=phase,
            order=int(order),
            status=status,
            completion_date=completion_date
        )
        
        # Also update the session storage for consistency
        if 'user_milestones' not in request.session:
            request.session['user_milestones'] = {}
            
        phase_id_str = str(phase_id)
        if phase_id_str not in request.session['user_milestones']:
            request.session['user_milestones'][phase_id_str] = []
        
        # Add to session
        session_milestone = {
            'id': new_milestone.id,
            'title': title,
            'description': description,
            'order': int(order),
            'status': status
        }
        
        if completion_date:
            session_milestone['completion_date'] = completion_date.isoformat()
            
        request.session['user_milestones'][phase_id_str].append(session_milestone)
        request.session.modified = True
        
        messages.success(request, f'Milestone "{title}" created successfully!')
        
        # Redirect to the phase detail page
        return redirect('strategy:phase_detail', pk=phase_id)
    
    def get_breadcrumbs(self):
        # Get the phase ID from the URL
        phase_id = self.kwargs.get('phase_id')
        
        try:
            # Get phase name from database
            phase = StrategyPhase.objects.get(id=phase_id)
            phase_name = phase.name
        except StrategyPhase.DoesNotExist:
            phase_name = 'Strategy Phase'
        
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': phase_name, 'url': reverse('strategy:phase_detail', kwargs={'pk': phase_id})},
            {'title': 'Create Milestone', 'url': None}
        ]


class StrategyMilestoneDeleteView(LoginRequiredMixin, View):
    """
    Delete view for strategy milestones using session storage
    """
    
    def get(self, request, *args, **kwargs):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Check if the milestone exists in session
        milestone_title = "Unknown Milestone"
        if 'user_milestones' in request.session and \
           str(phase_id) in request.session['user_milestones']:
            
            # Find the milestone to get its title before deletion
            phase_milestones = request.session['user_milestones'][str(phase_id)]
            for milestone in phase_milestones:
                if milestone['id'] == milestone_id:
                    milestone_title = milestone['title']
                    break
            
            # Remove the milestone from the session
            request.session['user_milestones'][str(phase_id)] = [
                m for m in phase_milestones if m['id'] != milestone_id
            ]
            request.session.modified = True
            
            messages.success(request, f'Milestone "{milestone_title}" deleted successfully!')
        else:
            messages.error(request, 'Milestone not found.')
        
        # Redirect to the phase detail page
        return redirect('strategy:phase_detail', pk=phase_id)
