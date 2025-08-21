#!/usr/bin/env python
"""
Production Database Seeding Script for R1D3
This script can be run directly on PythonAnywhere to seed the production database
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from projects.models import Team
from strategy.models import StrategyMilestone


def create_admin_user():
    """Create the main admin user"""
    print("Creating admin user...")
    
    # Admin credentials - CHANGE THESE IN PRODUCTION
    admin_data = {
        'username': 'admin',
        'email': 'admin@r1d3.com',
        'password': 'R1D3Admin2025!',  # Change this password!
        'first_name': 'System',
        'last_name': 'Administrator'
    }
    
    # Check if admin already exists
    if User.objects.filter(username=admin_data['username']).exists():
        print(f"Admin user '{admin_data['username']}' already exists.")
        return
    
    # Create superuser
    admin_user = User.objects.create_superuser(
        username=admin_data['username'],
        email=admin_data['email'],
        password=admin_data['password'],
        first_name=admin_data['first_name'],
        last_name=admin_data['last_name']
    )
    
    print(f"✅ Created admin user: {admin_data['username']}")
    print(f"   Email: {admin_data['email']}")
    print(f"   Password: {admin_data['password']} (CHANGE THIS!)")


def create_staff_users():
    """Create staff users for different departments"""
    print("\nCreating staff users...")
    
    staff_users = [
        {
            'username': 'project_manager',
            'email': 'pm@r1d3.com',
            'password': 'PM_R1D3_2025!',
            'first_name': 'Project',
            'last_name': 'Manager',
            'is_staff': True
        },
        {
            'username': 'developer',
            'email': 'dev@r1d3.com',
            'password': 'Dev_R1D3_2025!',
            'first_name': 'Lead',
            'last_name': 'Developer',
            'is_staff': True
        },
        {
            'username': 'content_manager',
            'email': 'content@r1d3.com',
            'password': 'Content_R1D3_2025!',
            'first_name': 'Content',
            'last_name': 'Manager',
            'is_staff': True
        },
        {
            'username': 'social_media',
            'email': 'social@r1d3.com',
            'password': 'Social_R1D3_2025!',
            'first_name': 'Social Media',
            'last_name': 'Manager',
            'is_staff': True
        }
    ]
    
    for user_data in staff_users:
        if User.objects.filter(username=user_data['username']).exists():
            print(f"User '{user_data['username']}' already exists. Skipping.")
            continue
        
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=user_data['is_staff']
        )
        
        print(f"✅ Created staff user: {user_data['username']} (password: {user_data['password']})")


def create_teams():
    """Create default teams"""
    print("\nCreating teams...")
    
    teams_data = [
        {
            'name': 'Development Team',
            'description': 'Core development team for R1D3 projects'
        },
        {
            'name': 'Content Team',
            'description': 'Content creation and indie news team'
        },
        {
            'name': 'Marketing Team',
            'description': 'Social media and marketing team'
        },
        {
            'name': 'Education Team',
            'description': 'Educational content and course development'
        },
        {
            'name': 'Arcade Team',
            'description': 'Arcade management and operations'
        },
        {
            'name': 'Theme Park Team',
            'description': 'Theme park operations and maintenance'
        }
    ]
    
    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            name=team_data['name'],
            defaults={'description': team_data['description']}
        )
        if created:
            print(f"✅ Created team: {team.name}")
        else:
            print(f"Team already exists: {team.name}")


def create_milestones():
    """Create initial strategy milestones"""
    print("\nCreating strategy milestones...")
    
    milestones_data = [
        {
            'title': 'Release First Indie Game',
            'description': 'Complete development and release our first indie game to establish R1D3 in the gaming market',
            'status': 'in_progress',
            'priority': 'high'
        },
        {
            'title': 'Launch Content Platform',
            'description': 'Develop and launch comprehensive content management and indie news platform',
            'status': 'planning',
            'priority': 'high'
        },
        {
            'title': 'Build Community Engagement',
            'description': 'Create active community around R1D3 brand through social media and events',
            'status': 'planning',
            'priority': 'medium'
        },
        {
            'title': 'Establish Educational Programs',
            'description': 'Launch educational courses and knowledge base for game development',
            'status': 'planning',
            'priority': 'medium'
        },
        {
            'title': 'Expand Business Operations',
            'description': 'Grow arcade and theme park operations for additional revenue streams',
            'status': 'planning',
            'priority': 'low'
        }
    ]
    
    for milestone_data in milestones_data:
        milestone, created = StrategyMilestone.objects.get_or_create(
            title=milestone_data['title'],
            defaults={
                'description': milestone_data['description'],
                'status': milestone_data['status'],
                'priority': milestone_data['priority']
            }
        )
        if created:
            print(f"✅ Created milestone: {milestone.title}")
        else:
            print(f"Milestone already exists: {milestone.title}")


def main():
    """Main seeding function"""
    print("🚀 Starting R1D3 Production Database Seeding...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            create_admin_user()
            create_staff_users()
            create_teams()
            create_milestones()
        
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print("\n🔐 IMPORTANT SECURITY NOTES:")
        print("1. Change all default passwords immediately after first login")
        print("2. Update email addresses to real ones")
        print("3. Review user permissions and adjust as needed")
        print("4. Delete this script after running to avoid security risks")
        
    except Exception as e:
        print(f"\n❌ Error during database seeding: {str(e)}")
        raise


if __name__ == '__main__':
    main()
