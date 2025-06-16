"""
Views for creating and editing Game Design Documents with a structured form approach.
This provides a user-friendly interface without requiring HTML editing.
"""
import os
import json
from bs4 import BeautifulSoup
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.contrib import messages

from .game_models import GameProject, GameDesignDocument, GDDSection, GDDFeature
from .gdd_structured_form import (
    GDDStructuredForm, GDDSectionStructuredForm, GDDFeatureStructuredForm,
    GDDSectionFormSet, GDDFeatureFormSet, GDDSubsectionFormSet, STANDARD_GDD_SECTIONS
)
from .gdd_utils import prepare_structured_gdd_sections

class GDDStructuredCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for creating a Game Design Document using a structured form approach
    that matches the 13-section GDD template structure
    """
    def test_func(self):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer

    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Check if GDD already exists
        try:
            gdd = GameDesignDocument.objects.get(game=game)
            # Redirect back to the game detail page
            return redirect('games:game_detail', pk=game.id)
        except GameDesignDocument.DoesNotExist:
            # Create an empty GDD with all standard sections automatically
            if request.GET.get('auto_create', False):
                # Create the GDD with the correct fields from the model
                gdd = GameDesignDocument.objects.create(
                    game=game,
                    high_concept=f"{game.title} - Game Design Document",
                    player_experience="What the player will experience playing this game",
                    core_mechanics="Core gameplay mechanics will be defined here",
                    game_rules="Game rules will be defined here",
                    controls="Controls will be defined here"
                )
                
                # Create all standard sections
                for section in STANDARD_GDD_SECTIONS:
                    section_id = section['section_id']
                    
                    # Create the section
                    gdd_section = GDDSection.objects.create(
                        gdd=gdd,
                        title=section['title'],
                        section_id=section_id,
                        order=section['order'],
                        content=''
                    )
                    
                    # Create default empty features for each subsection if defined
                    if 'subsections' in section:
                        for subsection in section['subsections']:
                            subsection_id = subsection['subsection_id']
                            # Create an empty placeholder feature for this subsection
                            GDDFeature.objects.create(
                                section=gdd_section,
                                subsection_id=subsection_id,
                                feature_name=f"Add {subsection['title']} features here",
                                description="Click to edit this placeholder feature",
                                priority="medium",
                                order=0
                            )
                
                messages.success(request, f"Empty GDD created for {game.title} with all standard sections.")
                # Redirect back to the game detail page instead of the edit page
                return redirect('games:game_detail', pk=game.id)
        
        form = GDDStructuredForm(initial={'game': game, 'high_concept': f"{game.title} - Game Design Document"})
        
        # Initialize section formsets based on the standard GDD sections using our utility function
        section_formsets = prepare_structured_gdd_sections()
        
        context = {
            'form': form,
            'game': game,
            'section_formsets': section_formsets,
            'standard_sections': STANDARD_GDD_SECTIONS,
            'show_auto_create': True  # Flag to show auto-create button
        }
        
        return render(request, 'projects/gdd_structured_form.html', context)
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        form = GDDStructuredForm(request.POST)
        
        if form.is_valid():
            # Save the GDD
            gdd = form.save(commit=False)
            gdd.game = game
            gdd.save()
            
            # Process each section
            for section in STANDARD_GDD_SECTIONS:
                section_id = section['section_id']
                
                # Create the section
                gdd_section = GDDSection.objects.create(
                    gdd=gdd,
                    title=section['title'],
                    section_id=section_id,
                    order=section['order'],
                    content=request.POST.get(f'section_content_{section_id}', '')
                )
                
                # Process features for this section
                feature_prefix = f'feature_{section_id}'
                feature_count = int(request.POST.get(f'{feature_prefix}-TOTAL_FORMS', 0))
                
                for i in range(feature_count):
                    # Skip if this is an empty or deleted feature
                    if request.POST.get(f'{feature_prefix}-{i}-DELETE', '') == 'on':
                        continue
                        
                    feature_name = request.POST.get(f'{feature_prefix}-{i}-feature_name', '')
                    if not feature_name:
                        continue
                        
                    # Create the feature
                    GDDFeature.objects.create(
                        section=gdd_section,
                        feature_name=feature_name,
                        description=request.POST.get(f'{feature_prefix}-{i}-description', ''),
                        priority=request.POST.get(f'{feature_prefix}-{i}-priority', 'medium'),
                        status=request.POST.get(f'{feature_prefix}-{i}-status', 'to_do'),
                        task_id=request.POST.get(f'{feature_prefix}-{i}-task_id', ''),
                        assigned_to=request.POST.get(f'{feature_prefix}-{i}-assigned_to', ''),
                        due_date=request.POST.get(f'{feature_prefix}-{i}-due_date', None) or None
                    )
            
            return redirect('games:game_detail', pk=game_id)
        
        # If form is invalid, re-render with errors
        context = {
            'form': form,
            'game': game,
            'standard_sections': STANDARD_GDD_SECTIONS
        }
        
        return render(request, 'projects/gdd_structured_form.html', context)


class GDDStructuredEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for editing a Game Design Document using a structured form approach
    that matches the 13-section industry-standard GDD template structure
    """
    def test_func(self):
        # Get the GDD by its primary key
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer

    def get(self, request, *args, **kwargs):
        # Get the GDD by its primary key
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        
        form = GDDStructuredForm(instance=gdd)
        
        # Get all sections for this GDD
        existing_sections = GDDSection.objects.filter(gdd=gdd).order_by('order')
        
        # Initialize section formsets based on the standard GDD sections using our utility function
        section_formsets = prepare_structured_gdd_sections(gdd)
        
        # Prepare section data for template with section numbers
        numbered_sections = []
        for i, section_data in enumerate(STANDARD_GDD_SECTIONS, 1):
            section_id = section_data['section_id']
            if section_id in section_formsets:
                section_formsets[section_id]['section_number'] = i
                numbered_sections.append({
                    'section_id': section_id,
                    'section_number': i,
                    'formset': section_formsets[section_id]
                })
        
        context = {
            'form': form,
            'game': game,
            'gdd': gdd,
            'section_formsets': section_formsets,
            'numbered_sections': numbered_sections,
            'standard_sections': STANDARD_GDD_SECTIONS,
            'is_edit': True
        }
        
        return render(request, 'projects/gdd_structured_form.html', context)
    
    def post(self, request, *args, **kwargs):
        # Get the GDD by its primary key
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        
        form = GDDStructuredForm(request.POST, instance=gdd)
        
        if form.is_valid():
            # Save the GDD
            gdd = form.save()
            
            # Process each section
            for i, section in enumerate(STANDARD_GDD_SECTIONS, 1):
                section_id = section['section_id']
                
                # Get or create the section
                gdd_section, created = GDDSection.objects.get_or_create(
                    gdd=gdd,
                    section_id=section_id,
                    defaults={
                        'title': section['title'],
                        'order': i,
                        'content': request.POST.get(f'section_content_{section_id}', ''),
                        'description': section.get('description', '')
                    }
                )
                
                # Update existing section
                if not created:
                    gdd_section.title = section['title']
                    gdd_section.order = i
                    gdd_section.content = request.POST.get(f'section_content_{section_id}', '')
                    gdd_section.description = section.get('description', '')
                    gdd_section.save()
                
                # Process section-level features (without subsection_id)
                feature_prefix = f'feature_{section_id}'
                if f'{feature_prefix}-TOTAL_FORMS' in request.POST:
                    feature_count = int(request.POST.get(f'{feature_prefix}-TOTAL_FORMS', 0))
                    
                    # Process each feature in the formset
                    for j in range(feature_count):
                        feature_id = request.POST.get(f'{feature_prefix}-{j}-id', '')
                        feature_name = request.POST.get(f'{feature_prefix}-{j}-feature_name', '')
                        description = request.POST.get(f'{feature_prefix}-{j}-description', '')
                        priority = request.POST.get(f'{feature_prefix}-{j}-priority', '')
                        status = request.POST.get(f'{feature_prefix}-{j}-status', '')
                        task_id = request.POST.get(f'{feature_prefix}-{j}-task_id', '')
                        assigned_to = request.POST.get(f'{feature_prefix}-{j}-assigned_to', '')
                        due_date = request.POST.get(f'{feature_prefix}-{j}-due_date', None) or None
                        delete = request.POST.get(f'{feature_prefix}-{j}-DELETE', '') == 'on'
                        
                        # Skip empty features
                        if not feature_name and not feature_id:
                            continue
                            
                        # Delete feature if marked for deletion
                        if delete and feature_id:
                            try:
                                GDDFeature.objects.get(id=feature_id).delete()
                            except GDDFeature.DoesNotExist:
                                pass
                            continue
                            
                        # Update existing feature or create new one
                        if feature_id:
                            try:
                                feature = GDDFeature.objects.get(id=feature_id)
                                feature.feature_name = feature_name
                                feature.description = description
                                feature.priority = priority
                                feature.status = status
                                feature.task_id = task_id
                                feature.assigned_to = assigned_to
                                feature.due_date = due_date
                                feature.save()
                            except GDDFeature.DoesNotExist:
                                pass
                        else:
                            # Create new feature
                            GDDFeature.objects.create(
                                section=gdd_section,
                                feature_name=feature_name,
                                description=description,
                                priority=priority,
                                status=status,
                                task_id=task_id,
                                assigned_to=assigned_to,
                                due_date=due_date
                            )
                
                # Process subsection features
                if 'subsections' in section:
                    for subsection in section['subsections']:
                        subsection_id = subsection['subsection_id']
                        subsection_prefix = f'subsection_{section_id}_{subsection_id}'
                        
                        if f'{subsection_prefix}-TOTAL_FORMS' in request.POST:
                            subsection_count = int(request.POST.get(f'{subsection_prefix}-TOTAL_FORMS', 0))
                            
                            # Process each feature in the subsection formset
                            for j in range(subsection_count):
                                feature_id = request.POST.get(f'{subsection_prefix}-{j}-id', '')
                                feature_name = request.POST.get(f'{subsection_prefix}-{j}-feature_name', '')
                                description = request.POST.get(f'{subsection_prefix}-{j}-description', '')
                                priority = request.POST.get(f'{subsection_prefix}-{j}-priority', '')
                                status = request.POST.get(f'{subsection_prefix}-{j}-status', '')
                                task_id = request.POST.get(f'{subsection_prefix}-{j}-task_id', '')
                                assigned_to = request.POST.get(f'{subsection_prefix}-{j}-assigned_to', '')
                                due_date = request.POST.get(f'{subsection_prefix}-{j}-due_date', None) or None
                                delete = request.POST.get(f'{subsection_prefix}-{j}-DELETE', '') == 'on'
                                
                                # Skip empty features
                                if not feature_name and not feature_id:
                                    continue
                                    
                                # Delete feature if marked for deletion
                                if delete and feature_id:
                                    try:
                                        GDDFeature.objects.get(id=feature_id).delete()
                                    except GDDFeature.DoesNotExist:
                                        pass
                                    continue
                                    
                                # Update existing feature or create new one
                                if feature_id:
                                    try:
                                        feature = GDDFeature.objects.get(id=feature_id)
                                        feature.feature_name = feature_name
                                        feature.description = description
                                        feature.priority = priority
                                        feature.status = status
                                        feature.task_id = task_id
                                        feature.assigned_to = assigned_to
                                        feature.due_date = due_date
                                        feature.save()
                                    except GDDFeature.DoesNotExist:
                                        pass
                                else:
                                    # Create new feature
                                    GDDFeature.objects.create(
                                        section=gdd_section,
                                        subsection_id=subsection_id,
                                        feature_name=feature_name,
                                        description=description,
                                        priority=priority,
                                        status=status,
                                        task_id=task_id,
                                        assigned_to=assigned_to,
                                        due_date=due_date
                                    )
            
            messages.success(request, f"GDD '{gdd.high_concept}' updated successfully.")
            return redirect('games:game_detail', pk=game.id)
        
        # If form is invalid, re-render with errors
        context = {
            'form': form,
            'game': game,
            'gdd': gdd,
            'standard_sections': STANDARD_GDD_SECTIONS,
            'is_edit': True
        }
        
        return render(request, 'projects/gdd_structured_form.html', context)


class GDDSectionFeatureView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for managing features for a specific GDD section
    """
    def test_func(self):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        section_id = self.kwargs.get('section_id')
        
        game = get_object_or_404(GameProject, id=game_id)
        
        try:
            gdd = GameDesignDocument.objects.get(game=game)
            section = GDDSection.objects.get(gdd=gdd, section_id=section_id)
        except (GameDesignDocument.DoesNotExist, GDDSection.DoesNotExist):
            return JsonResponse({'error': 'GDD or section not found'}, status=404)
        
        # Get features for this section
        features = GDDFeature.objects.filter(section=section).order_by('order', 'id')
        
        # Group features by subsection_id
        features_by_subsection = {}
        for feature in features:
            subsection_id = feature.subsection_id or 'main'
            if subsection_id not in features_by_subsection:
                features_by_subsection[subsection_id] = []
            features_by_subsection[subsection_id].append({
                'id': feature.id,
                'feature_name': feature.feature_name,
                'description': feature.description,
                'priority': feature.priority,
                'status': feature.status,
                'task_id': feature.task_id,
                'assigned_to': feature.assigned_to,
                'due_date': feature.due_date.isoformat() if feature.due_date else None,
                'order': feature.order
            })
        
        return JsonResponse({
            'section': {
                'id': section.id,
                'title': section.title,
                'section_id': section.section_id,
                'content': section.content
            },
            'features_by_subsection': features_by_subsection
        })
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        section_id = self.kwargs.get('section_id')
        
        game = get_object_or_404(GameProject, id=game_id)
        
        try:
            gdd = GameDesignDocument.objects.get(game=game)
            section = GDDSection.objects.get(gdd=gdd, section_id=section_id)
        except (GameDesignDocument.DoesNotExist, GDDSection.DoesNotExist):
            return JsonResponse({'error': 'GDD or section not found'}, status=404)
        
        try:
            data = json.loads(request.body)
            feature_name = data.get('feature_name', '')
            description = data.get('description', '')
            priority = data.get('priority', 'medium')
            subsection_id = data.get('subsection_id', None)
            
            if not feature_name:
                return JsonResponse({'error': 'Feature name is required'}, status=400)
            
            # Create the feature
            feature = GDDFeature.objects.create(
                section=section,
                subsection_id=subsection_id,
                feature_name=feature_name,
                description=description,
                priority=priority,
                status='to_do',
                order=0
            )
            
            return JsonResponse({
                'id': feature.id,
                'feature_name': feature.feature_name,
                'description': feature.description,
                'priority': feature.priority,
                'status': feature.status,
                'subsection_id': feature.subsection_id,
                'order': feature.order
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class UpdateFeatureOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for updating the order of features within a section
    """
    def test_func(self):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        section_id = self.kwargs.get('section_id')
        
        game = get_object_or_404(GameProject, id=game_id)
        
        try:
            data = json.loads(request.body)
            feature_orders = data.get('feature_orders', [])
            
            with transaction.atomic():
                for order_data in feature_orders:
                    feature_id = order_data.get('id')
                    new_order = order_data.get('order')
                    
                    try:
                        feature = GDDFeature.objects.get(id=feature_id)
                        feature.order = new_order
                        feature.save()
                    except GDDFeature.DoesNotExist:
                        pass
            
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
