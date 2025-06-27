from django.shortcuts import render, get_object_or_404
from django.views.generic import View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.urls import reverse
from .task_models import GameDevelopmentTask
from .task_forms import GameDevelopmentTaskForm
from .game_models import GameTask, GameMilestone  # Keep for backwards compatibility during transition
from .forms import GameTaskForm  # Keep for backwards compatibility during transition
import json

class GameTaskStatusUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update game development task status via AJAX
    """
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    template_name = 'projects/game_task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = getattr(self.object, 'game', None)
        return context
    
    def get_success_url(self):
        return JsonResponse({'status': 'success'})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(self.object, 'game') and self.object.game:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.status = self.request.POST.get('status')
        form.save()
        return self.get_success_url()
    
    def form_invalid(self, form):
        return JsonResponse({
            'status': 'error', 
            'errors': form.errors.as_json()
        }, status=400)


class GameTaskHoursUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update game development task actual hours via AJAX
    """
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    template_name = 'projects/game_task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = getattr(self.object, 'game', None)
        return context
    
    def get_success_url(self):
        return JsonResponse({'status': 'success'})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(self.object, 'game') and self.object.game:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.actual_hours = self.request.POST.get('actual_hours')
        form.save()
        return self.get_success_url()
    
    def form_invalid(self, form):
        return JsonResponse({
            'status': 'error', 
            'errors': form.errors.as_json()
        }, status=400)


class GameTaskBatchUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update multiple game development tasks at once via AJAX
    """
    model = GameDevelopmentTask
    form_class = GameDevelopmentTaskForm
    template_name = 'projects/game_task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = getattr(self.object, 'game', None)
        return context
    
    def get_success_url(self):
        return JsonResponse({'status': 'success'})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(self.object, 'game') and self.object.game:
            form.fields['milestone'].queryset = GameMilestone.objects.filter(game=self.object.game)
        return form
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        task_ids = json.loads(self.request.POST.get('task_ids'))
        status = self.request.POST.get('status')
        
        GameDevelopmentTask.objects.filter(id__in=task_ids).update(status=status)
        return self.get_success_url()
    
    def form_invalid(self, form):
        return JsonResponse({
            'status': 'error', 
            'errors': form.errors.as_json()
        }, status=400)
