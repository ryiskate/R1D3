"""
Unified task form views for R1D3 tasks.
This module provides specialized task form views for R1D3 tasks
that use the unified task form templates.
"""
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from .task_models import R1D3Task
from .task_forms import R1D3TaskForm


class UnifiedR1D3TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new R1D3 task using the unified task form template.
    """
    model = R1D3Task
    form_class = R1D3TaskForm
    template_name = 'projects/r1d3_task_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f"R1D3 Task '{form.instance.title}' created successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:r1d3_task_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = "R1D3 Task"
        context['is_create'] = True
        return context


class UnifiedR1D3TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing R1D3 task using the unified task form template.
    """
    model = R1D3Task
    form_class = R1D3TaskForm
    template_name = 'projects/r1d3_task_form.html'
    
    def test_func(self):
        # Only allow the task creator or assigned user to update it
        task = self.get_object()
        return self.request.user == task.created_by or self.request.user == task.assigned_to
    
    def form_valid(self, form):
        messages.success(self.request, f"R1D3 Task '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:r1d3_task_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section_name'] = "R1D3 Task"
        context['is_create'] = False
        return context
