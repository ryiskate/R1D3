#!/usr/bin/env python
"""
Script to directly fix the StrategyMilestoneUpdateView.post method in strategy/views.py
by replacing the redirect call with an alternative approach.
"""
import os
import sys
import re

def fix_view_directly(file_path):
    """Fix the view by directly modifying the post method."""
    print(f"Directly fixing view in: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup of the original file
    backup_path = file_path + '.bak_direct_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Find line 556 where the error is occurring
    lines = content.split('\n')
    
    if len(lines) < 556:
        print(f"Error: File has fewer than 556 lines (only {len(lines)} lines).")
        return False
    
    # Print the problematic lines for context
    print("\nProblematic lines around line 556:")
    for i in range(max(0, 556-5), min(len(lines), 556+5)):
        print(f"{i+1}: {lines[i]}")
    
    # Find the StrategyMilestoneUpdateView class
    class_pattern = r'class StrategyMilestoneUpdateView\(.*?\):'
    class_match = re.search(class_pattern, content)
    
    if not class_match:
        print("Error: Could not find StrategyMilestoneUpdateView class in the file.")
        return False
    
    class_start = class_match.start()
    
    # Find the post method within the class
    post_pattern = r'def post\(self, request, \*args, \*\*kwargs\):'
    post_matches = list(re.finditer(post_pattern, content[class_start:]))
    
    if not post_matches:
        print("Error: Could not find post method in StrategyMilestoneUpdateView class.")
        return False
    
    post_start = class_start + post_matches[0].start()
    
    # Find the end of the post method (next def or end of file)
    next_def = content.find('def ', post_start + 10)
    if next_def == -1:
        post_end = len(content)
    else:
        post_end = next_def
    
    post_method = content[post_start:post_end]
    
    # Check if 'redirect' is used in the post method
    if 'redirect' in post_method:
        print("\nFound 'redirect' in the post method. Replacing with HttpResponseRedirect...")
        
        # Add the HttpResponseRedirect import at the top of the file
        if 'from django.http import HttpResponseRedirect' not in content:
            import_line = 'from django.http import HttpResponseRedirect\n'
            # Find a good place to add the import (after other imports)
            import_end = content.find('\n\n', content.find('import'))
            if import_end == -1:
                import_end = content.find('\n', content.find('import'))
            
            new_content = content[:import_end] + '\n' + import_line + content[import_end:]
        else:
            new_content = content
        
        # Replace redirect with HttpResponseRedirect in the post method
        new_post_method = post_method.replace('redirect(', 'HttpResponseRedirect(')
        new_content = new_content.replace(post_method, new_post_method)
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Successfully replaced 'redirect' with 'HttpResponseRedirect' in the post method.")
        return True
    else:
        # If we can't find 'redirect' in the post method, we need to look at line 556 specifically
        print("\nCould not find 'redirect' in the post method. Looking at line 556 specifically...")
        
        # Get line 556 (0-indexed is 555)
        line_556 = lines[555] if len(lines) > 555 else ""
        print(f"Line 556: {line_556}")
        
        # Check if line 556 contains 'redirect'
        if 'redirect' in line_556:
            # Add the HttpResponseRedirect import at the top of the file
            if 'from django.http import HttpResponseRedirect' not in content:
                import_line = 'from django.http import HttpResponseRedirect\n'
                # Find a good place to add the import (after other imports)
                import_end = content.find('\n\n', content.find('import'))
                if import_end == -1:
                    import_end = content.find('\n', content.find('import'))
                
                new_content = content[:import_end] + '\n' + import_line + content[import_end:]
            else:
                new_content = content
            
            # Replace redirect with HttpResponseRedirect in line 556
            lines[555] = lines[555].replace('redirect(', 'HttpResponseRedirect(')
            new_content = '\n'.join(lines)
            
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Successfully replaced 'redirect' with 'HttpResponseRedirect' in line 556.")
            return True
        else:
            # If we still can't find 'redirect', let's try a more direct approach
            print("\nCould not find 'redirect' in line 556. Trying a more direct approach...")
            
            # Add both imports at the top of the file
            if 'from django.shortcuts import redirect' not in content:
                import_line = 'from django.shortcuts import redirect\n'
                # Find a good place to add the import (after other imports)
                import_end = content.find('\n\n', content.find('import'))
                if import_end == -1:
                    import_end = content.find('\n', content.find('import'))
                
                new_content = content[:import_end] + '\n' + import_line + content[import_end:]
                
                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("Added 'from django.shortcuts import redirect' import at the top of the file.")
                return True
            else:
                print("The 'redirect' import is already in the file, but there might be an indentation or scope issue.")
                return False

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
    
    if fix_view_directly(file_path):
        print("\nFix applied successfully!")
        print("The view has been modified to use HttpResponseRedirect instead of redirect.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the fix.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
