#!/usr/bin/env python
"""
Script to create user accounts for R1D3 platform on PythonAnywhere.
This script:
1. Creates superuser accounts
2. Creates regular user accounts
3. Lists all existing users
"""
import os
import sys
import django
from getpass import getpass

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def list_users():
    """List all existing users."""
    print("\n=== Existing Users ===")
    users = User.objects.all()
    
    if not users:
        print("No users found in the database.")
        return
    
    for user in users:
        user_type = "Superuser" if user.is_superuser else "Staff" if user.is_staff else "Regular"
        status = "Active" if user.is_active else "Inactive"
        print(f"- {user.username} ({user.email}) - {user_type} - {status}")
    
    print(f"\nTotal users: {users.count()}")

def create_superuser(username, email, password):
    """Create a superuser account."""
    print(f"\n=== Creating Superuser: {username} ===")
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        
        # Ask if they want to update the password
        update = input("Do you want to update the password? (y/n): ").lower()
        if update == 'y':
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            print(f"✓ Updated password and permissions for '{username}'")
        return
    
    # Create new superuser
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Superuser '{username}' created successfully!")
        print(f"  Email: {email}")
        print(f"  Password: {'*' * len(password)}")
    except Exception as e:
        print(f"✗ Error creating superuser: {e}")

def create_regular_user(username, email, password, is_staff=False):
    """Create a regular user account."""
    print(f"\n=== Creating User: {username} ===")
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        return
    
    # Create new user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = is_staff
        user.is_active = True
        user.save()
        
        user_type = "Staff user" if is_staff else "Regular user"
        print(f"✓ {user_type} '{username}' created successfully!")
        print(f"  Email: {email}")
        print(f"  Password: {'*' * len(password)}")
    except Exception as e:
        print(f"✗ Error creating user: {e}")

def delete_user(username):
    """Delete a user account."""
    print(f"\n=== Deleting User: {username} ===")
    
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"✓ User '{username}' deleted successfully!")
    except User.DoesNotExist:
        print(f"✗ User '{username}' does not exist.")
    except Exception as e:
        print(f"✗ Error deleting user: {e}")

def interactive_mode():
    """Interactive mode to create users."""
    print("\n=== R1D3 User Account Creator ===")
    print("This script will help you create user accounts for your R1D3 platform.")
    
    while True:
        print("\nOptions:")
        print("1. Create superuser")
        print("2. Create regular user")
        print("3. List all users")
        print("4. Delete user")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = getpass("Enter password: ")
            password_confirm = getpass("Confirm password: ")
            
            if password != password_confirm:
                print("✗ Passwords do not match!")
                continue
            
            create_superuser(username, email, password)
        
        elif choice == '2':
            username = input("Enter username: ").strip()
            email = input("Enter email: ").strip()
            password = getpass("Enter password: ")
            password_confirm = getpass("Confirm password: ")
            
            if password != password_confirm:
                print("✗ Passwords do not match!")
                continue
            
            is_staff = input("Make this user staff? (y/n): ").lower() == 'y'
            create_regular_user(username, email, password, is_staff)
        
        elif choice == '3':
            list_users()
        
        elif choice == '4':
            username = input("Enter username to delete: ").strip()
            confirm = input(f"Are you sure you want to delete '{username}'? (y/n): ").lower()
            if confirm == 'y':
                delete_user(username)
        
        elif choice == '5':
            print("\nExiting...")
            break
        
        else:
            print("✗ Invalid choice. Please try again.")

def quick_create_admin():
    """Quick create admin account."""
    print("\n=== Quick Admin Account Creation ===")
    
    # Default admin credentials
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (default: admin@r1d3.com): ").strip() or "admin@r1d3.com"
    password = getpass("Enter admin password: ")
    
    if not password:
        print("✗ Password cannot be empty!")
        return
    
    create_superuser(username, email, password)
    
    print("\n=== Admin Account Created ===")
    print("You can now log in to your R1D3 platform at:")
    print("https://r1d3.pythonanywhere.com/accounts/login/")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create user accounts for R1D3 platform')
    parser.add_argument('--quick', action='store_true', help='Quick create admin account')
    parser.add_argument('--list', action='store_true', help='List all users')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--username', help='Username for new user')
    parser.add_argument('--email', help='Email for new user')
    parser.add_argument('--password', help='Password for new user')
    parser.add_argument('--superuser', action='store_true', help='Create as superuser')
    
    args = parser.parse_args()
    
    if args.quick:
        quick_create_admin()
    elif args.list:
        list_users()
    elif args.interactive:
        interactive_mode()
    elif args.username and args.email and args.password:
        if args.superuser:
            create_superuser(args.username, args.email, args.password)
        else:
            create_regular_user(args.username, args.email, args.password)
    else:
        # Default to interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
