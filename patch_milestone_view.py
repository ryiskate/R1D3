#!/usr/bin/env python
"""
Script to directly patch the StrategyMilestoneUpdateView in strategy/views.py
to fix the foreign key constraint error when updating milestones.
"""
import os
import sys
import re
from pathlib import Path

def patch_views_file(file_path):
    """Patch the strategy/views.py file to fix the foreign key constraint error."""
    print(f"Attempting to patch file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the pattern to find the problematic code block
    pattern = r"""(\s+# Check if we're setting this milestone to in_progress
\s+if status == 'in_progress' and milestone\.status != 'in_progress':
\s+# Set all other in-progress milestones to not_started
\s+in_progress_milestones = StrategyMilestone\.objects\.filter\(status='in_progress'\)\.exclude\(id=milestone_id\)
\s+for other_milestone in in_progress_milestones:
\s+other_milestone\.status = 'not_started'
\s+other_milestone\.save\(\)
\s+messages\.info\(request, f"Milestone '[^']+' was changed from 'In Progress' to 'Not Started'"\))"""
    
    # Define the replacement code with transaction.atomic()
    replacement = r"""        # Check if we're setting this milestone to in_progress
        if status == 'in_progress' and milestone.status != 'in_progress':
            # Set all other in-progress milestones to not_started
            from django.db import transaction
            
            # Use transaction.atomic() to ensure database integrity
            with transaction.atomic():
                # First update all other milestones directly in the database
                StrategyMilestone.objects.filter(status='in_progress').exclude(id=milestone_id).update(
                    status='not_started'
                )
                
                # Add info message
                messages.info(request, f"Other in-progress milestones were changed to 'Not Started'")"""
    
    # Check if the pattern exists in the content
    if not re.search(pattern, content):
        print("Error: Could not find the target code block to replace.")
        print("The file structure might have changed. Manual intervention required.")
        return False
    
    # Replace the pattern with the new code
    new_content = re.sub(pattern, replacement, content)
    
    # Create a backup of the original file
    backup_path = file_path + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully patched {file_path}")
    return True

def main():
    """Main function to run the script."""
    # Check if a file path was provided as an argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default path for local development
        file_path = os.path.join('strategy', 'views.py')
        
        # Check if we're in the project root
        if not os.path.exists(file_path):
            # Try to find the file in the current directory structure
            for root, _, files in os.walk('.'):
                if 'views.py' in files and 'strategy' in root:
                    potential_path = os.path.join(root, 'views.py')
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        break
    
    # Ensure the file path is absolute
    file_path = os.path.abspath(file_path)
    
    print(f"Patching strategy views file at: {file_path}")
    
    if patch_views_file(file_path):
        print("\nPatch applied successfully!")
        print("The milestone update view has been modified to use transaction.atomic()")
        print("and direct database updates to avoid foreign key constraint errors.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the patch.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
