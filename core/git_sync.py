"""
Git and Database Sync utilities for R1D3 project
"""
import subprocess
import os
from django.conf import settings


class GitSyncManager:
    """Manages Git operations for database synchronization"""
    
    def __init__(self):
        self.base_dir = settings.BASE_DIR
        
    def run_git_command(self, command):
        """Run a git command and return the result"""
        try:
            result = subprocess.run(
                command,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'returncode': -1
            }
    
    def check_database_changes(self):
        """Check if there are uncommitted database changes"""
        result = self.run_git_command('git status --porcelain db.sqlite3')
        return {
            'has_changes': bool(result['output'].strip()),
            'status': result['output'].strip()
        }
    
    def pull_latest(self):
        """Pull latest changes from remote"""
        return self.run_git_command('git pull')
    
    def commit_database(self, message):
        """Commit database changes"""
        # Add database file
        add_result = self.run_git_command('git add db.sqlite3')
        if not add_result['success']:
            return add_result
        
        # Commit
        commit_result = self.run_git_command(f'git commit -m "Database: {message}"')
        return commit_result
    
    def push_changes(self):
        """Push changes to remote"""
        return self.run_git_command('git push')
    
    def sync_database(self, commit_message=None):
        """
        Full database sync workflow:
        1. Check for local changes
        2. If changes exist and message provided, commit and push
        3. Pull latest changes
        4. Return status
        """
        status = {
            'success': False,
            'message': '',
            'details': [],
            'database_updated': False,
            'needs_restart': False
        }
        
        # Check for local changes
        changes = self.check_database_changes()
        
        if changes['has_changes']:
            if commit_message:
                # Commit local changes
                status['details'].append('Committing local database changes...')
                commit_result = self.commit_database(commit_message)
                
                if not commit_result['success']:
                    status['message'] = f"Failed to commit: {commit_result['error']}"
                    return status
                
                status['details'].append('✓ Database changes committed')
                
                # Push changes
                status['details'].append('Pushing to remote...')
                push_result = self.push_changes()
                
                if not push_result['success']:
                    status['message'] = "Failed to push. Try pulling first."
                    status['details'].append(f"✗ Push failed: {push_result['error']}")
                    return status
                
                status['details'].append('✓ Changes pushed successfully')
            else:
                status['message'] = "You have uncommitted database changes. Please provide a commit message."
                status['has_uncommitted_changes'] = True
                return status
        
        # Pull latest changes
        status['details'].append('Pulling latest changes...')
        pull_result = self.pull_latest()
        
        if not pull_result['success']:
            status['message'] = f"Failed to pull: {pull_result['error']}"
            status['details'].append(f"✗ Pull failed: {pull_result['error']}")
            return status
        
        status['details'].append('✓ Pull completed')
        
        # Check if database was updated
        if 'db.sqlite3' in pull_result['output']:
            status['database_updated'] = True
            status['needs_restart'] = True
            status['details'].append('⚠ Database was updated! Restart server to use new data.')
        
        # Success!
        status['success'] = True
        if changes['has_changes'] and commit_message:
            status['message'] = 'Database synced! Your changes were pushed.'
        elif status['database_updated']:
            status['message'] = 'Database synced! New data received. Please restart server.'
        else:
            status['message'] = 'Database already up to date.'
        
        return status
    
    def get_sync_status(self):
        """Get current sync status information"""
        # Check for uncommitted changes
        db_changes = self.check_database_changes()
        
        # Get last commit info
        last_commit = self.run_git_command('git log -1 --pretty=format:"%h - %s (%cr)" db.sqlite3')
        
        # Check if we're behind remote
        self.run_git_command('git fetch')
        behind = self.run_git_command('git rev-list HEAD..origin/master --count')
        
        return {
            'has_uncommitted_changes': db_changes['has_changes'],
            'last_database_commit': last_commit['output'] if last_commit['success'] else 'Unknown',
            'commits_behind': int(behind['output'].strip()) if behind['success'] and behind['output'].strip().isdigit() else 0
        }
