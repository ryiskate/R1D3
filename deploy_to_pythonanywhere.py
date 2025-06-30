#!/usr/bin/env python
"""
Deployment script for updating R1D3 on PythonAnywhere using direct REST API calls
"""
import os
import sys
import time
import argparse
import requests
import json

def deploy_to_pythonanywhere(username, api_token, webapp_name=None):
    """Deploy the latest changes to PythonAnywhere using direct API calls"""
    print(f"Connecting to PythonAnywhere account: {username}")
    
    # API base URL
    api_base = f"https://www.pythonanywhere.com/api/v0/user/{username}"
    headers = {"Authorization": f"Token {api_token}"}
    
    # If webapp_name is not provided, use username as default
    if not webapp_name:
        webapp_name = username
    
    # Create a new console
    print("Starting a Bash console...")
    response = requests.post(
        f"{api_base}/consoles/",
        headers=headers,
        json={"executable": "bash", "arguments": ""}
    )
    
    if response.status_code != 201:
        print(f"Failed to create console: {response.text}")
        return False
    
    console_id = response.json()["id"]
    print(f"Console created with ID: {console_id}")
    
    # Commands to run
    commands = [
        f"cd ~/{webapp_name}",  # Adjust this path to your actual project directory
        "git pull",
        "python manage.py migrate",
        "python manage.py collectstatic --noinput"
    ]
    
    # Run each command
    for command in commands:
        print(f"Running: {command}")
        response = requests.post(
            f"{api_base}/consoles/{console_id}/send_input/",
            headers=headers,
            data={"input": command + "\n"}
        )
        
        if response.status_code != 200:
            print(f"Failed to run command: {response.text}")
            return False
        
        # Wait a bit for the command to complete
        print("Waiting for command to complete...")
        time.sleep(5)
        
        # Get the console output
        response = requests.get(
            f"{api_base}/consoles/{console_id}/get_latest_output/",
            headers=headers
        )
        
        if response.status_code == 200:
            output = response.json()["output"]
            print(f"Command output:\n{output}")
        else:
            print(f"Failed to get command output: {response.text}")
    
    # Reload the web app
    print(f"Reloading web app {webapp_name}...")
    response = requests.post(
        f"{api_base}/webapps/{webapp_name}/reload/",
        headers=headers
    )
    
    if response.status_code == 200:
        print("Web app reloaded successfully!")
    else:
        print(f"Failed to reload web app: {response.text}")
        return False
    
    print("Deployment completed successfully!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy R1D3 to PythonAnywhere")
    parser.add_argument("username", help="Your PythonAnywhere username")
    parser.add_argument("token", help="Your PythonAnywhere API token")
    parser.add_argument("--webapp", help="Your web app name (defaults to username)")
    
    args = parser.parse_args()
    deploy_to_pythonanywhere(args.username, args.token, args.webapp)
