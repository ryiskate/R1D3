from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

from .models import GameProject, GameDesignDocument, GDDSection, GDDFeature
from .forms import GDDStructuredForm, GDDSectionForm, GDDFeatureForm

# Standard GDD sections with their order and subsections
STANDARD_GDD_SECTIONS = [
    {
        'title': 'Game Overview',
        'section_id': 'game_overview',
        'order': 1,
        'subsections': [
            {'title': 'High Concept', 'subsection_id': 'high_concept'},
            {'title': 'Target Audience', 'subsection_id': 'target_audience'},
            {'title': 'Unique Selling Points', 'subsection_id': 'unique_selling_points'},
            {'title': 'Platforms', 'subsection_id': 'platforms'}
        ]
    },
    # Other sections omitted for brevity
]

def prepare_structured_gdd_sections():
    """
    Prepare section formsets based on the standard GDD sections
    """
    section_formsets = []
    for section in STANDARD_GDD_SECTIONS:
        section_formsets.append({
            'title': section['title'],
            'section_id': section['section_id'],
            'order': section['order'],
            'subsections': section.get('subsections', [])
        })
    return section_formsets

class GDDSimpleCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for creating a simple Game Design Document with a basic overview section
    and three initial features
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
            # Redirect to the GDD detail page
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
        
        # Create the GDD with the correct fields from the model
        with transaction.atomic():
            gdd = GameDesignDocument.objects.create(
                game=game,
                high_concept=f"{game.title} - Game Design Document",
                player_experience="What the player will experience playing this game",
                core_mechanics="Core gameplay mechanics will be defined here",
                game_rules="Game rules will be defined here",
                controls="Controls will be defined here"
            )
            
            # Create Game Overview section
            overview_section = GDDSection.objects.create(
                gdd=gdd,
                title="Game Overview",
                section_id="game_overview",
                order=1,
                content=""
            )
            
            # Create three initial features
            GDDFeature.objects.create(
                section=overview_section,
                subsection_id="high_concept",
                feature_name="High Concept",
                description="A brief, one or two sentence description of the game.",
                priority="critical",
                status="backlog",
                order=1
            )
            
            GDDFeature.objects.create(
                section=overview_section,
                subsection_id="target_audience",
                feature_name="Target Audience",
                description="The types of players the game is designed for (e.g., casual, hardcore, social, etc.).",
                priority="medium",
                status="to_do",
                order=2
            )
            
            GDDFeature.objects.create(
                section=overview_section,
                subsection_id="unique_selling_points",
                feature_name="Unique Selling Points",
                description="What makes this game unique compared to others in the same genre.",
                priority="high",
                status="in_progress",
                order=3
            )
        
        messages.success(request, f"Simple GDD created successfully for {game.title}.")
        return redirect('games:gdd_detail', pk=gdd.id)

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
        
        return render(request, 'projects/gdd_structured_create.html', context)
    
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
                section_title = section['title']
                section_order = section['order']
                
                # Create the section
                gdd_section = GDDSection.objects.create(
                    gdd=gdd,
                    title=section_title,
                    section_id=section_id,
                    order=section_order,
                    content=''
                )
                
                # Process features for this section if provided
                if 'subsections' in section:
                    for subsection in section['subsections']:
                        subsection_id = subsection['subsection_id']
                        feature_name = request.POST.get(f"feature_{section_id}_{subsection_id}", "")
                        description = request.POST.get(f"description_{section_id}_{subsection_id}", "")
                        priority = request.POST.get(f"priority_{section_id}_{subsection_id}", "medium")
                        
                        if feature_name:  # Only create if a feature name was provided
                            GDDFeature.objects.create(
                                section=gdd_section,
                                subsection_id=subsection_id,
                                feature_name=feature_name,
                                description=description,
                                priority=priority,
                                order=0
                            )
            
            messages.success(request, f"GDD created successfully for {game.title}.")
            return redirect('games:gdd_detail', pk=gdd.id)
        else:
            messages.error(request, "There was an error creating the GDD. Please check the form.")
            
            # Re-initialize section formsets
            section_formsets = prepare_structured_gdd_sections()
            
            context = {
                'form': form,
                'game': game,
                'section_formsets': section_formsets,
                'standard_sections': STANDARD_GDD_SECTIONS
            }
            
            return render(request, 'projects/gdd_structured_create.html', context)

class GDDStructuredEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for editing a Game Design Document using a structured form approach
    """
    def test_func(self):
        gdd_id = self.kwargs.get('pk')
        gdd = get_object_or_404(GameDesignDocument, id=gdd_id)
        game = gdd.game
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        # Implementation for GET request
        pass
    
    def post(self, request, *args, **kwargs):
        # Implementation for POST request
        pass

class GDDSectionFeatureView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for managing features within a GDD section
    """
    def test_func(self):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def get(self, request, *args, **kwargs):
        # Implementation for GET request
        pass
    
    def post(self, request, *args, **kwargs):
        # Implementation for POST request
        pass

class UpdateFeatureOrderView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for updating the order of features within a section
    """
    def test_func(self):
        game_id = self.kwargs.get('game_id')
        game = get_object_or_404(GameProject, id=game_id)
        return self.request.user.is_staff or self.request.user == game.lead_developer or self.request.user == game.lead_designer
    
    def post(self, request, *args, **kwargs):
        # Implementation for POST request
        pass
