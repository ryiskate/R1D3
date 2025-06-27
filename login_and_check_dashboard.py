import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import traceback

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth.models import User
from projects.game_models import GameTask
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask,
    SocialMediaTask, ArcadeTask, ThemeParkTask
)

def login_and_check_dashboard():
    print("Starting login and dashboard check...")
    # Base URL
    base_url = 'http://127.0.0.1:8000'
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Get CSRF token from login page
    login_url = urljoin(base_url, '/accounts/login/')
    print(f"Accessing login page: {login_url}")
    try:
        login_response = session.get(login_url)
        print(f"Login page status code: {login_response.status_code}")
        login_soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_input = login_soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if not csrf_input:
            print("CSRF token not found in login page")
            print("Login page content:")
            print(login_response.text[:500]) # Print first 500 chars
            return
        csrf_token = csrf_input['value']
        print(f"Found CSRF token: {csrf_token[:10]}...")
    except Exception as e:
        print(f"Error accessing login page: {e}")
        traceback.print_exc()
        return
    
    # Login with admin credentials
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'login': 'admin',
        'password': 'admin123',
    }
    session.post(login_url, data=login_data, headers={'Referer': login_url})
    
    # Access the dashboard
    dashboard_url = urljoin(base_url, '/dashboard/')
    dashboard_response = session.get(dashboard_url)
    
    # Print dashboard content for debugging
    print(f"Dashboard status code: {dashboard_response.status_code}")
    
    # Check if we're logged in by looking for admin username in the response
    if 'admin' in dashboard_response.text:
        print("Successfully logged in as admin")
    else:
        print("Failed to log in as admin")
        return
    
    # Parse the dashboard HTML
    dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
    
    # Find task table
    task_table = dashboard_soup.find('table', {'id': 'dataTable'})
    if not task_table:
        print("Task table not found in dashboard")
        return
    
    # Count tasks in the table
    task_rows = task_table.find('tbody').find_all('tr')
    print(f"Found {len(task_rows)} tasks in the dashboard table")
    
    # Print task counts from database for comparison
    print("\nTask counts in database:")
    print(f"GameTask count: {GameTask.objects.count()}")
    print(f"R1D3Task count: {R1D3Task.objects.count()}")
    print(f"GameDevelopmentTask count: {GameDevelopmentTask.objects.count()}")
    print(f"EducationTask count: {EducationTask.objects.count()}")
    print(f"SocialMediaTask count: {SocialMediaTask.objects.count()}")
    print(f"ArcadeTask count: {ArcadeTask.objects.count()}")
    print(f"ThemeParkTask count: {ThemeParkTask.objects.count()}")
    
    # Calculate total tasks
    total_tasks = (
        GameTask.objects.count() +
        R1D3Task.objects.count() +
        GameDevelopmentTask.objects.count() +
        EducationTask.objects.count() +
        SocialMediaTask.objects.count() +
        ArcadeTask.objects.count() +
        ThemeParkTask.objects.count()
    )
    print(f"Total tasks in database: {total_tasks}")
    
    # Check if all tasks are displayed
    if len(task_rows) == total_tasks:
        print("\nSUCCESS: All tasks are displayed in the dashboard!")
    else:
        print(f"\nWARNING: Not all tasks are displayed. Dashboard shows {len(task_rows)} out of {total_tasks} tasks.")

if __name__ == "__main__":
    try:
        login_and_check_dashboard()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
