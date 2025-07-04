from django.core.management.base import BaseCommand
import os
import json
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore

class Command(BaseCommand):
    help = 'Load initial milestones into all active sessions'

    def handle(self, *args, **options):
        # Load the initial milestones from the fixture file
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'fixtures', 'initial_milestones.json')
        
        self.stdout.write(f"Looking for fixture file at: {file_path}")
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Fixture file not found at {file_path}"))
            return
            
        try:
            with open(file_path, 'r') as f:
                initial_milestones = json.load(f)
                self.stdout.write(self.style.SUCCESS(f"Loaded initial milestones: {initial_milestones}"))
                
                # Get all active sessions
                sessions = Session.objects.all()
                self.stdout.write(f"Found {len(sessions)} active sessions")
                
                # Update each session with the initial milestones
                for session in sessions:
                    session_data = session.get_decoded()
                    session_data['user_milestones'] = initial_milestones
                    
                    # Create a new session store and save the updated data
                    session_store = SessionStore(session_key=session.session_key)
                    session_store.load()
                    session_store['user_milestones'] = initial_milestones
                    session_store.save()
                    
                self.stdout.write(self.style.SUCCESS("Successfully loaded initial milestones into all active sessions"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading initial milestones: {e}"))
