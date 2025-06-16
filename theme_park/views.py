from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class ThemeParkDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Theme Park department"""
    template_name = 'theme_park/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class ParkProjectsView(LoginRequiredMixin, TemplateView):
    """View for managing theme park projects"""
    template_name = 'theme_park/projects.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class AttractionsView(LoginRequiredMixin, TemplateView):
    """View for managing theme park attractions"""
    template_name = 'theme_park/attractions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class ParkMapView(LoginRequiredMixin, TemplateView):
    """View for theme park map"""
    template_name = 'theme_park/map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context


class ThemeParkTasksView(LoginRequiredMixin, TemplateView):
    """View for theme park department tasks"""
    template_name = 'theme_park/tasks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'theme_park'
        return context
