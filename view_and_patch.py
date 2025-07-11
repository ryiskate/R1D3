#!/usr/bin/env python
"""
Script to view and patch the StrategyMilestoneUpdateView in strategy/views.py
to fix the foreign key constraint error when updating milestones.
"""
import os
import sys
import re
from pathlib import Path

def view_milestone_update_view(file_path):
    """View the StrategyMilestoneUpdateView class in the file."""
    print(f"Viewing file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the StrategyMilestoneUpdateView class
    class_pattern = r'class StrategyMilestoneUpdateView\(.*?\):.*?(?=class|$)'
    class_match = re.search(class_pattern, content, re.DOTALL)
    
    if not class_match:
        print("Error: Could not find StrategyMilestoneUpdateView class in the file.")
        return False
    
    class_text = class_match.group(0)
    print("\nFound StrategyMilestoneUpdateView class:")
    print("-" * 80)
    print(class_text)
    print("-" * 80)
    
    # Look for the post method
    post_pattern = r'def post\(self, request, .*?\):(.*?)(?=def |$)'
    post_match = re.search(post_pattern, class_text, re.DOTALL)
    
    if post_match:
        post_text = post_match.group(0)
        print("\nFound post method:")
        print("-" * 80)
        print(post_text)
        print("-" * 80)
    else:
        print("\nCould not find post method in the class.")
        
        # Look for any method that might be handling milestone status updates
        status_update_pattern = r'def .*?\(.*?\):(.*?status.*?in_progress.*?)(?=def |$)'
        status_match = re.search(status_update_pattern, class_text, re.DOTALL)
        
        if status_match:
            status_text = status_match.group(0)
            print("\nFound method with status update logic:")
            print("-" * 80)
            print(status_text)
            print("-" * 80)
    
    return True

def create_direct_sql_patch(file_path):
    """Create a direct SQL patch for the milestone update view."""
    print(f"\nCreating direct SQL patch for: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup of the original file
    backup_path = file_path + '.bak2'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Find the pattern for updating other milestones
    update_pattern = r'(if status == [\'"]in_progress[\'"] and milestone\.status != [\'"]in_progress[\'"]:\s+)(# Set all other in-progress milestones to not_started\s+in_progress_milestones = StrategyMilestone\.objects\.filter\(status=[\'"]in_progress[\'"]\)\.exclude\(id=milestone_id\)\s+for other_milestone in in_progress_milestones:\s+other_milestone\.status = [\'"]not_started[\'"]\s+other_milestone\.save\(\))'
    
    # Create the replacement code
    replacement = r'\1# Set all other in-progress milestones to not_started using direct SQL\n            from django.db import connection\n            \n            # Use raw SQL to bypass foreign key constraints\n            with connection.cursor() as cursor:\n                # Temporarily disable foreign key constraints\n                cursor.execute("PRAGMA foreign_keys = OFF;")\n                \n                # Update all other in-progress milestones directly\n                cursor.execute("""\n                    UPDATE strategy_strategymilestone \n                    SET status = \'not_started\', updated_at = datetime(\'now\') \n                    WHERE status = \'in_progress\' AND id != %s;\n                """, [milestone_id])\n                \n                # Re-enable foreign key constraints\n                cursor.execute("PRAGMA foreign_keys = ON;")\n                \n            # Add info message\n            messages.info(request, "Other in-progress milestones were changed to \'Not Started\'")'
    
    # Replace the pattern in the content
    new_content = re.sub(update_pattern, replacement, content)
    
    if new_content == content:
        print("Error: Could not find the pattern to replace.")
        
        # Try a more general pattern
        general_pattern = r'(if status == [\'"]in_progress[\'"] and milestone\.status != [\'"]in_progress[\'"]:[^\n]*\n[^\n]*)(in_progress_milestones = StrategyMilestone\.objects\.filter\(status=[\'"]in_progress[\'"]\)[^\n]*\n[^\n]*for other_milestone in in_progress_milestones:[^\n]*\n[^\n]*other_milestone\.status = [\'"]not_started[\'"]\n[^\n]*other_milestone\.save\(\))'
        
        new_content = re.sub(general_pattern, replacement, content)
        
        if new_content == content:
            print("Error: Could not find the pattern to replace with the general pattern.")
            
            # Try an even more general approach
            print("\nTrying a manual approach...")
            
            # Look for the StrategyMilestoneUpdateView class
            class_pattern = r'class StrategyMilestoneUpdateView\(.*?\):.*?(?=class|$)'
            class_match = re.search(class_pattern, content, re.DOTALL)
            
            if not class_match:
                print("Error: Could not find StrategyMilestoneUpdateView class.")
                return False
            
            class_text = class_match.group(0)
            
            # Look for the in_progress milestone update code
            update_code = r'in_progress_milestones = StrategyMilestone\.objects\.filter\(status=\'in_progress\'\)\.exclude\(id=milestone_id\)'
            
            if update_code in class_text:
                print("Found the update code. Creating a manual patch...")
                
                # Create the manual patch
                manual_patch = """
            # Use direct SQL to bypass foreign key constraints
            from django.db import connection
            with connection.cursor() as cursor:
                # Temporarily disable foreign key constraints
                cursor.execute("PRAGMA foreign_keys = OFF;")
                
                # Update all other in-progress milestones directly
                cursor.execute('''
                    UPDATE strategy_strategymilestone 
                    SET status = 'not_started', updated_at = datetime('now') 
                    WHERE status = 'in_progress' AND id != %s;
                ''', [milestone_id])
                
                # Re-enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys = ON;")
                
            # Add info message
            messages.info(request, "Other in-progress milestones were changed to 'Not Started'")
"""
                
                # Replace the update code and the following lines
                new_class_text = class_text.replace(update_code, manual_patch)
                
                # Remove the for loop that updates individual milestones
                for_loop_pattern = r'for other_milestone in in_progress_milestones:.*?other_milestone\.save\(\)'
                new_class_text = re.sub(for_loop_pattern, '', new_class_text, flags=re.DOTALL)
                
                # Replace the class in the content
                new_content = content.replace(class_text, new_class_text)
                
                if new_content == content:
                    print("Error: Could not replace the class text.")
                    return False
            else:
                print("Error: Could not find the update code in the class.")
                return False
    
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
    
    print(f"Processing strategy views file at: {file_path}")
    
    # First, view the milestone update view
    if not view_milestone_update_view(file_path):
        print("Failed to view the milestone update view.")
        return
    
    # Ask the user if they want to proceed with the patch
    response = input("\nDo you want to proceed with patching the file? (y/n): ")
    
    if response.lower() == 'y':
        if create_direct_sql_patch(file_path):
            print("\nPatch applied successfully!")
            print("The milestone update view has been modified to use direct SQL with foreign key checks disabled.")
            print("\nYou should now be able to update milestones without issues.")
        else:
            print("\nFailed to apply the patch.")
            print("Please check the error messages above and try again.")
    else:
        print("\nPatch operation cancelled.")

if __name__ == "__main__":
    main()
