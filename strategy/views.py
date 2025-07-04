from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages

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
        
        # Define the phases with their basic information
        phases = [
            {
                'id': 1,
                'name': 'Indie Game Development',
                'phase_type': 'indie_dev',
                'description': 'Building a foundation in game development through education and indie projects. '
                               'Focus on learning game development tools, creating indie games, and establishing '
                               'industry connections.',
                'order': 1,
                'is_current': True,
                'is_completed': False,
                'milestones': []
            },
            {
                'id': 2,
                'name': 'Arcade Machine Development',
                'phase_type': 'arcade',
                'description': 'Expanding into physical gaming experiences through arcade machine development. '
                               'Learn hardware integration, develop custom controllers, create arcade-specific '
                               'game experiences, and establish arcade locations.',
                'order': 2,
                'is_current': False,
                'is_completed': False,
                'milestones': []
            },
            {
                'id': 3,
                'name': 'Theme Park Attractions',
                'phase_type': 'theme_park',
                'description': 'Creating immersive physical experiences through theme park attractions. '
                               'Develop 3D attractions and simulators, design and build roller coasters, '
                               'create themed environments, and establish full theme park experiences.',
                'order': 3,
                'is_current': False,
                'is_completed': False,
                'milestones': []
            }
        ]
        
        # Always ensure we have the initial milestones loaded
        import os
        import json
        
        # Only initialize milestones if they don't exist in the session
        if 'user_milestones' not in self.request.session:
            # Load initial milestones from fixtures
            file_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'initial_milestones.json')
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        initial_milestones = json.load(f)
                        self.request.session['user_milestones'] = initial_milestones
                        self.request.session.modified = True
                        messages.success(self.request, 'Initial milestones loaded successfully!')
                except Exception as e:
                    messages.error(self.request, f'Error loading initial milestones: {e}')
            else:
                messages.error(self.request, f'Initial milestones file not found at {file_path}')


        
        # Load milestones from session for each phase
        has_in_progress_milestone = False
        in_progress_phase_id = None
        
        if 'user_milestones' in self.request.session:
            for phase in phases:
                phase_id = str(phase['id'])
                if phase_id in self.request.session['user_milestones']:
                    phase['milestones'] = self.request.session['user_milestones'][phase_id]
                    
                    # Check if this phase has an in-progress milestone
                    for milestone in phase['milestones']:
                        if milestone.get('status') == 'in_progress':
                            has_in_progress_milestone = True
                            in_progress_phase_id = phase['id']
                            break
        
        # Calculate progress for each phase and set current phase based on in-progress milestone
        for phase in phases:
            # Reset is_current flag
            phase['is_current'] = False
            
            # Count completed milestones using status field
            completed_milestones = sum(1 for m in phase['milestones'] if m.get('status') == 'completed')
            total_milestones = len(phase['milestones'])
            
            if total_milestones > 0:
                phase['progress_percentage'] = int((completed_milestones / total_milestones) * 100)
            else:
                phase['progress_percentage'] = 0
                
            phase['completed_milestones'] = completed_milestones
            phase['total_milestones'] = total_milestones
            
            # Set is_completed based on all milestones being completed
            phase['is_completed'] = (completed_milestones == total_milestones and total_milestones > 0)
        
        # Mark the phase with in-progress milestone as current
        if has_in_progress_milestone and in_progress_phase_id:
            for phase in phases:
                if phase['id'] == in_progress_phase_id:
                    phase['is_current'] = True
                    break
        # If no phase has an in-progress milestone, keep phase 1 as current (default)
        elif not has_in_progress_milestone:
            phases[0]['is_current'] = True
        
        context['phases'] = phases
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
        
        # Define the phases with their basic information
        phases = [
            {
                'id': 1,
                'name': 'Indie Game Development',
                'phase_type': 'indie_dev',
                'description': 'Building a foundation in game development through education and indie projects. '
                               'Focus on learning game development tools, creating indie games, and establishing '
                               'industry connections.',
                'order': 1,
                'is_current': True,
                'is_completed': False,
                'milestones': []
            },
            {
                'id': 2,
                'name': 'Arcade Machine Development',
                'phase_type': 'arcade',
                'description': 'Expanding into physical gaming experiences through arcade machine development. '
                               'Learn hardware integration, develop custom controllers, create arcade-specific '
                               'game experiences, and establish arcade locations.',
                'order': 2,
                'is_current': False,
                'is_completed': False,
                'milestones': []
            },
            {
                'id': 3,
                'name': 'Theme Park Attractions',
                'phase_type': 'theme_park',
                'description': 'Creating immersive physical experiences through theme park attractions. '
                               'Develop 3D attractions and simulators, design and build roller coasters, '
                               'create themed environments, and establish full theme park experiences.',
                'order': 3,
                'is_current': False,
                'is_completed': False,
                'milestones': []
            }
        ]
        
        # Load milestones from session for each phase
        if 'user_milestones' in self.request.session:
            for phase in phases:
                phase_id_str = str(phase['id'])
                if phase_id_str in self.request.session['user_milestones']:
                    phase['milestones'] = self.request.session['user_milestones'][phase_id_str]
        
        # Get the phase ID from the URL
        phase_id = int(self.kwargs.get('pk'))
        
        # Find the requested phase
        phase = next((p for p in phases if p['id'] == phase_id), None)
        if not phase:
            # If phase not found, redirect to the company strategy page
            return redirect('strategy:dashboard')
        
        # All milestones are now loaded from session
        all_milestones = phase['milestones']
        
        context['phase'] = phase
        context['milestones'] = all_milestones
        
        # Calculate completed milestones and progress percentage
        completed_milestones = sum(1 for m in all_milestones if m.get('is_completed', False))
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
        
        # Hardcoded phase names for breadcrumbs
        phase_names = {1: 'Indie Game Development', 2: 'Arcade Machine Development', 3: 'Theme Park Attractions'}
        phase_name = phase_names.get(int(phase_id), 'Strategy Phase')
        
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
        
        # Hardcoded phases data
        phases = [
            {
                'id': 1,
                'name': 'Indie Game Development',
                'phase_type': 'indie_dev',
                'description': 'Building a foundation in game development through education and indie projects.'
            },
            {
                'id': 2,
                'name': 'Arcade Machine Development',
                'phase_type': 'arcade',
                'description': 'Expanding into physical gaming experiences through arcade machine development.'
            },
            {
                'id': 3,
                'name': 'Theme Park Attractions',
                'phase_type': 'theme_park',
                'description': 'Creating immersive physical experiences through theme park attractions.'
            }
        ]
        
        # Find the requested phase
        phase = next((p for p in phases if p['id'] == phase_id), None)
        if not phase:
            # If phase not found, redirect to the company strategy page
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
        
        # Hardcoded phases data
        phases = [
            {
                'id': 1,
                'name': 'Indie Game Development',
                'phase_type': 'indie_dev',
                'description': 'Building a foundation in game development through education and indie projects.'
            },
            {
                'id': 2,
                'name': 'Arcade Machine Development',
                'phase_type': 'arcade',
                'description': 'Expanding into physical gaming experiences through arcade machine development.'
            },
            {
                'id': 3,
                'name': 'Theme Park Attractions',
                'phase_type': 'theme_park',
                'description': 'Creating immersive physical experiences through theme park attractions.'
            }
        ]
        
        # Find the requested phase
        phase = next((p for p in phases if p['id'] == phase_id), None)
        if not phase:
            # If phase not found, redirect to the company strategy page
            return redirect('strategy:dashboard')
        
        context['phase'] = phase
        
        # Get the milestone from session storage
        milestone = None
        if 'user_milestones' in self.request.session and str(phase_id) in self.request.session['user_milestones']:
            milestone = next((m for m in self.request.session['user_milestones'][str(phase_id)] if m['id'] == milestone_id), None)
        
        if not milestone:
            # If milestone not found, redirect to the phase detail page
            return redirect('strategy:phase_detail', pk=phase_id)
        
        context['milestone'] = milestone
        context['form_action'] = reverse('strategy:milestone_update', kwargs={'phase_id': phase_id, 'milestone_id': milestone_id})
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Check if the milestone exists in session
        if 'user_milestones' not in request.session or \
           str(phase_id) not in request.session['user_milestones'] or \
           not any(m['id'] == milestone_id for m in request.session['user_milestones'][str(phase_id)]):
            messages.error(request, 'Milestone not found.')
            return redirect('strategy:phase_detail', pk=phase_id)
        
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        status = request.POST.get('status')
        is_completed = request.POST.get('is_completed') == 'on'
        
        # Validate form data
        if not title or not description or not order or not status:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('strategy:milestone_update', phase_id=phase_id, milestone_id=milestone_id)
        
        # Update the milestone in session storage
        phase_id_str = str(phase_id)
        
        # Check if we're setting this milestone to in_progress
        if status == 'in_progress':
            # Store the current milestone ID to avoid changing its status
            current_milestone_id = milestone_id
            
            # Check all phases for in-progress milestones
            for phase_key, phase_milestones in request.session['user_milestones'].items():
                for m in phase_milestones:
                    # Skip the current milestone being updated
                    if phase_key == phase_id_str and m['id'] == current_milestone_id:
                        continue
                    
                    # Change any other in-progress milestone to not started
                    if m['status'] == 'in_progress':
                        m['status'] = 'not_started'
                        messages.info(request, f"Milestone '{m['title']}' in Phase {phase_key} was changed from 'In Progress' to 'Not Started'")
        
        # Update the milestone
        for milestone in request.session['user_milestones'][phase_id_str]:
            if milestone['id'] == milestone_id:
                milestone['title'] = title
                milestone['description'] = description
                milestone['order'] = int(order)
                milestone['status'] = status
                milestone['is_completed'] = is_completed
                
                # Remove completion_date if it exists
                if 'completion_date' in milestone:
                    del milestone['completion_date']
                break
        
        request.session.modified = True
        
        # Show success message
        messages.success(request, f'Milestone "{title}" updated successfully!')
        
        # Redirect to the phase detail page
        return redirect('strategy:phase_detail', pk=phase_id)
    
    def get_breadcrumbs(self):
        # Get the phase ID and milestone ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        milestone_id = int(self.kwargs.get('milestone_id'))
        
        # Hardcoded phase names for breadcrumbs
        phase_names = {1: 'Indie Game Development', 2: 'Arcade Machine Development', 3: 'Theme Park Attractions'}
        phase_name = phase_names.get(phase_id, 'Strategy Phase')
        
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
        
        # Delete the milestone from the session
        if 'user_milestones' in request.session:
            if str(phase_id) in request.session['user_milestones']:
                request.session['user_milestones'][str(phase_id)] = [
                    m for m in request.session['user_milestones'][str(phase_id)] 
                    if m['id'] != milestone_id
                ]
                request.session.modified = True
        
        messages.success(request, 'Strategy milestone deleted successfully!')
        return redirect('strategy:phase_detail', pk=phase_id)
    
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
    def get_breadcrumbs(self):
        phase_id = int(self.kwargs.get('phase_id'))
        # Hardcoded phase names for breadcrumbs
        phase_names = {1: 'Indie Game Development', 2: 'Arcade Machine Development', 3: 'Theme Park Attractions'}
        phase_name = phase_names.get(phase_id, 'Strategy Phase')
        
        return [
            {'title': 'Strategy', 'url': reverse('strategy:dashboard')},
            {'title': phase_name, 'url': reverse('strategy:phase_detail', kwargs={'pk': phase_id})},
            {'title': 'Delete Milestone', 'url': None}
        ]


class StrategyMilestoneCreateView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """
    Create view for strategy milestones (session-based version)
    """
    template_name = 'strategy/milestone_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the phase ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        
        # Hardcoded phases data
        phases = [
            {
                'id': 1,
                'name': 'Indie Game Development',
                'phase_type': 'indie_dev',
                'description': 'Building a foundation in game development through education and indie projects.'
            },
            {
                'id': 2,
                'name': 'Arcade Machine Development',
                'phase_type': 'arcade',
                'description': 'Expanding into physical gaming experiences through arcade machine development.'
            },
            {
                'id': 3,
                'name': 'Theme Park Attractions',
                'phase_type': 'theme_park',
                'description': 'Creating immersive physical experiences through theme park attractions.'
            }
        ]
        
        # Find the requested phase
        phase = next((p for p in phases if p['id'] == phase_id), None)
        if not phase:
            # If phase not found, redirect to the company strategy page
            return redirect('strategy:dashboard')
        
        context['phase'] = phase
        context['form_action'] = reverse('strategy:milestone_create', kwargs={'phase_id': phase_id})
        context['is_update'] = False
        
        return context
    
    def post(self, request, *args, **kwargs):
        # Get the phase ID from the URL
        phase_id = int(self.kwargs.get('phase_id'))
        
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        status = request.POST.get('status')
        is_completed = request.POST.get('is_completed') == 'on'
        
        # Validate form data
        if not title or not description or not order or not status:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('strategy:milestone_create', phase_id=phase_id)
        
        # Initialize session storage for user milestones if needed
        if 'user_milestones' not in request.session:
            request.session['user_milestones'] = {}
            
        # Initialize phase milestones if needed
        phase_id_str = str(phase_id)
        if phase_id_str not in request.session['user_milestones']:
            request.session['user_milestones'][phase_id_str] = []
            
        # Generate a new milestone ID
        existing_milestones = request.session['user_milestones'][phase_id_str]
        new_id = 1
        if existing_milestones:
            new_id = max(m['id'] for m in existing_milestones) + 1
        
        # Check if another milestone is already in progress across all phases
        if status == 'in_progress':
            # Check all phases for in-progress milestones
            for phase_key, phase_milestones in request.session['user_milestones'].items():
                for milestone in phase_milestones:
                    if milestone['status'] == 'in_progress':
                        milestone['status'] = 'not_started'
                        messages.info(request, f"Milestone '{milestone['title']}' in Phase {phase_key} was changed from 'In Progress' to 'Not Started'")
        
        # Create a new milestone and add it to the session
        new_milestone = {
            'id': new_id,
            'title': title,
            'description': description,
            'order': int(order),
            'status': status,
            'is_completed': is_completed
        }
            
        request.session['user_milestones'][phase_id_str].append(new_milestone)
        request.session.modified = True
        
        messages.success(request, f'Milestone "{title}" created successfully!')
        
        # Redirect to the phase detail page
        return redirect('strategy:phase_detail', pk=phase_id)
    
    def get_breadcrumbs(self):
        # Get the phase ID from the URL
        phase_id = self.kwargs.get('phase_id')
        
        # Hardcoded phase names for breadcrumbs
        phase_names = {1: 'Indie Game Development', 2: 'Arcade Machine Development', 3: 'Theme Park Attractions'}
        phase_name = phase_names.get(int(phase_id), 'Strategy Phase')
        
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
