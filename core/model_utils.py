"""
Utility functions for working with task models in the R1D3 platform.
"""

def get_task_model_map():
    """
    Returns a mapping of task_type strings to their corresponding model classes.
    This ensures consistency across all views that need to map task types to models.
    """
    # Import task models here to avoid circular imports
    from projects.task_models import (
        R1D3Task, GameDevelopmentTask, EducationTask,
        SocialMediaTask, ArcadeTask, ThemeParkTask
    )
    
    return {
        'r1d3': R1D3Task,
        'game_development': GameDevelopmentTask,
        'education': EducationTask,
        'social_media': SocialMediaTask,
        'arcade': ArcadeTask,
        'theme_park': ThemeParkTask,
    }

def get_task_type_for_model(model_instance):
    """
    Returns the task_type string for a given task model instance.
    """
    model_name = model_instance.__class__.__name__
    
    model_to_type = {
        'R1D3Task': 'r1d3',
        'GameDevelopmentTask': 'game_development',
        'EducationTask': 'education',
        'SocialMediaTask': 'social_media',
        'ArcadeTask': 'arcade',
        'ThemeParkTask': 'theme_park',
    }
    
    return model_to_type.get(model_name, 'r1d3')  # Default to r1d3 if not found
