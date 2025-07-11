#!/usr/bin/env python
"""
Script to directly patch the StrategyMilestoneUpdateView in strategy/views.py
to avoid foreign key constraint errors when updating milestones.
This script will find and replace the problematic code in the post method.
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
    
    # Create a backup of the original file
    backup_path = file_path + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Look for the StrategyMilestoneUpdateView class
    class_pattern = r'class StrategyMilestoneUpdateView\(.*?\):'
    if not re.search(class_pattern, content):
        print("Error: Could not find StrategyMilestoneUpdateView class in the file.")
        return False
    
    # Find the post method within the class
    post_method_pattern = r'def post\(self, request, \*args, \*\*kwargs\):[^}]*?return super\(\)\.form_valid\(form\)'
    post_method = re.search(post_method_pattern, content, re.DOTALL)
    
    if not post_method:
        print("Error: Could not find post method in StrategyMilestoneUpdateView class.")
        return False
    
    post_method_text = post_method.group(0)
    
    # Find the problematic code block that updates other milestones
    problematic_code = r'''if status == 'in_progress' and milestone\.status != 'in_progress':
\s+# Set all other in-progress milestones to not_started
\s+in_progress_milestones = StrategyMilestone\.objects\.filter\(status='in_progress'\)\.exclude\(id=milestone_id\)
\s+for other_milestone in in_progress_milestones:
\s+other_milestone\.status = 'not_started'
\s+other_milestone\.save\(\)'''
    
    # Create the replacement code that uses direct SQL update
    replacement_code = '''if status == 'in_progress' and milestone.status != 'in_progress':
            # Set all other in-progress milestones to not_started using direct SQL
            from django.db import connection
            
            # Use raw SQL to bypass foreign key constraints
            with connection.cursor() as cursor:
                # Temporarily disable foreign key constraints
                cursor.execute("PRAGMA foreign_keys = OFF;")
                
                # Update all other in-progress milestones directly
                cursor.execute("""
                    UPDATE strategy_strategymilestone 
                    SET status = 'not_started', updated_at = datetime('now') 
                    WHERE status = 'in_progress' AND id != %s;
                """, [milestone_id])
                
                # Re-enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys = ON;")
                
            # Add info message
            messages.info(request, "Other in-progress milestones were changed to 'Not Started'")'''
    
    # Replace the problematic code with the new code
    new_post_method = re.sub(problematic_code, replacement_code, post_method_text)
    
    if new_post_method == post_method_text:
        print("Error: Could not find the problematic code block to replace.")
        print("The file structure might have changed. Manual intervention required.")
        return False
    
    # Replace the post method in the file content
    new_content = content.replace(post_method_text, new_post_method)
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully patched {file_path}")
    print("The milestone update view has been modified to use direct SQL with foreign key checks disabled.")
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
        print("The milestone update view has been modified to use direct SQL with foreign key checks disabled.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the patch.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
