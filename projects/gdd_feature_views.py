from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db import transaction

from .game_models import GameProject, GameDesignDocument, GDDSection, GDDFeature, GameTask
from .gdd_utils import extract_features_from_html, create_sections_and_features, convert_feature_to_task, update_gdd_html_with_task_status

class ExtractFeaturesView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Extract features from a GDD's HTML content and create GDDFeature objects
    """
    def test_func(self):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        
        if not gdd.html_content:
            messages.error(request, "This GDD doesn't have HTML content to extract features from.")
            return redirect('games:gdd_detail', pk=gdd.game.id)
        
        # Extract features from HTML
        with transaction.atomic():
            sections, features = create_sections_and_features(gdd, gdd.html_content)
        
        messages.success(request, f"Successfully extracted {len(features)} features from {len(sections)} sections.")
        return redirect('games:gdd_detail', pk=gdd.game.id)


class GDDFeaturesListView(LoginRequiredMixin, ListView):
    """
    List all features extracted from a GDD
    """
    model = GDDFeature
    template_name = 'projects/gdd_features_list.html'
    context_object_name = 'features'
    
    def get_queryset(self):
        gdd_id = self.kwargs.get('pk')
        self.gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        return GDDFeature.objects.filter(section__gdd=self.gdd).select_related('section', 'task')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gdd'] = self.gdd
        context['game'] = self.gdd.game
        context['sections'] = GDDSection.objects.filter(gdd=self.gdd)
        return context


class ConvertFeatureToTaskView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Convert a GDD feature to a game task
    """
    def test_func(self):
        feature_id = self.kwargs.get('pk')
        feature = get_object_or_404(GDDFeature, id=feature_id)
        game = feature.section.gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def post(self, request, *args, **kwargs):
        feature_id = self.kwargs.get('pk')
        feature = get_object_or_404(GDDFeature, id=feature_id)
        
        if feature.task:
            messages.info(request, f"Feature '{feature.feature_name}' is already linked to task #{feature.task.id}.")
        else:
            game = feature.section.gdd.game
            task = convert_feature_to_task(feature, game)
            messages.success(request, f"Feature '{feature.feature_name}' converted to task #{task.id}.")
        
        return redirect('games:gdd_features', pk=feature.section.gdd.id)


class ConvertAllFeaturesToTasksView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Convert all GDD features to game tasks
    """
    def test_func(self):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def post(self, request, *args, **kwargs):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        
        features = GDDFeature.objects.filter(section__gdd=gdd, task__isnull=True)
        tasks_created = 0
        
        with transaction.atomic():
            for feature in features:
                convert_feature_to_task(feature, game)
                tasks_created += 1
        
        messages.success(request, f"Successfully converted {tasks_created} features to tasks.")
        return redirect('games:gdd_features', pk=gdd_id)


class UpdateGDDWithTaskStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Update the GDD HTML content with current task statuses
    """
    def test_func(self):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def post(self, request, *args, **kwargs):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        
        update_gdd_html_with_task_status(gdd)
        messages.success(request, "GDD updated with current task statuses.")
        
        return redirect('games:gdd_detail', pk=gdd.game.id)


@require_POST
def task_status_update_callback(request, task_id):
    """
    Callback for when a task status is updated
    Updates the linked GDD feature if it exists
    """
    task = get_object_or_404(GameTask, id=task_id)
    
    try:
        feature = task.gdd_feature
        gdd = feature.section.gdd
        update_gdd_html_with_task_status(gdd)
        return JsonResponse({'success': True, 'message': 'GDD updated with task status'})
    except GDDFeature.DoesNotExist:
        return JsonResponse({'success': True, 'message': 'No linked GDD feature found'})
