"""
Views for Epic management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from .task_models import Epic
from .epic_forms import EpicForm


class EpicListView(LoginRequiredMixin, ListView):
    """
    List all epics with filtering by company section and status
    """
    model = Epic
    template_name = 'projects/epic_list.html'
    context_object_name = 'epics'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Epic.objects.all()
        
        # Filter by company section
        section = self.request.GET.get('section')
        if section:
            queryset = queryset.filter(company_section=section)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset.order_by('-priority', 'target_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_sections'] = Epic.COMPANY_SECTION_CHOICES
        context['statuses'] = Epic.STATUS_CHOICES
        context['current_section'] = self.request.GET.get('section', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Stats
        context['total_epics'] = Epic.objects.count()
        context['in_progress_count'] = Epic.objects.filter(status='in_progress').count()
        context['completed_count'] = Epic.objects.filter(status='completed').count()
        
        return context


class EpicCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new epic
    """
    model = Epic
    form_class = EpicForm
    template_name = 'projects/epic_form.html'
    
    def form_valid(self, form):
        # Set created_by_name from session
        current_user_name = self.request.session.get('current_user_name', '')
        if current_user_name:
            form.instance.created_by_name = current_user_name
        
        messages.success(self.request, f"Epic '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:epic_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class EpicUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing epic
    """
    model = Epic
    form_class = EpicForm
    template_name = 'projects/epic_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f"Epic '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:epic_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


class EpicDetailView(LoginRequiredMixin, DetailView):
    """
    View epic details with all associated tasks
    """
    model = Epic
    template_name = 'projects/epic_detail.html'
    context_object_name = 'epic'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        epic = self.object
        
        # Get all tasks for this epic
        tasks = epic.get_all_tasks()
        
        # Organize tasks by status
        context['tasks_by_status'] = {
            'backlog': [t for t in tasks if t.status == 'backlog'],
            'to_do': [t for t in tasks if t.status == 'to_do'],
            'in_progress': [t for t in tasks if t.status == 'in_progress'],
            'in_review': [t for t in tasks if t.status == 'in_review'],
            'done': [t for t in tasks if t.status == 'done'],
            'blocked': [t for t in tasks if t.status == 'blocked'],
        }
        
        # Stats
        context['total_tasks'] = len(tasks)
        context['completed_tasks'] = len([t for t in tasks if t.status == 'done'])
        context['progress_percentage'] = epic.get_progress()
        context['subtask_count'] = epic.get_subtask_count()
        
        return context


class EpicDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete an epic
    """
    model = Epic
    template_name = 'projects/epic_confirm_delete.html'
    success_url = reverse_lazy('projects:epic_list')
    
    def delete(self, request, *args, **kwargs):
        epic = self.get_object()
        messages.success(request, f"Epic '{epic.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)
