from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class SocialMediaDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the Social Media department"""
    template_name = 'social_media/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class PostScheduleView(LoginRequiredMixin, TemplateView):
    """View for managing post schedules"""
    template_name = 'social_media/schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class PostIdeasView(LoginRequiredMixin, TemplateView):
    """View for managing post ideas"""
    template_name = 'social_media/ideas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class AnalyticsView(LoginRequiredMixin, TemplateView):
    """View for social media analytics"""
    template_name = 'social_media/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context


class SocialMediaTasksView(LoginRequiredMixin, TemplateView):
    """View for social media department tasks"""
    template_name = 'social_media/tasks.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_department'] = 'social_media'
        return context
