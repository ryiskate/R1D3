"""
Views for creating and editing Game Design Documents with a structured form approach.
This provides a user-friendly interface without requiring HTML editing.
"""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.contrib import messages

from .game_models import GameProject, GameDesignDocument, GDDSection, GDDFeature

# Define the standard GDD sections based on industry-standard 13-section structure
STANDARD_GDD_SECTIONS = [
    {
        'title': 'Game Overview',
        'section_id': 'game_overview',
        'order': 1,
        'description': 'Provide a high-level overview of your game concept, target audience, and unique selling points.'
    },
    {
        'title': 'Gameplay',
        'section_id': 'gameplay',
        'order': 2,
        'description': 'Describe the core mechanics, controls, progression systems, and game economy.'
    },
    {
        'title': 'Game World',
        'section_id': 'game_world',
        'order': 3,
        'description': 'Describe the world overview, environments, level design, and world interaction.'
    },
    {
        'title': 'Characters',
        'section_id': 'characters',
        'order': 4,
        'description': 'Detail player characters, NPCs, enemies, and relationships.'
    },
    {
        'title': 'Narrative',
        'section_id': 'narrative',
        'order': 5,
        'description': 'Outline story overview, narrative structure, storytelling methods, and player choice.'
    },
    {
        'title': 'Technical Requirements',
        'section_id': 'technical',
        'order': 6,
        'description': 'Define platform-specific requirements and technical specifications.'
    },
    {
        'title': 'Audio Design',
        'section_id': 'audio',
        'order': 7,
        'description': 'Specify music, sound effects, voice acting, and audio implementation.'
    },
    {
        'title': 'User Interface & UX',
        'section_id': 'ui_ux',
        'order': 8,
        'description': 'Detail UI design, HUD, menus, and accessibility features.'
    },
    {
        'title': 'Art Direction',
        'section_id': 'art',
        'order': 9,
        'description': 'Define visual style, character art, environment art, and visual effects.'
    },
    {
        'title': 'Monetization',
        'section_id': 'monetization',
        'order': 10,
        'description': 'Outline revenue model, in-game purchases, monetization balance, and additional revenue streams.'
    },
    {
        'title': 'Development & Production',
        'section_id': 'development',
        'order': 11,
        'description': 'Plan development roadmap, team structure, budget, and post-launch support.'
    },
    {
        'title': 'Marketing & Distribution',
        'section_id': 'marketing',
        'order': 12,
        'description': 'Detail marketing strategy, promotional channels, distribution platforms, and community engagement.'
    },
    {
        'title': 'Appendices',
        'section_id': 'appendices',
        'order': 13,
        'description': 'Include reference materials, technical specifications, change log, and glossary.'
    }
]


class GDDStructuredCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for creating a Game Design Document using a structured form approach
    that matches the 13-section industry-standard GDD template structure
    """
    def test_func(self):
        # Get the game by its ID
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Check if a GDD already exists for this game
        if hasattr(game, 'design_document'):
            messages.warning(request, "A Game Design Document already exists for this game.")
            return redirect('games:gdd_detail', pk=game.design_document.id)
        
        # Create a simple context for the template
        context = {
            'game': game,
            'standard_sections': STANDARD_GDD_SECTIONS
        }
        
        return render(request, 'projects/gdd_structured_create.html', context)
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Get the title from the form
        title = request.POST.get('high_concept', f"{game.title} - Game Design Document")
        
        # Create the GDD with transaction to ensure all related objects are created together
        with transaction.atomic():
            # Create the main GDD object
            gdd = GameDesignDocument.objects.create(
                game=game,
                high_concept=title,
                player_experience="What the player will experience playing this game",
                core_mechanics="Core gameplay mechanics will be defined here",
                game_rules="Game rules will be defined here",
                controls="Controls will be defined here"
            )
            
            # Create all standard sections
            for section_data in STANDARD_GDD_SECTIONS:
                section_id = section_data['section_id']
                section_title = section_data['title']
                section_order = section_data['order']
                
                # Create the section
                gdd_section = GDDSection.objects.create(
                    gdd=gdd,
                    title=section_title,
                    section_id=section_id,
                    order=section_order,
                    content=section_data.get('description', '')
                )
                
                # Handle Game Overview section features with editable names
                if section_id == 'game_overview':
                    # Get form data for high concept
                    high_concept_name = request.POST.get('high_concept_name', 'High Concept')
                    high_concept_desc = request.POST.get('high_concept', '')
                    high_concept_priority = request.POST.get('high_concept_priority', 'critical')
                    high_concept_status = request.POST.get('high_concept_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="high_concept",
                        feature_name=high_concept_name,
                        description=high_concept_desc or "A brief, one or two sentence description of the game.",
                        priority=high_concept_priority,
                        status=high_concept_status,
                        order=1
                    )
                    
                    # Get form data for target audience
                    target_audience_name = request.POST.get('target_audience_name', 'Target Audience')
                    target_audience_desc = request.POST.get('target_audience', '')
                    target_audience_priority = request.POST.get('target_audience_priority', 'medium')
                    target_audience_status = request.POST.get('target_audience_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="target_audience",
                        feature_name=target_audience_name,
                        description=target_audience_desc or "The types of players the game is designed for.",
                        priority=target_audience_priority,
                        status=target_audience_status,
                        order=2
                    )
                    
                    # Get form data for unique selling points
                    usp_name = request.POST.get('unique_selling_points_name', 'Unique Selling Points')
                    usp_desc = request.POST.get('unique_selling_points', '')
                    usp_priority = request.POST.get('unique_selling_points_priority', 'high')
                    usp_status = request.POST.get('unique_selling_points_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="unique_selling_points",
                        feature_name=usp_name,
                        description=usp_desc or "What makes this game unique compared to others.",
                        priority=usp_priority,
                        status=usp_status,
                        order=3
                    )
                    
                # Handle Gameplay section features with editable names
                elif section_id == 'gameplay':
                    # Get form data for core mechanics
                    core_mechanics_name = request.POST.get('core_mechanics_name', 'Core Mechanics')
                    core_mechanics_desc = request.POST.get('core_mechanics', '')
                    core_mechanics_priority = request.POST.get('core_mechanics_priority', 'critical')
                    core_mechanics_status = request.POST.get('core_mechanics_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="core_mechanics",
                        feature_name=core_mechanics_name,
                        description=core_mechanics_desc or "The primary gameplay mechanics that define the experience.",
                        priority=core_mechanics_priority,
                        status=core_mechanics_status,
                        order=1
                    )
                    
                    # Get form data for controls
                    controls_name = request.POST.get('controls_name', 'Controls')
                    controls_desc = request.POST.get('controls', '')
                    controls_priority = request.POST.get('controls_priority', 'high')
                    controls_status = request.POST.get('controls_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="controls",
                        feature_name=controls_name,
                        description=controls_desc or "How the player interacts with the game.",
                        priority=controls_priority,
                        status=controls_status,
                        order=2
                    )
                    
                # Handle Game World section features with editable names
                elif section_id == 'game_world':
                    # Get form data for world overview
                    world_overview_name = request.POST.get('world_overview_name', 'World Overview')
                    world_overview_desc = request.POST.get('world_overview', '')
                    world_overview_priority = request.POST.get('world_overview_priority', 'high')
                    world_overview_status = request.POST.get('world_overview_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="world_overview",
                        feature_name=world_overview_name,
                        description=world_overview_desc or "The setting and general atmosphere of the game world.",
                        priority=world_overview_priority,
                        status=world_overview_status,
                        order=1
                    )
                    
                    # Get form data for environments
                    environments_name = request.POST.get('environments_name', 'Environments')
                    environments_desc = request.POST.get('environments', '')
                    environments_priority = request.POST.get('environments_priority', 'high')
                    environments_status = request.POST.get('environments_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="environments",
                        feature_name=environments_name,
                        description=environments_desc or "Different environments players will encounter.",
                        priority=environments_priority,
                        status=environments_status,
                        order=2
                    )
                    
                # For other sections, add a placeholder feature
                else:
                    # Check if there are any feature name inputs for this section
                    # Format would be {section_id}_feature_name
                    feature_name_key = f"{section_id}_feature_name"
                    feature_desc_key = f"{section_id}_feature"
                    feature_priority_key = f"{section_id}_feature_priority"
                    feature_status_key = f"{section_id}_feature_status"
                    
                    # Check if we have a custom feature name input for this section
                    if feature_name_key in request.POST and request.POST.get(feature_name_key):
                        feature_name = request.POST.get(feature_name_key)
                        feature_desc = request.POST.get(feature_desc_key, '')
                        feature_priority = request.POST.get(feature_priority_key, 'medium')
                        feature_status = request.POST.get(feature_status_key, 'backlog')
                        
                        GDDFeature.objects.create(
                            section=gdd_section,
                            feature_name=feature_name,
                            description=feature_desc or "Click to edit this feature",
                            priority=feature_priority,
                            status=feature_status,
                            order=1
                        )
                    else:
                        # Add a placeholder feature
                        GDDFeature.objects.create(
                            section=gdd_section,
                            feature_name=f"Add {section_title} features here",
                            description="Click to edit this placeholder feature",
                            priority="medium",
                            status="backlog",
                            order=1
                        )
            
            messages.success(request, f"Game Design Document created successfully for {game.title}.")
            return redirect('games:gdd_detail', pk=gdd.id)


class GameDesignDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for deleting a Game Design Document
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
            with transaction.atomic():
                # Get the GDD and all its related objects
                gdd = GameDesignDocument.objects.get(game=game)
                
                # Get all sections
                sections = gdd.sections.all()
                
                # Delete all features first to avoid integrity errors
                for section in sections:
                    GDDFeature.objects.filter(section=section).delete()
                
                # Then delete all sections
                sections.delete()
                
                # Finally delete the GDD itself
                gdd.delete()
                
                messages.success(request, "Game Design Document has been deleted.")
        except GameDesignDocument.DoesNotExist:
            messages.info(request, "No Game Design Document exists for this game.")
        
        return redirect('games:game_detail', pk=game_id)
