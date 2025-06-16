import re

# Read the file
with open('projects/gdd_structured_views.py', 'r') as f:
    content = f.read()

# Fix the redirect in GDDStructuredEditView
content = content.replace(
    "return redirect('gdd_structured_create', game_id=game_id)",
    "return redirect('games:gdd_structured_create', game_id=game_id)"
)

# Write the changes back to the file
with open('projects/gdd_structured_views.py', 'w') as f:
    f.write(content)

print("URL fixes applied successfully")
