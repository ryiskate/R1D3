#!/usr/bin/env python
"""
Script to completely restore the original views.py file from a backup
and then add the import at the very top without modifying anything else.
"""
import os
import sys
import glob
import shutil

def restore_original_views(file_path):
    """Restore the original views.py file and add the import at the very top."""
    print(f"Restoring original views file: {file_path}")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    # Find the most recent backup file
    backup_dir = os.path.dirname(file_path)
    backup_files = glob.glob(os.path.join(backup_dir, "views.py.bak*"))
    
    if not backup_files:
        print("No backup files found. Cannot restore original file.")
        return False
    
    # Sort backup files by modification time (newest first)
    backup_files.sort(key=os.path.getmtime, reverse=True)
    print(f"Found {len(backup_files)} backup files. Using the most recent one: {backup_files[0]}")
    
    # Create a new backup of the current file before restoring
    backup_path = file_path + '.bak_before_final_restore'
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Created backup of current file at: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    # Restore from the most recent backup
    try:
        shutil.copy2(backup_files[0], file_path)
        print(f"Restored original content from: {backup_files[0]}")
    except Exception as e:
        print(f"Error restoring from backup: {e}")
        return False
    
    # Now add the import at the very top of the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add the import at the very top
        new_content = 'from django.shortcuts import redirect\n\n' + content
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Added 'from django.shortcuts import redirect' at the very top of the file.")
        return True
    except Exception as e:
        print(f"Error adding import: {e}")
        # If there's an error, try to restore from the backup we just created
        try:
            shutil.copy2(backup_path, file_path)
            print(f"Restored from backup after error: {backup_path}")
        except Exception as restore_error:
            print(f"Error restoring from backup after error: {restore_error}")
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
    
    if restore_original_views(file_path):
        print("\nFix applied successfully!")
        print("The views.py file has been restored from backup and the import has been added at the top.")
        print("\nYou should now be able to update milestones without issues.")
    else:
        print("\nFailed to apply the fix.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
