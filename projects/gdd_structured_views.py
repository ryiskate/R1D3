"""
Views for creating and editing Game Design Documents with a structured form approach.
This provides a user-friendly interface without requiring HTML editing.
"""
import os
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.contrib import messages

from .game_models import GameProject, GameDesignDocument, GDDSection, GDDFeature

# Simple form for GDD creation
class GDDStructuredForm:
    def __init__(self, **kwargs):
        self.initial = kwargs.get('initial', {})
        
    def is_valid(self):
        return True
        
    def save(self, commit=True):
        return None

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
        'description': 'Define marketing strategy, promotional channels, distribution platforms, and community engagement.'
    },
    {
        'title': 'Appendices',
        'section_id': 'appendices',
        'order': 13,
        'description': 'Include reference materials, technical specifications, change log, and glossary.'
    }
]

class GDDSimpleCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for creating a Game Design Document using a simplified form approach
    with just a title and a basic table structure
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
            messages.warning(request, f"A GDD already exists for {game.title}. You can edit it instead.")
            return redirect('games:gdd_detail', pk=gdd.id)
        except GameDesignDocument.DoesNotExist:
            pass
        
        context = {
            'game': game,
        }
        
        return render(request, 'projects/gdd_simple_create.html', context)
    
    def post(self, request, *args, **kwargs):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        
        # Check if GDD already exists
        try:
            gdd = GameDesignDocument.objects.get(game=game)
            messages.warning(request, f"A GDD already exists for {game.title}. You can edit it instead.")
            return redirect('games:gdd_detail', pk=gdd.id)
        except GameDesignDocument.DoesNotExist:
            pass
        
        title = request.POST.get('title', f"{game.title} - Game Design Document")
        description = request.POST.get('description', game.description or "")
        
        # Get feature data from the form
        high_concept = request.POST.get('high_concept', "")
        high_concept_priority = request.POST.get('high_concept_priority', "critical")
        high_concept_status = request.POST.get('high_concept_status', "backlog")
        high_concept_notes = request.POST.get('high_concept_notes', "")
        
        target_audience = request.POST.get('target_audience', "")
        target_audience_priority = request.POST.get('target_audience_priority', "medium")
        target_audience_status = request.POST.get('target_audience_status', "to_do")
        target_audience_notes = request.POST.get('target_audience_notes', "")
        
        unique_selling_points = request.POST.get('unique_selling_points', "")
        unique_selling_points_priority = request.POST.get('unique_selling_points_priority', "high")
        unique_selling_points_status = request.POST.get('unique_selling_points_status', "in_progress")
        unique_selling_points_notes = request.POST.get('unique_selling_points_notes', "")
        
        # Get additional notes and section title if provided
        additional_notes = request.POST.get('additional_notes', '')
        section_title = request.POST.get('section_title', '')
        
        # Collect all bullet points
        bullet_points = []
        for key in request.POST.keys():
            if key.startswith('bullet_point_'):
                value = request.POST.get(key, '').strip()
                if value:  # Only add non-empty bullet points
                    bullet_points.append(value)
        
        # Format bullet points as HTML if any exist
        bullet_points_html = ''
        if bullet_points:
            bullet_points_html = '<ul>\n'
            for point in bullet_points:
                bullet_points_html += f'<li>{point}</li>\n'
            bullet_points_html += '</ul>'
        
        # Create the GDD
        with transaction.atomic():
            # Get custom feature names from the form
            high_concept_name = request.POST.get('high_concept_name', 'High Concept')
            target_audience_name = request.POST.get('target_audience_name', 'Target Audience')
            unique_selling_points_name = request.POST.get('unique_selling_points_name', 'Unique Selling Points')
            
            # Collect dynamically added custom features
            custom_features_html = ''
            custom_feature_prefix = 'custom_feature_'
            
            # Find all custom feature fields in the POST data
            for key in request.POST.keys():
                # Look for keys like 'custom_feature_1', 'custom_feature_2', etc.
                if key.startswith(custom_feature_prefix) and not key.endswith('_name') and not key.endswith('_priority') and not key.endswith('_status') and not key.endswith('_notes'):
                    feature_id = key
                    
                    # Get the feature data
                    feature_name = request.POST.get(f"{feature_id}_name", "Custom Feature")
                    feature_desc = request.POST.get(feature_id, "")
                    feature_priority = request.POST.get(f"{feature_id}_priority", "medium")
                    feature_status = request.POST.get(f"{feature_id}_status", "backlog")
                    feature_notes = request.POST.get(f"{feature_id}_notes", "")
                    
                    # Add to custom features HTML
                    custom_features_html += f'''
                    <tr>
                        <td>{feature_name}</td>
                        <td>{feature_desc or "Custom feature description"}</td>
                        <td><span class="badge bg-primary">{feature_priority}</span></td>
                        <td><span class="badge bg-secondary">{feature_status}</span></td>
                        <td>{feature_notes}</td>
                    </tr>
                    '''
            
            # Create custom section HTML if a title was provided
            custom_section_html = ''
            if section_title:
                custom_section_html = f'''
                <h2>{section_title}</h2>
                <div class="section-content">
                    <p>{additional_notes}</p>
                    {bullet_points_html}
                </div>
                '''
            
            # Get features section title and description
            features_section_title = request.POST.get('features_section_title', 'Core Game Features')
            features_section_description = request.POST.get('features_section_description', 'Define the essential features that make your game unique')
            
            # Process static sections
            static_sections_html = ''
            static_sections = [
                'gameplay', 'gameworld', 'characters', 'narrative', 'technical', 
                'audio', 'ui', 'art', 'monetization', 'development', 'marketing', 'appendices'
            ]
            
            section_titles = {
                'gameplay': '2. Gameplay',
                'gameworld': '3. Game World',
                'characters': '4. Characters',
                'narrative': '5. Narrative',
                'technical': '6. Technical Requirements',
                'audio': '7. Audio Design',
                'ui': '8. User Interface & UX',
                'art': '9. Art Direction',
                'monetization': '10. Monetization',
                'development': '11. Development & Production',
                'marketing': '12. Marketing & Distribution',
                'appendices': '13. Appendices'
            }
            
            section_descriptions = {
                'gameplay': 'Define the core mechanics, controls, progression systems, and game economy',
                'gameworld': 'Define the world overview, environments, level design, and world interaction',
                'characters': 'Define player characters, NPCs, enemies, and relationships',
                'narrative': 'Define the story overview, narrative structure, storytelling methods, and player choice',
                'technical': 'Define platform-specific requirements and technical specifications',
                'audio': 'Define music, sound effects, voice acting, and audio implementation',
                'ui': 'Define UI design, HUD, menus, and accessibility features',
                'art': 'Define visual style, character art, environment art, and visual effects',
                'monetization': 'Define revenue model, in-game purchases, monetization balance, and additional revenue streams',
                'development': 'Define development roadmap, team structure, budget, and post-launch support',
                'marketing': 'Define marketing strategy, promotional channels, distribution platforms, and community engagement',
                'appendices': 'Additional reference materials, technical specifications, change log, and glossary'
            }
            
            for section_key in static_sections:
                # Check if section has content
                has_feature_table = False
                has_bullet_points = False
                
                # Check for feature table
                feature_keys = []
                for key in request.POST.keys():
                    if key.startswith(f"{section_key}_feature_") and not key.endswith('_name') and not key.endswith('_priority') and not key.endswith('_status') and not key.endswith('_notes'):
                        feature_keys.append(key)
                        has_feature_table = True
                
                # Check for bullet points
                bullet_keys = []
                for key in request.POST.keys():
                    if key.startswith(f"{section_key}_bullet_"):
                        bullet_keys.append(key)
                        has_bullet_points = True
                
                # If section has content, generate HTML
                if has_feature_table or has_bullet_points:
                    section_html = f'''
                    <h2>{section_titles.get(section_key, f'Section {section_key}')}</h2>
                    <p>{section_descriptions.get(section_key, '')}</p>
                    '''
                    
                    if has_feature_table:
                        # Generate feature table HTML
                        section_html += '''
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th style="width: 20%">Feature</th>
                                    <th style="width: 40%">Description</th>
                                    <th style="width: 10%">Priority</th>
                                    <th style="width: 10%">Status</th>
                                    <th style="width: 20%">Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                        '''
                        
                        # Sort feature keys to maintain order
                        feature_keys.sort(key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else 0)
                        
                        for feature_key in feature_keys:
                            feature_id = feature_key.split(f"{section_key}_feature_")[1]
                            feature_name = request.POST.get(f"{section_key}_feature_{feature_id}_name", f"Feature {feature_id}")
                            feature_desc = request.POST.get(feature_key, "")
                            feature_priority = request.POST.get(f"{section_key}_feature_{feature_id}_priority", "medium")
                            feature_status = request.POST.get(f"{section_key}_feature_{feature_id}_status", "backlog")
                            feature_notes = request.POST.get(f"{section_key}_feature_{feature_id}_notes", "")
                            
                            section_html += f'''
                            <tr>
                                <td>{feature_name}</td>
                                <td>{feature_desc}</td>
                                <td><span class="badge bg-primary">{feature_priority}</span></td>
                                <td><span class="badge bg-secondary">{feature_status}</span></td>
                                <td>{feature_notes}</td>
                            </tr>
                            '''
                        
                        section_html += '''
                            </tbody>
                        </table>
                        '''
                    
                    if has_bullet_points:
                        # Generate bullet points HTML
                        section_html += '<ul>\n'
                        
                        # Sort bullet keys to maintain order
                        bullet_keys.sort(key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else 0)
                        
                        for bullet_key in bullet_keys:
                            bullet_text = request.POST.get(bullet_key, "").strip()
                            if bullet_text:  # Only add non-empty bullet points
                                section_html += f'<li>{bullet_text}</li>\n'
                        
                        section_html += '</ul>\n'
                    
                    # Add section HTML to static sections HTML
                    static_sections_html += section_html
            
            # Process dynamic sections
            dynamic_sections_html = ''
            dynamic_section_prefix = 'dynamic_section_'
            dynamic_sections = set()
            
            # Find all dynamic section fields in the POST data
            for key in request.POST.keys():
                if key.startswith(dynamic_section_prefix) and '_title' in key:
                    section_id = key.split('_title')[0].replace(dynamic_section_prefix, '')
                    dynamic_sections.add(section_id)
            
            # Process each dynamic section
            for section_id in dynamic_sections:
                section_title = request.POST.get(f'{dynamic_section_prefix}{section_id}_title', f'Section {section_id}')
                section_description = request.POST.get(f'{dynamic_section_prefix}{section_id}_description', '')
                
                # Start the section HTML
                section_html = f'''
                <h3>{section_title}</h3>
                <p>{section_description}</p>
                '''
                
                # Check if this is a table section or bullet section
                feature_keys = [k for k in request.POST.keys() if k.startswith(f'{dynamic_section_prefix}{section_id}_feature_') and 
                                not k.endswith('_name') and not k.endswith('_priority') and 
                                not k.endswith('_status') and not k.endswith('_notes')]
                
                bullet_keys = [k for k in request.POST.keys() if k.startswith(f'{dynamic_section_prefix}{section_id}_bullet_')]
                
                # If it has features, create a table
                if feature_keys:
                    section_html += '''
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Feature</th>
                                <th>Description</th>
                                <th>Priority</th>
                                <th>Status</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                    '''
                    
                    # Process each feature in this section
                    for feature_key in feature_keys:
                        feature_id = feature_key.split(f'{dynamic_section_prefix}{section_id}_feature_')[1]
                        feature_name = request.POST.get(f'{dynamic_section_prefix}{section_id}_feature_{feature_id}_name', f'Feature {feature_id}')
                        feature_desc = request.POST.get(feature_key, "")
                        feature_priority = request.POST.get(f'{dynamic_section_prefix}{section_id}_feature_{feature_id}_priority', 'medium')
                        feature_status = request.POST.get(f'{dynamic_section_prefix}{section_id}_feature_{feature_id}_status', 'backlog')
                        feature_notes = request.POST.get(f'{dynamic_section_prefix}{section_id}_feature_{feature_id}_notes', '')
                        
                        # Add the feature row
                        section_html += f'''
                        <tr>
                            <td>{feature_name}</td>
                            <td>{feature_desc}</td>
                            <td><span class="badge bg-primary">{feature_priority}</span></td>
                            <td><span class="badge bg-secondary">{feature_status}</span></td>
                            <td>{feature_notes}</td>
                        </tr>
                        '''
                    
                    section_html += '''
                        </tbody>
                    </table>
                    '''
                
                # If it has bullets, create a bullet list
                elif bullet_keys:
                    section_html += '<ul>\n'
                    
                    # Process each bullet point
                    for bullet_key in sorted(bullet_keys):
                        bullet_content = request.POST.get(bullet_key, '')
                        if bullet_content.strip():
                            section_html += f'<li>{bullet_content}</li>\n'
                    
                    section_html += '</ul>\n'
                
                # Add the section HTML to the dynamic sections
                dynamic_sections_html += section_html
            
            # Create HTML content for the GDD
            html_content = f'''
            <h1>{title}</h1>
            <p>{description}</p>
            
            <h2>1. Game Overview</h2>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th style="width: 20%">Feature</th>
                        <th style="width: 40%">Description</th>
                        <th style="width: 10%">Priority</th>
                        <th style="width: 10%">Status</th>
                        <th style="width: 20%">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{high_concept_name}</td>
                        <td>{high_concept}</td>
                        <td><span class="badge bg-primary">{high_concept_priority}</span></td>
                        <td><span class="badge bg-secondary">{high_concept_status}</span></td>
                        <td>{high_concept_notes}</td>
                    </tr>
                    <tr>
                        <td>{target_audience_name}</td>
                        <td>{target_audience}</td>
                        <td><span class="badge bg-primary">{target_audience_priority}</span></td>
                        <td><span class="badge bg-secondary">{target_audience_status}</span></td>
                        <td>{target_audience_notes}</td>
                    </tr>
                    <tr>
                        <td>{unique_selling_points_name}</td>
                        <td>{unique_selling_points}</td>
                        <td><span class="badge bg-primary">{unique_selling_points_priority}</span></td>
                        <td><span class="badge bg-secondary">{unique_selling_points_status}</span></td>
                        <td>{unique_selling_points_notes}</td>
                    </tr>
                    {custom_features_html}
                </tbody>
            </table>
            
            {custom_section_html}
            {static_sections_html}
            {dynamic_sections_html}
            '''
            
            # Create the GDD with HTML content mode enabled
            gdd = GameDesignDocument.objects.create(
                game=game,
                high_concept=title,
                player_experience=description,
                core_mechanics="Core gameplay mechanics will be defined here",
                game_rules="Game rules will be defined here",
                controls="Controls will be defined here",
                html_content=html_content,
                use_html_content=True
            )
            
            # Create the Game Overview section
            overview_section = GDDSection.objects.create(
                gdd=gdd,
                title="Game Overview",
                section_id="game_overview",
                order=1,
                content="Provide a high-level overview of your game concept, target audience, and unique selling points."
            )
            
            # Get custom feature names from the form
            high_concept_name = request.POST.get('high_concept_name', 'High Concept')
            target_audience_name = request.POST.get('target_audience_name', 'Target Audience')
            unique_selling_points_name = request.POST.get('unique_selling_points_name', 'Unique Selling Points')
            
            # Create the initial features with data from the form including custom names
            # Create the initial features with data from the form including custom names
            # Avoid using status field directly as it's overridden by a property
            feature = GDDFeature(
                section=overview_section,
                subsection_id="high_concept",
                feature_name=high_concept_name,  # Use custom name
                description=high_concept or "A brief, one or two sentence description of the game.",
                priority=high_concept_priority,
                notes=high_concept_notes,
                order=1
            )
            feature.save()
            
            feature = GDDFeature(
                section=overview_section,
                subsection_id="target_audience",
                feature_name=target_audience_name,  # Use custom name
                description=target_audience or "The types of players the game is designed for (e.g., casual, hardcore, social, etc.).",
                priority=target_audience_priority,
                notes=target_audience_notes,
                order=2
            )
            feature.save()
            
            feature = GDDFeature(
                section=overview_section,
                subsection_id="unique_selling_points",
                feature_name=unique_selling_points_name,  # Use custom name
                description=unique_selling_points or "What makes this game unique compared to others in the same genre.",
                priority=unique_selling_points_priority,
                notes=unique_selling_points_notes,
                order=3
            )
            feature.save()
        
            # Create a custom section if a title was provided
            if section_title:
                # Create a section ID from the title (lowercase, replace spaces with underscores)
                section_id = section_title.lower().replace(' ', '_')
                
                # Create the custom section
                custom_section = GDDSection.objects.create(
                    gdd=gdd,
                    title=section_title,
                    section_id=section_id,
                    order=2,  # Place after the Game Overview section
                    content=additional_notes + ("\n" + bullet_points_html if bullet_points_html else "")
                )
                
                # If there are bullet points, create features for each one
                for i, point in enumerate(bullet_points, 1):
                    feature = GDDFeature(
                        section=custom_section,
                        subsection_id=f"{section_id}_point_{i}",
                        feature_name=f"Point {i}",
                        description=point,
                        priority="medium",
                        order=i
                    )
                    feature.save()
            
            # Process any dynamically added custom features
            custom_feature_prefix = 'custom_feature_'
            feature_order = 4  # Start after the three standard features
            
            # Find all custom feature fields in the POST data
            for key in request.POST.keys():
                # Look for keys like 'custom_feature_1', 'custom_feature_2', etc.
                if key.startswith(custom_feature_prefix) and not key.endswith('_name') and not key.endswith('_priority') and not key.endswith('_status') and not key.endswith('_notes'):
                    feature_id = key
                    
                    # Get the feature data
                    feature_name = request.POST.get(f"{feature_id}_name", "Custom Feature")
                    feature_desc = request.POST.get(feature_id, "")
                    feature_priority = request.POST.get(f"{feature_id}_priority", "medium")
                    feature_status = request.POST.get(f"{feature_id}_status", "backlog")
                    feature_notes = request.POST.get(f"{feature_id}_notes", "")
                    
                    # Create the feature - avoid using status property
                    feature = GDDFeature(
                        section=overview_section,
                        subsection_id=feature_id,
                        feature_name=feature_name,
                        description=feature_desc or "Custom feature description",
                        priority=feature_priority,
                        notes=feature_notes,
                        order=feature_order
                    )
                    feature.save()
                    
                    feature_order += 1
            
        messages.success(request, f"Simple GDD created successfully for {game.title}.")
        return redirect('games:gdd_detail', pk=gdd.id)

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
        
        # Create a form for the GDD
        form = GDDStructuredForm(initial={'game': game, 'high_concept': f"{game.title} - Game Design Document"})
        
        context = {
            'form': form,
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
                
                # Create features for this section based on the template and form data
                if section_id == 'game_overview':
                    # Game Overview section features
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
                    
                elif section_id == 'gameplay':
                    # Gameplay section features
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
                    
                    # Get form data for progression systems
                    progression_name = request.POST.get('progression_name', 'Progression Systems')
                    progression_desc = request.POST.get('progression', '')
                    progression_priority = request.POST.get('progression_priority', 'medium')
                    progression_status = request.POST.get('progression_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="progression",
                        feature_name=progression_name,
                        description=progression_desc or "How the player advances through the game.",
                        priority=progression_priority,
                        status=progression_status,
                        order=3
                    )
                    
                elif section_id == 'game_world':
                    # Game World section features
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
                    
                    # Get form data for level design
                    level_design_name = request.POST.get('level_design_name', 'Level Design')
                    level_design_desc = request.POST.get('level_design', '')
                    level_design_priority = request.POST.get('level_design_priority', 'high')
                    level_design_status = request.POST.get('level_design_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="level_design",
                        feature_name=level_design_name,
                        description=level_design_desc or "How levels are structured and what they contain.",
                        priority=level_design_priority,
                        status=level_design_status,
                        order=3
                    )
                    
                elif section_id == 'characters':
                    # Characters section features
                    # Get form data for player characters
                    player_characters_name = request.POST.get('player_characters_name', 'Player Characters')
                    player_characters_desc = request.POST.get('player_characters', '')
                    player_characters_priority = request.POST.get('player_characters_priority', 'high')
                    player_characters_status = request.POST.get('player_characters_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="player_characters",
                        feature_name=player_characters_name,
                        description=player_characters_desc or "Description of playable characters, their abilities, and progression.",
                        priority=player_characters_priority,
                        status=player_characters_status,
                        order=1
                    )
                    
                    # Get form data for NPCs
                    npcs_name = request.POST.get('npcs_name', 'NPCs')
                    npcs_desc = request.POST.get('npcs', '')
                    npcs_priority = request.POST.get('npcs_priority', 'medium')
                    npcs_status = request.POST.get('npcs_status', 'backlog')
                    
                    GDDFeature.objects.create(
                        section=gdd_section,
                        subsection_id="npcs",
                        feature_name=npcs_name,
                        description=npcs_desc or "Non-player characters and their roles in the game.",
                        priority=npcs_priority,
                        status=npcs_status,
                        order=2
                    )
                    
                else:
                    # For other sections, check if there are any feature name inputs
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
                        # Add a placeholder feature for other sections
                        GDDFeature.objects.create(
                            section=gdd_section,
                            feature_name=f"Add {section_title} features here",
                            description="Click to edit this placeholder feature",
                            priority="medium",
                            status="backlog",
                            order=1
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
