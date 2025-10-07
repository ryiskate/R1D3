#!/usr/bin/env python
"""
Script to help find your project directory on PythonAnywhere.
This script:
1. Searches common locations for your project
2. Checks for Django project markers
3. Prints the path if found
"""
import os
import sys

def find_project_directory():
    """Find the R1D3 project directory on PythonAnywhere."""
    print("Searching for R1D3 project directory...")
    
    # Common locations to check
    possible_locations = [
        '/home',  # Root home directory
        '/var/www',  # Web directory
        os.path.expanduser('~'),  # User's home directory
    ]
    
    # Project markers to identify Django project
    project_markers = [
        'manage.py',
        'company_system/settings.py',
        'company_system/urls.py',
    ]
    
    for base_location in possible_locations:
        print(f"\nSearching in {base_location}...")
        
        if not os.path.exists(base_location):
            print(f"  {base_location} does not exist, skipping.")
            continue
            
        # Walk through directories
        for root, dirs, files in os.walk(base_location):
            # Skip virtual environments and other common non-project directories
            if any(skip_dir in root for skip_dir in ['/venv/', '/.git/', '/__pycache__/', '/node_modules/']):
                continue
                
            # Check if this directory has project markers
            has_markers = any(os.path.exists(os.path.join(root, marker)) for marker in project_markers)
            
            if has_markers:
                print(f"\nPotential Django project found at: {root}")
                print("Project markers found:")
                for marker in project_markers:
                    marker_path = os.path.join(root, marker)
                    if os.path.exists(marker_path):
                        print(f"  ✓ {marker}")
                    else:
                        print(f"  ✗ {marker}")
                        
                print("\nTo navigate to this directory:")
                print(f"cd {root}")
                print("\nTo check if it's a git repository:")
                print(f"cd {root} && git status")
                
                return root
    
    print("\nNo Django project directory found in common locations.")
    print("You may need to search manually or check your PythonAnywhere dashboard for the correct path.")
    return None

def print_pythonanywhere_instructions():
    """Print instructions for finding your project on PythonAnywhere."""
    print("\n=== FINDING YOUR PROJECT ON PYTHONANYWHERE ===")
    print("1. Go to the PythonAnywhere dashboard: https://www.pythonanywhere.com/user/YOUR_USERNAME/")
    print("2. Click on the 'Web' tab")
    print("3. Look for 'Source code' and 'Working directory' sections")
    print("4. These will show the paths to your project")
    print("\nAlternatively, check these common locations:")
    print("- /home/YOUR_USERNAME/")
    print("- /home/YOUR_USERNAME/YOUR_PROJECT_NAME/")
    print("- /home/YOUR_USERNAME/www/")
    print("\nYou can also check your WSGI file for the path:")
    print("- Click on 'WSGI configuration file' in the Web tab")
    print("- Look for a line like: path = '/home/YOUR_USERNAME/YOUR_PROJECT_NAME'")

def main():
    """Main function to run the script."""
    print_pythonanywhere_instructions()
    find_project_directory()

if __name__ == "__main__":
    main()
