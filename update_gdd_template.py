"""
Script to update the existing GDD in the database with the modified template.
This will read the updated template file and update the GDD for game_id=2.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models
from projects.game_models import GameDesignDocument, GameProject

def update_gdd_with_template():
    try:
        # Get the GDD for game_id=1
        game_id = 1
        gdd = GameDesignDocument.objects.get(game_id=game_id)
        game = GameProject.objects.get(id=game_id)
        
        print(f"Found GDD for game: {game.title} (ID: {game_id})")
        
        # Read the updated template file
        template_path = os.path.join('static', 'templates', 'gdd_template.html')
        with open(template_path, 'r', encoding='utf-8') as file:
            updated_template = file.read()
        
        # Update the GDD with the new template
        gdd.html_content = updated_template
        gdd.use_html_content = True
        gdd.save()
        
        print(f"Successfully updated GDD with the modified template!")
        print(f"The GDD now includes task management columns in all feature tables.")
        
    except GameDesignDocument.DoesNotExist:
        print(f"No GDD found for game_id={game_id}")
    except Exception as e:
        print(f"Error updating GDD: {str(e)}")

if __name__ == "__main__":
    update_gdd_with_template()
