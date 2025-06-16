from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class ArcadeDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Arcade Entertainment department"""
    template_name = 'arcade/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class ArcadeProjectsView(LoginRequiredMixin, TemplateView):
    """View for managing arcade projects"""
    template_name = 'arcade/projects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class LocationsView(LoginRequiredMixin, TemplateView):
    """View for managing arcade locations"""
    template_name = 'arcade/locations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class RevenueView(LoginRequiredMixin, TemplateView):
    """View for arcade revenue tracking"""
    template_name = 'arcade/revenue.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context


class ArcadeTasksView(LoginRequiredMixin, TemplateView):
    """View for arcade department tasks"""
    template_name = 'arcade/tasks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'arcade'
        return context
