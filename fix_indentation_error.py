#!/usr/bin/env python
"""
Script to fix the indentation error in the StrategyMilestoneUpdateView post method.
"""
import os
import sys
import re

def fix_indentation_error(file_path):
    """Fix the indentation error in the post method."""
    print(f"Fixing indentation error in: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup of the original file
    backup_path = file_path + '.bak_indent_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Make sure HttpResponseRedirect is imported
    if 'from django.http import HttpResponseRedirect' not in content:
        # Find a good place to add the import (after other imports)
        import_end = content.find('\n\n', content.find('import'))
        if import_end == -1:
            import_end = content.find('\n', content.find('import'))
        
        content = content[:import_end] + '\nfrom django.http import HttpResponseRedirect' + content[import_end:]
    
    # Find the StrategyMilestoneUpdateView class
    class_pattern = r'class StrategyMilestoneUpdateView\(.*?\):'
    class_match = re.search(class_pattern, content)
    
    if not class_match:
        print("Error: Could not find StrategyMilestoneUpdateView class in the file.")
        return False
    
    # The complete new post method with proper indentation
    new_post_method = """    def post(self, request, *args, **kwargs):
        # Get the milestone and form
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            # Get the milestone and status
            milestone_id = self.kwargs.get('milestone_id')
            milestone = self.get_object()
            status = form.cleaned_data.get('status')
            
            # If setting to in_progress, update other milestones using direct SQL
            if status == 'in_progress' and milestone.status != 'in_progress':
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
                from django.contrib import messages
                messages.info(request, "Other in-progress milestones were changed to 'Not Started'")
            
            # Save the form
            self.object = form.save()
            
            # Show success message
            from django.contrib import messages
            messages.success(self.request, f"Milestone '{self.object.title}' updated successfully.")
            
            # Mark the session as modified
            self.request.session.modified = True
            
            # Redirect to the milestone list
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)"""
    
    # Find the post method within the class
    post_pattern = r'def post\(self, request, \*args, \*\*kwargs\):'
    class_content = content[class_match.start():]
    post_match = re.search(post_pattern, class_content)
    
    if not post_match:
        print("Error: Could not find post method in StrategyMilestoneUpdateView class.")
        return False
    
    post_start = class_match.start() + post_match.start()
    
    # Find the end of the post method (next def or end of class)
    content_after_post = content[post_start:]
    next_def = content_after_post.find('\n    def ', 10)
    if next_def == -1:
        # Try to find the end of the class (next class definition or end of file)
        next_class = content_after_post.find('\nclass ', 10)
        if next_class == -1:
            post_end = post_start + len(content_after_post)
        else:
            post_end = post_start + next_class
    else:
        post_end = post_start + next_def
    
    # Replace the old post method with the new one
    new_content = content[:post_start] + new_post_method + content[post_end:]
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Successfully fixed the indentation error in the post method.")
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
    
    if fix_indentation_error(file_path):
        print("\nFix applied successfully!")
        print("The indentation error in the post method has been fixed.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the fix.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
