#!/usr/bin/env python
"""
Script to configure PythonAnywhere to use MySQL instead of SQLite.
This script:
1. Creates or updates the .env file with the correct DATABASE_URL
2. Updates the WSGI file to load environment variables
3. Provides instructions for setting up the MySQL database
"""
import os
import sys
import re
import argparse
from pathlib import Path

def create_env_file(username, mysql_password, database_name=None):
    """Create or update .env file with MySQL database configuration."""
    if database_name is None:
        database_name = f"{username}$default"
    
    # PythonAnywhere MySQL hostname format
    mysql_host = f"{username}.mysql.pythonanywhere-services.com"
    
    # Create DATABASE_URL in the format mysql://username:password@host/database_name
    database_url = f"mysql://{username}:{mysql_password}@{mysql_host}/{database_name}"
    
    # Path to .env file
    env_path = Path('.env')
    
    # Check if .env file exists
    if env_path.exists():
        print(f"Found existing .env file at {env_path.absolute()}")
        # Read existing content
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Check if DATABASE_URL already exists
        if re.search(r'^DATABASE_URL=', content, re.MULTILINE):
            # Replace existing DATABASE_URL
            content = re.sub(
                r'^DATABASE_URL=.*$', 
                f'DATABASE_URL={database_url}', 
                content, 
                flags=re.MULTILINE
            )
        else:
            # Add DATABASE_URL at the end
            content += f"\n# Database configuration\nDATABASE_URL={database_url}\n"
        
        # Write updated content
        with open(env_path, 'w') as f:
            f.write(content)
        print(f"Updated DATABASE_URL in .env file")
    else:
        # Create new .env file
        with open(env_path, 'w') as f:
            f.write(f"# Database configuration\nDATABASE_URL={database_url}\n")
        print(f"Created new .env file with DATABASE_URL")
    
    return database_url

def update_wsgi_file(username):
    """Update the PythonAnywhere WSGI file to load environment variables."""
    wsgi_path = Path(f"/var/www/{username}_pythonanywhere_com_wsgi.py")
    
    if not wsgi_path.exists():
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

def print_instructions(username, database_url, database_name):
    """Print instructions for setting up the MySQL database."""
    print("\n=== INSTRUCTIONS FOR SETTING UP MYSQL ON PYTHONANYWHERE ===")
    print("1. Make sure you have installed the required packages:")
    print("   pip install python-dotenv dj-database-url mysqlclient")
    print("\n2. Create the MySQL database in PythonAnywhere:")
    print("   - Go to the PythonAnywhere dashboard")
    print("   - Click on the 'Databases' tab")
    print("   - If you haven't created a MySQL database yet, create one")
    print(f"   - Your database name should be: {database_name}")
    print("\n3. Initialize the database:")
    print("   - Go to the PythonAnywhere bash console")
    print("   - Navigate to your project directory:")
    print(f"     cd /home/{username}/R1D3")
    print("   - Run migrations:")
    print("     python manage.py migrate")
    print("\n4. Restart your web app:")
    print(f"   touch /var/www/{username}_pythonanywhere_com_wsgi.py")
    print("\n5. Verify the configuration:")
    print("   - Create a simple script to check the database connection:")
    print("     ```python")
    print("     # check_db.py")
    print("     import os")
    print("     import django")
    print("     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')")
    print("     django.setup()")
    print("     from django.db import connection")
    print("     print(f\"Database engine: {connection.vendor}\")")
    print("     ```")
    print("   - Run the script:")
    print("     python check_db.py")
    print("   - It should output: \"Database engine: mysql\"")
    print("\n=== DATABASE CONFIGURATION SUMMARY ===")
    print(f"DATABASE_URL: {database_url}")
    print("This URL has been added to your .env file.")
    print("Make sure this file is deployed to your PythonAnywhere account.")
    print("===========================================")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Configure PythonAnywhere to use MySQL')
    parser.add_argument('--username', required=True, help='Your PythonAnywhere username')
    parser.add_argument('--password', required=True, help='Your MySQL password')
    parser.add_argument('--database', help='Your MySQL database name (default: username$default)')
    
    args = parser.parse_args()
    
    username = args.username
    mysql_password = args.password
    database_name = args.database if args.database else f"{username}$default"
    
    print(f"Configuring MySQL for PythonAnywhere user: {username}")
    print(f"Database name: {database_name}")
    
    # Create or update .env file
    database_url = create_env_file(username, mysql_password, database_name)
    
    # Check if we're on PythonAnywhere
    if os.path.exists(f"/home/{username}"):
        print("Detected PythonAnywhere environment")
        # Update WSGI file
        update_wsgi_file(username)
    else:
        print("Not running on PythonAnywhere. WSGI file will need to be updated manually.")
    
    # Print instructions
    print_instructions(username, database_url, database_name)

if __name__ == "__main__":
    main()
