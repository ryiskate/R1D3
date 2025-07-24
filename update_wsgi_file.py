#!/usr/bin/env python
"""
Script to update the PythonAnywhere WSGI file to load environment variables.
This script will add the necessary imports to load environment variables from .env file.
"""
import os
import sys
import re
import argparse

def update_wsgi_file(username):
    """Update the PythonAnywhere WSGI file to load environment variables."""
    wsgi_path = f"/var/www/{username}_pythonanywhere_com_wsgi.py"
    
    if not os.path.exists(wsgi_path):
        print(f"WSGI file not found at {wsgi_path}")
        print("You may need to manually update your WSGI file.")
        return False
    
    with open(wsgi_path, 'r') as f:
        content = f.read()
    
    # Check if dotenv is already imported
    if "from dotenv import load_dotenv" not in content:
        # Add dotenv import and load_dotenv() call
        import_pattern = r"import os\s+import sys"
        if re.search(import_pattern, content):
            content = re.sub(
                import_pattern,
                "import os\nimport sys\nfrom dotenv import load_dotenv\n\n# Load environment variables from .env file\nload_dotenv()",
                content
            )
        else:
            # If the pattern doesn't match, add it at the top
            content = "import os\nimport sys\nfrom dotenv import load_dotenv\n\n# Load environment variables from .env file\nload_dotenv()\n\n" + content
        
        with open(wsgi_path, 'w') as f:
            f.write(content)
        print(f"Updated WSGI file to load environment variables")
        return True
    else:
        print(f"WSGI file already configured to load environment variables")
        return True

def print_wsgi_instructions(username):
    """Print instructions for manually updating the WSGI file."""
    print("\n=== MANUAL WSGI FILE UPDATE INSTRUCTIONS ===")
    print(f"If the automatic update fails, manually edit the WSGI file:")
    print(f"1. Open the file: /var/www/{username}_pythonanywhere_com_wsgi.py")
    print("2. Add these lines at the top after the imports:")
    print("   ```python")
    print("   from dotenv import load_dotenv")
    print("   load_dotenv()")
    print("   ```")
    print("3. Save the file and restart your web app:")
    print(f"   touch /var/www/{username}_pythonanywhere_com_wsgi.py")
    print("===========================================")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Update PythonAnywhere WSGI file')
    parser.add_argument('--username', required=True, help='Your PythonAnywhere username')
    
    args = parser.parse_args()
    username = args.username
    
    print(f"Updating WSGI file for PythonAnywhere user: {username}")
    
    # Try to update the WSGI file
    success = update_wsgi_file(username)
    
    if not success:
        print_wsgi_instructions(username)
    else:
        print("\nWSGI file updated successfully!")
        print(f"Restart your web app with: touch /var/www/{username}_pythonanywhere_com_wsgi.py")

if __name__ == "__main__":
    main()
