from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class EducationDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Education department"""
    template_name = 'education/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class ClassesView(LoginRequiredMixin, TemplateView):
    """View for managing education classes"""
    template_name = 'education/classes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class CourseMaterialsView(LoginRequiredMixin, TemplateView):
    """View for managing course materials"""
    template_name = 'education/materials.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class ScheduleView(LoginRequiredMixin, TemplateView):
    """View for class schedules"""
    template_name = 'education/schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context


class EducationTasksView(LoginRequiredMixin, TemplateView):
    """View for education department tasks"""
    template_name = 'education/tasks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'education'
        return context
