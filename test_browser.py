"""
Test script to check the milestone display in the browser.
"""
import os
import django
import requests
import re
import traceback
from bs4 import BeautifulSoup

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

def test_milestone_display():
    """Test the milestone display in the browser."""
    print("\n=== TESTING MILESTONE DISPLAY IN BROWSER ===")
    
    # Make a request to the server
    try:
        print("Making request to http://127.0.0.1:8000/")
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response length: {len(response.text)} characters")
        
        # Check if the response contains the milestone context processor debug output
        if "==== MILESTONE INFO CONTEXT PROCESSOR CALLED ====" in response.text:
            print("✅ Found milestone context processor debug output in response")
        else:
            print("❌ No milestone context processor debug output in response")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the milestone display
        milestone_display = soup.select_one('#milestone-display')
        
        if milestone_display:
            print("Found milestone display in HTML")
            
            # Extract the milestone text
            milestone_text = milestone_display.text.strip()
            print(f"Milestone text: {milestone_text}")
            
            # Print raw text for debugging
            print(f"Raw text: {repr(milestone_text)}")
            
            # Check if the milestone text contains the expected milestone title
            if "Release First Indie Game" in milestone_text:
                print("✅ Milestone title found in display")
            else:
                print("❌ Milestone title not found in display")
            
            # Check if the milestone text contains the expected company phase
            if "Indie Game Development" in milestone_text:
                print("✅ Company phase found in display")
            else:
                print("❌ Company phase not found in display")
            
            # Check the background style
            style = milestone_display.select_one('div').get('style', '')
            print(f"Background style: {style}")
            
            # For indie_dev phase, we expect a blue gradient
            if "linear-gradient(135deg, #4e73df 0%, #224abe 100%)" in style:
                print("✅ Correct background gradient for indie dev phase")
            else:
                print("❌ Incorrect background gradient")
        else:
            print("❌ Milestone display not found in HTML")
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    
    print("=== END OF TEST ===\n")

if __name__ == "__main__":
    test_milestone_display()
