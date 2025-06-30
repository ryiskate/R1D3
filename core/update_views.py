"""
Script to update the core views with the improved implementations.
Run this script to replace the existing views with the updated versions.
"""
import os
import shutil
from datetime import datetime

# Define the paths
base_dir = os.path.dirname(os.path.abspath(__file__))
views_path = os.path.join(base_dir, 'views.py')
legacy_views_path = os.path.join(base_dir, 'legacy_views.py')
updated_views_path = os.path.join(base_dir, 'updated_views.py')
updated_legacy_views_path = os.path.join(base_dir, 'updated_legacy_views.py')
updated_global_task_dashboard_path = os.path.join(base_dir, 'updated_global_task_dashboard.py')

# Create backup of the original files
backup_dir = os.path.join(base_dir, 'backups')
os.makedirs(backup_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
views_backup = os.path.join(backup_dir, f'views_{timestamp}.py.bak')
legacy_views_backup = os.path.join(backup_dir, f'legacy_views_{timestamp}.py.bak')

# Backup the original files
if os.path.exists(views_path):
    shutil.copy2(views_path, views_backup)
    print(f"Backed up views.py to {views_backup}")

if os.path.exists(legacy_views_path):
    shutil.copy2(legacy_views_path, legacy_views_backup)
    print(f"Backed up legacy_views.py to {legacy_views_backup}")

# Read the existing views.py file
with open(views_path, 'r', encoding='utf-8') as f:
    views_content = f.read()

# Read the updated files
with open(updated_views_path, 'r', encoding='utf-8') as f:
    updated_views_content = f.read()

with open(updated_legacy_views_path, 'r', encoding='utf-8') as f:
    updated_legacy_views_content = f.read()

with open(updated_global_task_dashboard_path, 'r', encoding='utf-8') as f:
    updated_global_task_dashboard_content = f.read()

# Replace the R1D3TaskUpdateView, R1D3TaskDeleteView, and R1D3TaskDetailView classes in views.py
import re

# Function to replace a class in the views.py file
def replace_class(content, class_name, new_content):
    pattern = rf'class {class_name}\(.*?\):(.*?)(?=\n\n\nclass|\Z)'
    replacement = f'class {class_name}(.*?):{new_content}'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

# Replace the task views
views_content = replace_class(views_content, 'R1D3TaskUpdateView', updated_views_content)
views_content = replace_class(views_content, 'R1D3TaskDeleteView', updated_views_content)
views_content = replace_class(views_content, 'R1D3TaskDetailView', updated_views_content)
views_content = replace_class(views_content, 'GlobalTaskDashboardView', updated_global_task_dashboard_content)

# Update the legacy_views.py file
with open(legacy_views_path, 'w', encoding='utf-8') as f:
    f.write(updated_legacy_views_content)
    print(f"Updated {legacy_views_path}")

# Write the updated views.py file
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)
    print(f"Updated {views_path}")

print("Views update completed successfully!")
