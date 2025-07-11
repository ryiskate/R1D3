#!/usr/bin/env python
"""
Script to restore the original views.py file from a backup and apply a minimal fix
to add the missing redirect import.
"""
import os
import sys
import glob
import re

def restore_and_fix_views(file_path):
    """Restore the original views.py file and add the missing import."""
    print(f"Restoring and fixing views file: {file_path}")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Find the most recent backup file
    backup_dir = os.path.dirname(file_path)
    backup_files = glob.glob(os.path.join(backup_dir, "views.py.bak*"))
    
    if not backup_files:
        print("No backup files found. Creating a new backup before proceeding.")
        # Create a backup of the current file
        backup_path = file_path + '.bak_before_restore'
        try:
            with open(file_path, 'r', encoding='utf-8') as f_in:
                with open(backup_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
            print(f"Created backup at: {backup_path}")
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    else:
        # Sort backup files by modification time (newest first)
        backup_files.sort(key=os.path.getmtime, reverse=True)
        print(f"Found {len(backup_files)} backup files. Using the most recent one: {backup_files[0]}")
        
        # Restore from the most recent backup
        try:
            with open(backup_files[0], 'r', encoding='utf-8') as f_in:
                original_content = f_in.read()
                
            # Create a new backup of the current file before restoring
            backup_path = file_path + '.bak_before_restore'
            with open(backup_path, 'w', encoding='utf-8') as f_out:
                with open(file_path, 'r', encoding='utf-8') as f_current:
                    f_out.write(f_current.read())
            print(f"Created backup of current file at: {backup_path}")
            
            # Write the original content back to the file
            with open(file_path, 'w', encoding='utf-8') as f_out:
                f_out.write(original_content)
            print(f"Restored original content from: {backup_files[0]}")
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
    
    # Now add the missing import at the top of the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the redirect import already exists
        if 'from django.shortcuts import redirect' in content:
            print("The 'redirect' import is already in the file.")
        else:
            # Find the best place to add the import
            # Look for other django.shortcuts imports first
            shortcuts_pattern = r'from django\.shortcuts import .*'
            shortcuts_match = re.search(shortcuts_pattern, content)
            
            if shortcuts_match:
                # Add redirect to existing django.shortcuts import
                old_import = shortcuts_match.group(0)
                if old_import.endswith(','):
                    new_import = old_import + ' redirect'
                else:
                    new_import = old_import + ', redirect'
                content = content.replace(old_import, new_import)
                print(f"Added 'redirect' to existing django.shortcuts import: {new_import}")
            else:
                # Add a new import line at the top of the file
                # Find the first import statement
                first_import = content.find('import')
                if first_import >= 0:
                    # Insert before the first import
                    content = content[:first_import] + 'from django.shortcuts import redirect\n\n' + content[first_import:]
                else:
                    # No imports found, add at the very top
                    content = 'from django.shortcuts import redirect\n\n' + content
                print("Added 'from django.shortcuts import redirect' at the top of the file.")
            
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return True
    except Exception as e:
        print(f"Error adding import: {e}")
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
    
    if restore_and_fix_views(file_path):
        print("\nFix applied successfully!")
        print("The views.py file has been restored from backup and the missing import has been added.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the fix.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
