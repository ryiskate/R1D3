#!/usr/bin/env python
"""
Script to fix the missing redirect import in strategy/views.py
"""
import os
import sys
import re
from pathlib import Path

def fix_redirect_import(file_path):
    """Add the missing redirect import to the views file."""
    print(f"Fixing missing redirect import in: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup of the original file
    backup_path = file_path + '.bak_redirect'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Check if the redirect import already exists
    if "from django.shortcuts import redirect" in content:
        print("The redirect import already exists in the file.")
        
        # Check if there's a different import from django.shortcuts
        shortcuts_import = re.search(r'from django\.shortcuts import (.*)', content)
        if shortcuts_import:
            imports = shortcuts_import.group(1)
            if "redirect" not in imports:
                # Add redirect to the existing import
                new_imports = imports + ", redirect"
                new_content = content.replace(shortcuts_import.group(0), f"from django.shortcuts import {new_imports}")
                
                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print("Added redirect to the existing django.shortcuts import.")
                return True
            else:
                print("The redirect import is already included in django.shortcuts import.")
                return True
    else:
        # Add the import at the top of the file after other imports
        import_pattern = r'(from django\..*?\n)'
        last_import = list(re.finditer(import_pattern, content))[-1]
        
        new_content = content[:last_import.end()] + "from django.shortcuts import redirect\n" + content[last_import.end():]
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Added the missing redirect import.")
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
    
    if fix_redirect_import(file_path):
        print("\nFix applied successfully!")
        print("The missing redirect import has been added to the file.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the fix.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
