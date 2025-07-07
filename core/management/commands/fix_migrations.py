"""
Django management command to fix migration dependency issues.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fix migration dependency issues between projects, strategy, and indie_news apps'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking current migration state...'))
        self.check_migrations()
        
        self.stdout.write(self.style.SUCCESS('Fixing migration order...'))
        self.fix_migration_order()
        
        self.stdout.write(self.style.SUCCESS('Checking updated migration state...'))
        self.check_migrations()
        
        self.stdout.write(self.style.SUCCESS('Migration fix complete. You can now run migrate.'))

    def check_migrations(self):
        """Check the current migration state"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('indie_news', 'projects', 'strategy') ORDER BY applied")
            rows = cursor.fetchall()
            
            self.stdout.write("Relevant migration records in the database:")
            self.stdout.write("-" * 80)
            self.stdout.write(f"{'App':<20} {'Migration Name':<50} {'Applied At'}")
            self.stdout.write("-" * 80)
            
            for row in rows:
                app, name, applied = row
                self.stdout.write(f"{app:<20} {name:<50} {applied}")

    def fix_migration_order(self):
        """Fix the migration order by updating the timestamps"""
        with connection.cursor() as cursor:
            # First, check if the problematic migrations exist
            cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='indie_news' AND name='0002_indienewstask_team'")
            indie_news = cursor.fetchone()
            
            cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='projects' AND name='0015_team_arcadetask_team_educationtask_team_and_more'")
            projects_team = cursor.fetchone()
            
            cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='strategy' AND name='0001_initial'")
            strategy_initial = cursor.fetchone()
            
            cursor.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='projects' AND name='0001_initial'")
            projects_initial = cursor.fetchone()
            
            if not indie_news:
                self.stdout.write(self.style.ERROR("Could not find indie_news.0002_indienewstask_team migration!"))
            else:
                self.stdout.write(f"Found indie_news.0002_indienewstask_team with ID {indie_news[0]} applied at {indie_news[3]}")
            
            if not projects_team:
                self.stdout.write(self.style.ERROR("Could not find projects.0015_team_arcadetask_team_educationtask_team_and_more migration!"))
            else:
                self.stdout.write(f"Found projects.0015_team... with ID {projects_team[0]} applied at {projects_team[3]}")
            
            if not strategy_initial:
                self.stdout.write(self.style.ERROR("Could not find strategy.0001_initial migration!"))
            else:
                self.stdout.write(f"Found strategy.0001_initial with ID {strategy_initial[0]} applied at {strategy_initial[3]}")
            
            if not projects_initial:
                self.stdout.write(self.style.ERROR("Could not find projects.0001_initial migration!"))
            else:
                self.stdout.write(f"Found projects.0001_initial with ID {projects_initial[0]} applied at {projects_initial[3]}")
            
            # Update the timestamps to fix the order
            now = datetime.now()
            
            # Create timestamps with proper ordering
            # strategy.0001_initial should be first
            # projects.0001_initial should be second
            # projects.0015_team... should be third
            # indie_news.0002_indienewstask_team should be fourth
            
            # Use MySQL-compatible timestamp format
            if strategy_initial:
                strategy_time = now - timedelta(minutes=30)
                self.stdout.write(f"Setting strategy.0001_initial timestamp to: {strategy_time}")
                cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                              [strategy_time, strategy_initial[0]])
            
            if projects_initial:
                projects_initial_time = now - timedelta(minutes=25)
                self.stdout.write(f"Setting projects.0001_initial timestamp to: {projects_initial_time}")
                cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                              [projects_initial_time, projects_initial[0]])
            
            if projects_team:
                projects_team_time = now - timedelta(minutes=20)
                self.stdout.write(f"Setting projects.0015_team... timestamp to: {projects_team_time}")
                cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                              [projects_team_time, projects_team[0]])
            
            if indie_news:
                indie_news_time = now - timedelta(minutes=15)
                self.stdout.write(f"Setting indie_news.0002_indienewstask_team timestamp to: {indie_news_time}")
                cursor.execute("UPDATE django_migrations SET applied = %s WHERE id = %s", 
                              [indie_news_time, indie_news[0]])
            
            self.stdout.write(self.style.SUCCESS("Migration timestamps updated successfully!"))
