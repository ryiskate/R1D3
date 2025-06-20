from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, Count

from .models import Project, Milestone, Task, Risk
from .forms import ProjectForm, MilestoneForm, TaskForm, RiskForm


class ProjectDashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard view for projects section
    """
    model = Project
    template_name = 'projects/dashboard.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        # Show active projects by default
        return Project.objects.filter(status='active')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_projects'] = Project.objects.count()
        context['active_projects'] = Project.objects.filter(status='active').count()
        context['completed_projects'] = Project.objects.filter(status='completed').count()
        context['my_tasks'] = Task.objects.filter(assigned_to=self.request.user, status__in=['to_do', 'in_progress'])
        context['overdue_tasks'] = Task.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['to_do', 'in_progress']
        )
        return context


class ProjectListView(LoginRequiredMixin, ListView):
    """
    List all projects
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        queryset = Project.objects.all()
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by search query if provided
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(manager__username__icontains=query)
            )
            
        return queryset


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a specific project
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Get project milestones
        context['milestones'] = project.milestones.all().order_by('due_date')
        
        # Get project tasks
        context['tasks'] = project.tasks.all().order_by('-priority', 'due_date')
        context['tasks_by_status'] = {
            'to_do': project.tasks.filter(status='to_do').count(),
            'in_progress': project.tasks.filter(status='in_progress').count(),
            'in_review': project.tasks.filter(status='in_review').count(),
            'done': project.tasks.filter(status='done').count(),
            'blocked': project.tasks.filter(status='blocked').count(),
        }
        
        # Get project risks
        context['risks'] = project.risks.all().order_by('-risk_score')
        
        return context


class ProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a new project
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')
    
    def test_func(self):
        # Only allow staff or managers to create projects
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, "Project created successfully!")
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing project
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    
    def test_func(self):
        # Only allow staff or project manager to update
        project = self.get_object()
        return self.request.user.is_staff or self.request.user == project.manager
    
    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Project updated successfully!")
        return super().form_valid(form)


class TaskListView(LoginRequiredMixin, ListView):
    """
    List all tasks or tasks filtered by project using the modern task dashboard template
    """
    model = Task
    template_name = 'projects/task_dashboard.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = Task.objects.all()
        
        # Filter by project if provided
        project_id = self.kwargs.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        # Filter by assigned user if requested
        if self.request.GET.get('my_tasks'):
            queryset = queryset.filter(assigned_to=self.request.user)
            
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-priority', 'due_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add project to context if filtering by project
        project_id = self.kwargs.get('project_id')
        if project_id:
            context['project'] = get_object_or_404(Project, pk=project_id)
            
        # Add task statistics for the dashboard
        tasks = self.get_queryset()
        context['task_stats'] = {
            'total': tasks.count(),
            'to_do': tasks.filter(status='to_do').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'in_review': tasks.filter(status='in_review').count(),
            'done': tasks.filter(status='done').count(),
            'blocked': tasks.filter(status='blocked').count(),
        }
            
        return context
