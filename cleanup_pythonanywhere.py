#!/usr/bin/env python
"""
Script to clean up disk space on PythonAnywhere for R1D3 project.
This script will:
1. Remove Python cache files
2. Clean up virtual environment
3. Manage backups
4. Clear system cache
5. Optimize Git repository
"""
import os
import subprocess
import shutil
import glob
from datetime import datetime
import sys

def run_command(command):
    """Run a shell command and print output."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(e.stderr)
        return False

def get_size(path):
    """Get size of a directory in MB."""
    size = subprocess.check_output(['du', '-sm', path]).split()[0].decode('utf-8')
    return float(size)

def clean_python_cache():
    """Remove Python cache files."""
    print("\n=== Cleaning Python Cache Files ===")
    initial_size = get_size(os.path.expanduser("~"))
    
    # Remove .pyc files
    run_command("find ~ -name '*.pyc' -delete")
    
    # Remove __pycache__ directories
    run_command("find ~ -name '__pycache__' -type d -exec rm -rf {} +")
    
    # Remove .pytest_cache directories
    run_command("find ~ -name '.pytest_cache' -type d -exec rm -rf {} +")
    
    final_size = get_size(os.path.expanduser("~"))
    print(f"Freed up {initial_size - final_size:.2f}MB from Python cache files")

def clean_virtual_env():
    """Clean up virtual environment."""
    print("\n=== Cleaning Virtual Environment ===")
    venv_path = os.path.expanduser("~/venv")
    initial_size = get_size(venv_path)
    
    # Remove pip cache
    pip_cache = os.path.join(venv_path, "lib/python*/site-packages/pip/cache")
    run_command(f"rm -rf {pip_cache}")
    
    # Remove compiled files
    run_command(f"find {venv_path} -name '*.pyc' -delete")
    run_command(f"find {venv_path} -name '__pycache__' -type d -exec rm -rf {} +")
    
    # Remove test directories
    run_command(f"find {venv_path} -path '*/tests' -type d -exec rm -rf {} +")
    
    final_size = get_size(venv_path)
    print(f"Freed up {initial_size - final_size:.2f}MB from virtual environment")

def manage_backups():
    """Keep only recent backups."""
    print("\n=== Managing Backups ===")
    backup_dir = os.path.expanduser("~/backups")
    
    if not os.path.exists(backup_dir):
        print("No backups directory found")
        return
        
    initial_size = get_size(backup_dir)
    
    # List all SQL files
    sql_files = glob.glob(os.path.join(backup_dir, "*.sql"))
    
    if len(sql_files) <= 1:
        print("Only one or no backup files found. Nothing to clean.")
        return
        
    # Sort by modification time (newest first)
    sql_files.sort(key=os.path.getmtime, reverse=True)
    
    # Keep the newest file
    newest_file = sql_files[0]
    files_to_remove = sql_files[1:]
    
    print(f"Keeping newest backup: {os.path.basename(newest_file)}")
    print(f"Removing {len(files_to_remove)} older backups...")
    
    for file in files_to_remove:
        os.remove(file)
        print(f"Removed {os.path.basename(file)}")
    
    final_size = get_size(backup_dir)
    print(f"Freed up {initial_size - final_size:.2f}MB from backups")

def clear_system_cache():
    """Clear system cache."""
    print("\n=== Clearing System Cache ===")
    cache_dir = os.path.expanduser("~/.cache")
    
    if not os.path.exists(cache_dir):
        print("No cache directory found")
        return
        
    initial_size = get_size(cache_dir)
    
    # Clear cache directory
    for item in os.listdir(cache_dir):
        item_path = os.path.join(cache_dir, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            print(f"Removed {item}")
        except Exception as e:
            print(f"Error removing {item}: {e}")
    
    final_size = get_size(cache_dir)
    print(f"Freed up {initial_size - final_size:.2f}MB from system cache")

def optimize_git_repo():
    """Optimize Git repository."""
    print("\n=== Optimizing Git Repository ===")
    repo_dir = os.path.expanduser("~/R1D3")
    
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        print("No Git repository found at ~/R1D3")
        return
        
    initial_size = get_size(repo_dir)
    
    # Change to repository directory
    os.chdir(repo_dir)
    
    # Run git garbage collection
    run_command("git gc --aggressive --prune=now")
    
    final_size = get_size(repo_dir)
    print(f"Freed up {initial_size - final_size:.2f}MB from Git repository")

def main():
    """Main function to run all cleanup tasks."""
    start_time = datetime.now()
    initial_total = get_size(os.path.expanduser("~"))
    
    print(f"Starting cleanup at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Initial disk usage: {initial_total}MB")
    
    # Run all cleanup tasks
    clean_python_cache()
    clean_virtual_env()
    manage_backups()
    clear_system_cache()
    optimize_git_repo()
    
    # Calculate total savings
    final_total = get_size(os.path.expanduser("~"))
    saved = initial_total - final_total
    
    print("\n=== Cleanup Summary ===")
    print(f"Initial disk usage: {initial_total}MB")
    print(f"Final disk usage: {final_total}MB")
    print(f"Total space freed: {saved:.2f}MB ({saved/initial_total*100:.1f}%)")
    print(f"Cleanup completed in {(datetime.now() - start_time).total_seconds():.1f} seconds")

if __name__ == "__main__":
    main()
