from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from .game_models import GameProject, GameDesignDocument, GameTask
from .gdd_utils import extract_features_from_html, create_sections_and_features, convert_feature_to_task
from .gdd_upload_form import GDDUploadForm

class GDDUploadView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for uploading a GDD HTML file and creating tasks from it
    """
    def test_func(self):
        game_id = self.kwargs.get('pk')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('pk')
        game = get_object_or_404(GameProject, id=game_id)
        form = GDDUploadForm()
        
        # Check if a GDD already exists
        try:
            gdd = GameDesignDocument.objects.get(game=game)
            has_gdd = True
        except GameDesignDocument.DoesNotExist:
            has_gdd = False
        
        return render(request, 'projects/gdd_upload.html', {
            'form': form,
            'game': game,
            'has_gdd': has_gdd
        })
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('pk')
        game = get_object_or_404(GameProject, id=game_id)
        form = GDDUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            gdd_file = request.FILES['gdd_file']
            auto_create_tasks = form.cleaned_data.get('auto_create_tasks', False)
            update_existing = form.cleaned_data.get('update_existing', False)
            
            # Read the HTML content
            html_content = gdd_file.read().decode('utf-8')
            
            # Check if a GDD already exists
            try:
                gdd = GameDesignDocument.objects.get(game=game)
                if update_existing:
                    # Update existing GDD
                    gdd.html_content = html_content
                    gdd.use_html_content = True
                    gdd.save()
                    messages.success(request, "GDD updated successfully!")
                else:
                    messages.error(request, "A GDD already exists for this game. Check 'Update existing' to replace it.")
                    return render(request, 'projects/gdd_upload.html', {
                        'form': form,
                        'game': game,
                        'has_gdd': True
                    })
            except GameDesignDocument.DoesNotExist:
                # Create new GDD
                gdd = GameDesignDocument.objects.create(
                    game=game,
                    html_content=html_content,
                    use_html_content=True,
                    high_concept="Imported from HTML file",
                    player_experience="Imported from HTML file"
                )
                messages.success(request, "GDD created successfully!")
            
            # Extract features and create sections
            with transaction.atomic():
                sections, features = create_sections_and_features(gdd, html_content)
                
                # Create tasks for features if requested
                if auto_create_tasks:
                    tasks_created = 0
                    existing_tasks = 0
                    
                    # Get all existing task titles for this game
                    existing_task_titles = set(GameTask.objects.filter(game=game).values_list('title', flat=True))
                    
                    for feature in features:
                        # Only create a task if a task with the same name doesn't exist
                        if feature.feature_name not in existing_task_titles:
                            convert_feature_to_task(feature, game)
                            tasks_created += 1
                        else:
                            existing_tasks += 1
                    
                    if tasks_created > 0:
                        messages.success(request, f"Created {tasks_created} new tasks from GDD features.")
                    if existing_tasks > 0:
                        messages.info(request, f"Skipped {existing_tasks} features that already have matching tasks.")
            
            return redirect('games:gdd_detail', pk=game.id)
        
        return render(request, 'projects/gdd_upload.html', {
            'form': form,
            'game': game
        })
