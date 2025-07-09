from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
import json
from datetime import date, datetime, timedelta

from core.mixins import BreadcrumbMixin

from .models import IndieNewsTask, IndieGame, IndieEvent, IndieTool
from .forms import IndieNewsTaskForm, IndieGameForm, IndieEventForm, IndieToolForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Task Views
class IndieNewsTaskListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    Display a list of indie news tasks
    """
    model = IndieNewsTask
    template_name = 'indie_news/task_list.html'
    context_object_name = 'tasks'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tasks', 'url': None}
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by assigned user if provided
        assigned_to = self.request.GET.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)
        
        # Filter by news type if provided
        news_type = self.request.GET.get('news_type')
        if news_type:
            queryset = queryset.filter(news_type=news_type)
            
        # Search by title or description
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(game_title__icontains=search_query) |
                Q(developer__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add status counts
        queryset = self.get_queryset()
        status_counts = {}
        for status_code, status_name in self.model.STATUS_CHOICES:
            status_counts[status_code] = queryset.filter(status=status_code).count()
        context['status_counts'] = status_counts
        context['today'] = date.today()
        
        # Add users for filtering
        context['users'] = User.objects.all()
        
        # Add news types for filtering
        context['news_types'] = [choice[0] for choice in IndieNewsTask._meta.get_field('news_type').choices]
        
        # Add batch update URL
        context['batch_update_url'] = reverse('indie_news:task_batch_update')
        
        return context


class IndieNewsTaskCreateView(BreadcrumbMixin, LoginRequiredMixin, CreateView):
    """
    Create a new indie news task
    """
    model = IndieNewsTask
    form_class = IndieNewsTaskForm
    template_name = 'indie_news/task_form.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tasks', 'url': reverse('indie_news:task_list')},
            {'title': 'New Task', 'url': None}
        ]
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Indie news task created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:task_list')


class IndieNewsTaskDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """
    View details of an indie news task
    """
    model = IndieNewsTask
    template_name = 'indie_news/task_detail.html'
    context_object_name = 'task'
    
    def get_breadcrumbs(self):
        task = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tasks', 'url': reverse('indie_news:task_list')},
            {'title': task.title, 'url': None}
        ]


class IndieNewsTaskUpdateView(BreadcrumbMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing indie news task
    """
    model = IndieNewsTask
    form_class = IndieNewsTaskForm
    template_name = 'indie_news/task_form.html'
    
    def get_breadcrumbs(self):
        task = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tasks', 'url': reverse('indie_news:task_list')},
            {'title': task.title, 'url': reverse('indie_news:task_detail', kwargs={'pk': task.pk})},
            {'title': 'Edit', 'url': None}
        ]
    
    def test_func(self):
        task = self.get_object()
        # Allow task creator, assigned user, or admin to edit
        return (self.request.user == task.created_by or 
                self.request.user == task.assigned_to or 
                self.request.user.is_staff)
    
    def form_valid(self, form):
        messages.success(self.request, 'Indie news task updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:task_detail', kwargs={'pk': self.object.pk})


class IndieNewsTaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an indie news task
    """
    model = IndieNewsTask
    template_name = 'indie_news/task_confirm_delete.html'
    context_object_name = 'task'  # Explicitly set the context object name
    success_url = reverse_lazy('indie_news:task_list')
    
    def test_func(self):
        task = self.get_object()
        # Only allow task creator or admin to delete
        return self.request.user == task.created_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_title = task.title  # Store the title before deletion
        messages.success(request, f'Indie news task "{task_title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'indie_news'
        return context


class IndieNewsTaskBatchUpdateView(LoginRequiredMixin, View):
    """
    Update multiple indie news tasks at once via AJAX
    """
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            task_ids = data.get('task_ids', [])
            if not task_ids:
                return JsonResponse({'status': 'error', 'message': 'No tasks selected'}, status=400)
            
            fields_to_update = {}
            if data.get('status'):
                fields_to_update['status'] = data['status']
            if data.get('priority'):
                fields_to_update['priority'] = data['priority']
            if data.get('assigned_to'):
                try:
                    user = User.objects.get(id=data['assigned_to'])
                    fields_to_update['assigned_to'] = user
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)
            if data.get('due_date'):
                fields_to_update['due_date'] = data['due_date']
            if data.get('news_type'):
                fields_to_update['news_type'] = data['news_type']
                
            if not fields_to_update:
                return JsonResponse({'status': 'error', 'message': 'No fields to update'}, status=400)
                
            updated_count = IndieNewsTask.objects.filter(id__in=task_ids).update(**fields_to_update)
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Successfully updated {updated_count} tasks',
                'updated_count': updated_count
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Indie Game Views
class IndieGameListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    Display a list of indie games
    """
    model = IndieGame
    template_name = 'indie_news/game_list.html'
    context_object_name = 'games'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Games', 'url': None}
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by platform if provided
        platform = self.request.GET.get('platform')
        if platform:
            queryset = queryset.filter(platforms__icontains=platform)
        
        # Filter by genre if provided
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genres__icontains=genre)
            
        # Search by title or developer
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(developer__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platforms'] = [choice[0] for choice in IndieGame.PLATFORM_CHOICES]
        context['genres'] = [choice[0] for choice in IndieGame.GENRE_CHOICES]
        return context


class IndieGameCreateView(BreadcrumbMixin, LoginRequiredMixin, CreateView):
    """
    Create a new indie game
    """
    model = IndieGame
    form_class = IndieGameForm
    template_name = 'indie_news/game_form.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Games', 'url': reverse('indie_news:game_list')},
            {'title': 'New Game', 'url': None}
        ]
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, 'Indie game added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:game_list')


class IndieGameDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """
    View details of an indie game
    """
    model = IndieGame
    template_name = 'indie_news/game_detail.html'
    context_object_name = 'game'
    
    def get_breadcrumbs(self):
        game = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Games', 'url': reverse('indie_news:game_list')},
            {'title': game.title, 'url': None}
        ]


class IndieGameUpdateView(BreadcrumbMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing indie game
    """
    model = IndieGame
    form_class = IndieGameForm
    template_name = 'indie_news/game_form.html'
    
    def get_breadcrumbs(self):
        game = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Games', 'url': reverse('indie_news:game_list')},
            {'title': game.title, 'url': reverse('indie_news:game_detail', kwargs={'pk': game.pk})},
            {'title': 'Edit', 'url': None}
        ]
    
    def test_func(self):
        game = self.get_object()
        # Allow creator or admin to edit
        return self.request.user == game.added_by or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Indie game updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:game_detail', kwargs={'pk': self.object.pk})


class IndieGameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an indie game
    """
    model = IndieGame
    template_name = 'indie_news/game_confirm_delete.html'
    success_url = reverse_lazy('indie_news:game_list')
    
    def test_func(self):
        game = self.get_object()
        # Only allow creator or admin to delete
        return self.request.user == game.added_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Indie game deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Event Views
class IndieEventListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    Display a list of indie events
    """
    model = IndieEvent
    template_name = 'indie_news/event_list.html'
    context_object_name = 'events'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Events', 'url': None}
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by event type if provided
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by virtual/in-person if provided
        is_virtual = self.request.GET.get('is_virtual')
        if is_virtual is not None:
            is_virtual_bool = is_virtual.lower() == 'true'
            queryset = queryset.filter(is_virtual=is_virtual_bool)
            
        # Search by name or location
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(location__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = [choice[0] for choice in IndieEvent.EVENT_TYPE_CHOICES]
        context['today'] = date.today()
        return context


class IndieEventCreateView(BreadcrumbMixin, LoginRequiredMixin, CreateView):
    """
    Create a new indie event
    """
    model = IndieEvent
    form_class = IndieEventForm
    template_name = 'indie_news/event_form.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Events', 'url': reverse('indie_news:event_list')},
            {'title': 'New Event', 'url': None}
        ]
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, 'Indie event added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:event_list')


class IndieEventDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """
    View details of an indie event
    """
    model = IndieEvent
    template_name = 'indie_news/event_detail.html'
    context_object_name = 'event'
    
    def get_breadcrumbs(self):
        event = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Events', 'url': reverse('indie_news:event_list')},
            {'title': event.name, 'url': None}
        ]


class IndieEventUpdateView(BreadcrumbMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing indie event
    """
    model = IndieEvent
    form_class = IndieEventForm
    template_name = 'indie_news/event_form.html'
    
    def get_breadcrumbs(self):
        event = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Events', 'url': reverse('indie_news:event_list')},
            {'title': event.name, 'url': reverse('indie_news:event_detail', kwargs={'pk': event.pk})},
            {'title': 'Edit', 'url': None}
        ]
    
    def test_func(self):
        event = self.get_object()
        # Allow creator or admin to edit
        return self.request.user == event.added_by or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Indie event updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:event_detail', kwargs={'pk': self.object.pk})


class IndieEventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an indie event
    """
    model = IndieEvent
    template_name = 'indie_news/event_confirm_delete.html'
    success_url = reverse_lazy('indie_news:event_list')
    
    def test_func(self):
        event = self.get_object()
        # Only allow creator or admin to delete
        return self.request.user == event.added_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Indie event deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Tool Views
class IndieToolListView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    Display a list of indie development tools
    """
    model = IndieTool
    template_name = 'indie_news/tool_list.html'
    context_object_name = 'tools'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tools', 'url': None}
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by tool type if provided
        tool_type = self.request.GET.get('tool_type')
        if tool_type:
            queryset = queryset.filter(tool_type=tool_type)
        
        # Filter by pricing model if provided
        pricing_model = self.request.GET.get('pricing_model')
        if pricing_model:
            queryset = queryset.filter(pricing_model=pricing_model)
            
        # Search by name or description
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tool_types'] = [choice[0] for choice in IndieTool.TOOL_TYPE_CHOICES]
        context['pricing_models'] = [choice[0] for choice in IndieTool.PRICING_MODEL_CHOICES]
        return context


class IndieToolCreateView(BreadcrumbMixin, LoginRequiredMixin, CreateView):
    """
    Create a new indie development tool
    """
    model = IndieTool
    form_class = IndieToolForm
    template_name = 'indie_news/tool_form.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tools', 'url': reverse('indie_news:tool_list')},
            {'title': 'New Tool', 'url': None}
        ]
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, 'Indie tool added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:tool_list')


class IndieToolDetailView(BreadcrumbMixin, LoginRequiredMixin, DetailView):
    """
    View details of an indie development tool
    """
    model = IndieTool
    template_name = 'indie_news/tool_detail.html'
    context_object_name = 'tool'
    
    def get_breadcrumbs(self):
        tool = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tools', 'url': reverse('indie_news:tool_list')},
            {'title': tool.name, 'url': None}
        ]


class IndieToolUpdateView(BreadcrumbMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing indie development tool
    """
    model = IndieTool
    form_class = IndieToolForm
    template_name = 'indie_news/tool_form.html'
    
    def get_breadcrumbs(self):
        tool = self.get_object()
        return [
            {'title': 'Indie News', 'url': reverse('indie_news:dashboard')},
            {'title': 'Tools', 'url': reverse('indie_news:tool_list')},
            {'title': tool.name, 'url': reverse('indie_news:tool_detail', kwargs={'pk': tool.pk})},
            {'title': 'Edit', 'url': None}
        ]
    
    def test_func(self):
        tool = self.get_object()
        # Allow creator or admin to edit
        return self.request.user == tool.added_by or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, 'Indie tool updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('indie_news:tool_detail', kwargs={'pk': self.object.pk})


class IndieToolDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete an indie development tool
    """
    model = IndieTool
    template_name = 'indie_news/tool_confirm_delete.html'
    success_url = reverse_lazy('indie_news:tool_list')
    
    def test_func(self):
        tool = self.get_object()
        # Only staff members can delete tools
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Tool deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Dashboard View
class IndieNewsDashboardView(BreadcrumbMixin, LoginRequiredMixin, TemplateView):
    """
    Dashboard for the Indie News section showing stats and recent items
    """
    template_name = 'indie_news/dashboard.html'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Indie News', 'url': None}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts for stats cards
        context['task_count'] = IndieNewsTask.objects.count()
        context['game_count'] = IndieGame.objects.count()
        context['event_count'] = IndieEvent.objects.count()
        context['tool_count'] = IndieTool.objects.count()
        
        # Get task status counts for chart
        status_counts = IndieNewsTask.objects.values('status').annotate(count=Count('status'))
        context['status_counts'] = {
            'backlog': next((item['count'] for item in status_counts if item['status'] == 'backlog'), 0),
            'to_do': next((item['count'] for item in status_counts if item['status'] == 'to_do'), 0),
            'in_progress': next((item['count'] for item in status_counts if item['status'] == 'in_progress'), 0),
            'in_review': next((item['count'] for item in status_counts if item['status'] == 'in_review'), 0),
            'done': next((item['count'] for item in status_counts if item['status'] == 'done'), 0),
            'blocked': next((item['count'] for item in status_counts if item['status'] == 'blocked'), 0),
        }
        
        # Get news type counts for chart
        news_type_counts = IndieNewsTask.objects.values('news_type').annotate(count=Count('news_type'))
        context['news_type_counts'] = {
            'review': next((item['count'] for item in news_type_counts if item['news_type'] == 'review'), 0),
            'preview': next((item['count'] for item in news_type_counts if item['news_type'] == 'preview'), 0),
            'interview': next((item['count'] for item in news_type_counts if item['news_type'] == 'interview'), 0),
            'feature': next((item['count'] for item in news_type_counts if item['news_type'] == 'feature'), 0),
            'news': next((item['count'] for item in news_type_counts if item['news_type'] == 'news'), 0),
            'opinion': next((item['count'] for item in news_type_counts if item['news_type'] == 'opinion'), 0),
            'guide': next((item['count'] for item in news_type_counts if item['news_type'] == 'guide'), 0),
        }
        
        # Get recent tasks assigned to the current user
        context['recent_tasks'] = IndieNewsTask.objects.filter(assigned_to=self.request.user).order_by('-updated_at')[:5]
        
        # Also add the full list of user's tasks for the dashboard table
        context['user_indie_news_tasks'] = IndieNewsTask.objects.filter(assigned_to=self.request.user).order_by('-due_date')
        
        # Get recent games
        context['recent_games'] = IndieGame.objects.all().order_by('-added_on')[:4]
        
        # Get upcoming events (events starting from today)
        today = date.today()
        context['upcoming_events'] = IndieEvent.objects.filter(
            start_date__gte=today
        ).order_by('start_date')[:5]
        
        # Get recent tools
        context['recent_tools'] = IndieTool.objects.all().order_by('-added_on')[:5]
        
        return context
