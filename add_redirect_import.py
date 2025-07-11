#!/usr/bin/env python
"""
Script to directly add the missing redirect import to strategy/views.py
"""
import os
import sys

def add_redirect_import(file_path):
    """Add the missing redirect import to the views file."""
    print(f"Adding redirect import to: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Read the current file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup of the original file
    backup_path = file_path + '.bak_direct'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup of original file at: {backup_path}")
    
    # Add the import at the very top of the file
    new_content = "from django.shortcuts import redirect\n" + content
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Added the missing redirect import at the top of the file.")
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
    
    if add_redirect_import(file_path):
        print("\nFix applied successfully!")
        print("The missing redirect import has been added to the file.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the fix.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
