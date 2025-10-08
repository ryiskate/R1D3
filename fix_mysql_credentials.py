#!/usr/bin/env python
"""
Script to fix MySQL credentials on PythonAnywhere.
This script:
1. Checks your current MySQL credentials
2. Tests connection with new credentials
3. Updates your .env file with working credentials
"""
import os
import sys
import MySQLdb
import getpass
from dotenv import load_dotenv

def check_current_credentials():
    """Check current MySQL credentials in .env file."""
    print("\n=== Checking Current MySQL Credentials ===")
    
    # Load current environment variables
    load_dotenv()
    
    # Check if DATABASE_URL is set
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found in .env file.")
        return None
    
    print(f"Current DATABASE_URL: {database_url}")
    
    # Parse DATABASE_URL
    # Format: mysql://username:password@host/database_name
    try:
        # Remove mysql:// prefix
        if database_url.startswith('mysql://'):
            database_url = database_url[8:]
        
        # Split into credentials and host/database
        credentials, host_db = database_url.split('@', 1)
        
        # Split credentials into username and password
        username, password = credentials.split(':', 1)
        
        # Split host_db into host and database
        host, database = host_db.split('/', 1)
        
        # Handle port if present
        if ':' in host:
            host, port = host.split(':', 1)
            port = int(port)
        else:
            port = 3306
        
        return {
            'username': username,
            'password': password,
            'host': host,
            'database': database,
            'port': port
        }
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        return None

def get_pythonanywhere_mysql_credentials():
    """Get MySQL credentials from PythonAnywhere dashboard."""
    print("\n=== PythonAnywhere MySQL Credentials ===")
    print("To find your correct MySQL credentials:")
    print("1. Go to the PythonAnywhere dashboard")
    print("2. Click on the 'Databases' tab")
    print("3. Look for your MySQL database information")
    print("   - Username is usually your PythonAnywhere username")
    print("   - Password is what you set when creating the database")
    print("   - Host is usually 'username.mysql.pythonanywhere-services.com'")
    print("   - Database name is usually 'username$default'")
    
    username = input("Enter MySQL username: ")
    password = getpass.getpass("Enter MySQL password: ")
    host = input("Enter MySQL host (default: username.mysql.pythonanywhere-services.com): ")
    if not host:
        host = f"{username}.mysql.pythonanywhere-services.com"
    database = input("Enter MySQL database name (default: username$default): ")
    if not database:
        database = f"{username}$default"
    
    return {
        'username': username,
        'password': password,
        'host': host,
        'database': database,
        'port': 3306
    }

def test_mysql_connection(credentials):
    """Test MySQL connection with given credentials."""
    print("\n=== Testing MySQL Connection ===")
    
    try:
        connection = MySQLdb.connect(
            user=credentials['username'],
            passwd=credentials['password'],
            host=credentials['host'],
            db=credentials['database'],
            port=credentials['port']
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result[0] == 1:
            print("✓ MySQL connection successful!")
            connection.close()
            return True
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        return False

def update_env_file(credentials):
    """Update .env file with working credentials."""
    print("\n=== Updating .env File ===")
    
    # Create DATABASE_URL
    database_url = f"mysql://{credentials['username']}:{credentials['password']}@{credentials['host']}/{credentials['database']}"
    
    # Read current .env file
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or add DATABASE_URL
        database_url_found = False
        for i, line in enumerate(lines):
            if line.startswith('DATABASE_URL='):
                lines[i] = f"DATABASE_URL={database_url}\n"
                database_url_found = True
                break
        
        if not database_url_found:
            lines.append(f"DATABASE_URL={database_url}\n")
        
        # Write updated .env file
        with open(env_path, 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env file
        with open(env_path, 'w') as f:
            f.write(f"DATABASE_URL={database_url}\n")
            f.write("DEBUG=False\n")
            f.write("ALLOWED_HOSTS=r1d3.pythonanywhere.com,localhost,127.0.0.1\n")
    
    print(f"✓ Updated .env file with new DATABASE_URL")
    return True

def main():
    """Main function to run the script."""
    print("=== MySQL Credentials Fix Tool ===")
    
    # Check current credentials
    current_credentials = check_current_credentials()
    
    # Get new credentials
    print("\nPlease enter your correct MySQL credentials:")
    new_credentials = get_pythonanywhere_mysql_credentials()
    
    # Test connection with new credentials
    if test_mysql_connection(new_credentials):
        # Update .env file
        update_env_file(new_credentials)
        
        print("\n=== Next Steps ===")
        print("1. Restart your web app:")
        print("   touch /var/www/R1D3_pythonanywhere_com_wsgi.py")
        print("2. Try accessing your login page again")
    else:
        print("\n✗ MySQL connection failed with the provided credentials.")
        print("Please double-check your MySQL credentials in the PythonAnywhere dashboard.")

if __name__ == "__main__":
    main()
