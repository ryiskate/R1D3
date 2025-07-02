from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages

from core.mixins import BreadcrumbMixin

from .models import Vision, Goal, Objective, KeyResult
from .forms import VisionForm, GoalForm, ObjectiveForm, KeyResultForm


class StrategyDashboardView(BreadcrumbMixin, LoginRequiredMixin, ListView):
    """
    Dashboard view for strategy section
    """
    model = Vision
    template_name = 'strategy/dashboard.html'
    context_object_name = 'visions'
    
    def get_breadcrumbs(self):
        return [
            {'title': 'Strategy', 'url': None}
        ]
    
    def get_queryset(self):
        return Vision.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_goals'] = Goal.objects.filter(is_completed=False)
        context['active_objectives'] = Objective.objects.filter(is_completed=False)
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
