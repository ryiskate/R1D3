from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
import json

from .game_models import GameProject, GameDesignDocument, GDDSection, GameTask
from .game_forms import GameDesignDocumentForm


class GameDesignDocumentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit a game design document with HTML content support
    """
    model = GameDesignDocument
    form_class = GameDesignDocumentForm
    template_name = 'projects/gdd_form.html'
    
    def get_object(self, queryset=None):
        # Override get_object to add debugging and ensure game relationship
        obj = super().get_object(queryset)
        # Make sure we have a valid game relationship
        if not obj.game:
            # Try to find the game from the URL if possible
            game_id = self.kwargs.get('game_id')
            if game_id:
                from .game_models import GameProject
                try:
                    game = GameProject.objects.get(id=game_id)
                    obj.game = game
                    obj.save()
                except GameProject.DoesNotExist:
                    pass
        return obj
    
    def test_func(self):
        # Only allow staff or game leads to edit GDDs
        gdd = self.get_object()
        game = gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def form_valid(self, form):
        # Handle the main GDD form
        gdd = form.save(commit=False)
        
        # Handle HTML content mode
        use_html_content = self.request.POST.get('use_html_content') == 'on'
        gdd.use_html_content = use_html_content
        
        if use_html_content:
            gdd.html_content = self.request.POST.get('html_content', '')
            
            # Process sections data
            sections_data = self.request.POST.get('sections_data', '[]')
            try:
                sections_data = json.loads(sections_data)
            except json.JSONDecodeError:
                sections_data = []
            
            # Update or create sections
            existing_section_ids = []
            for section_data in sections_data:
                section_id = section_data.get('id', '')
                
                if section_id.startswith('new_'):
                    # Create new section
                    section = GDDSection(
                        gdd=gdd,
                        title=section_data.get('title', ''),
                        section_id=section_data.get('section_id', ''),
                        html_content=section_data.get('html_content', ''),
                        order=len(existing_section_ids)
                    )
                    section.save()
                    existing_section_ids.append(section.id)
                else:
                    # Update existing section
                    try:
                        section = GDDSection.objects.get(id=section_id, gdd=gdd)
                        section.title = section_data.get('title', '')
                        section.section_id = section_data.get('section_id', '')
                        section.html_content = section_data.get('html_content', '')
                        section.order = len(existing_section_ids)
                        section.save()
                        existing_section_ids.append(section.id)
                    except GDDSection.DoesNotExist:
                        pass
            
            # Delete sections that were removed
            GDDSection.objects.filter(gdd=gdd).exclude(id__in=existing_section_ids).delete()
        
        gdd.save()
        messages.success(self.request, "Game Design Document updated successfully!")
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        # Add robust error handling for game ID
        if self.object and self.object.game and self.object.game.id:
            # Redirect to the game detail page using the game's ID
            return reverse('games:game_detail', kwargs={'pk': self.object.game.id})
        else:
            # Fallback to the games list if we can't get the game ID
            return reverse('games:game_list')


class TaskGDDSectionLinkView(LoginRequiredMixin, View):
    """
    Link or unlink a task to a GDD section
    """
    def post(self, request, task_id):
        task = get_object_or_404(GameTask, id=task_id)
        section_id = request.POST.get('section_id')
        
        # Check permissions
        game = task.game
        if not (request.user.is_staff or request.user == game.lead_developer or 
                request.user == game.lead_designer or request.user == task.assigned_to):
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        if section_id:
            try:
                section = GDDSection.objects.get(id=section_id, gdd__game=game)
                task.gdd_section = section
                task.save()
                return JsonResponse({
                    'status': 'success', 
                    'message': f'Task linked to section: {section.title}'
                })
            except GDDSection.DoesNotExist:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Section not found'
                }, status=404)
        else:
            # Unlink task from section
            task.gdd_section = None
            task.save()
            return JsonResponse({
                'status': 'success', 
                'message': 'Task unlinked from section'
            })


class GameDesignDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Delete a game design document and redirect to the create page.
    This is primarily for development and testing purposes.
    """
    def test_func(self):
        # Only allow staff or game leads to delete GDDs
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        try:
            from django.db import transaction
            with transaction.atomic():
                # Get the GDD and all its related objects
                gdd = GameDesignDocument.objects.get(game=game)
                
                # Get all sections
                sections = gdd.sections.all()
                
                # Delete all features first to avoid integrity errors
                from projects.game_models import GDDFeature
                for section in sections:
                    GDDFeature.objects.filter(section=section).delete()
                
                # Delete all sections
                sections.delete()
                
                # Finally delete the GDD
                gdd.delete()
                
                messages.success(request, "Game Design Document has been deleted. You can now create a new one.")
        except GameDesignDocument.DoesNotExist:
            messages.info(request, "No Game Design Document exists for this game.")
        
        return redirect('games:gdd_simple_create', game_id=game_id)
