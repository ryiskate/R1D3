#!/usr/bin/env python
"""
Script to create a .env file with MySQL database configuration for PythonAnywhere.
This is a simplified version that just creates the .env file without checking packages.
"""
import os
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
    
    # Create new .env file or overwrite existing one
    with open(env_path, 'w') as f:
        f.write(f"# Database configuration\n")
        f.write(f"DATABASE_URL={database_url}\n")
        f.write(f"DEBUG=False\n")
        f.write(f"ALLOWED_HOSTS={username}.pythonanywhere.com,localhost,127.0.0.1\n")
    
    print(f"Created .env file with DATABASE_URL: {database_url}")
    return database_url

def print_instructions(username, database_name):
    """Print instructions for setting up the MySQL database."""
    print("\n=== INSTRUCTIONS FOR SETTING UP MYSQL ON PYTHONANYWHERE ===")
    print("\n1. Create the MySQL database in PythonAnywhere:")
    print("   - Go to the PythonAnywhere dashboard")
    print("   - Click on the 'Databases' tab")
    print("   - If you haven't created a MySQL database yet, create one")
    print(f"   - Your database name should be: {database_name}")
    print("\n2. Update your WSGI file:")
    print(f"   - Edit /var/www/{username}_pythonanywhere_com_wsgi.py")
    print("   - Add these lines at the top after the imports:")
    print("     ```python")
    print("     from dotenv import load_dotenv")
    print("     load_dotenv()")
    print("     ```")
    print("\n3. Run migrations:")
    print("   python manage.py migrate --fake-initial")
    print("\n4. Restart your web app:")
    print(f"   touch /var/www/{username}_pythonanywhere_com_wsgi.py")
    print("\n===========================================")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Create .env file for MySQL configuration')
    parser.add_argument('--username', required=True, help='Your PythonAnywhere username')
    parser.add_argument('--password', required=True, help='Your MySQL password')
    parser.add_argument('--database', help='Your MySQL database name (default: username$default)')
    
    args = parser.parse_args()
    
    username = args.username
    mysql_password = args.password
    database_name = args.database if args.database else f"{username}$default"
    
    print(f"Creating .env file with MySQL configuration for: {username}")
    print(f"Database name: {database_name}")
    
    # Create .env file
    create_env_file(username, mysql_password, database_name)
    
    # Print instructions
    print_instructions(username, database_name)

if __name__ == "__main__":
    main()
