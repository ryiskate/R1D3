"""
Migration script to transfer data from the old GameTask model to the new specialized task models.
This script should be run after the new models have been created and before the old model is removed.
"""

import os
import sys
import django
import argparse
from django.utils import timezone
from django.db import transaction

# Set up Django environment
sys.path.append('e:/SistemaR1D3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import models after Django setup
from projects.game_models import GameTask
from projects.task_models import (
    R1D3Task, GameDevelopmentTask, EducationTask, 
    SocialMediaTask, ArcadeTask, ThemeParkTask
)
from django.contrib.auth.models import User

def migrate_tasks(dry_run=False, section_filter=None, batch_size=100, verbose=False):
    """
    Migrate tasks from the old GameTask model to the new specialized task models
    based on their company_section field.
    
    Args:
        dry_run (bool): If True, only simulate the migration without creating new tasks
        section_filter (str): If provided, only migrate tasks from this company section
        batch_size (int): Number of tasks to process in each transaction
        verbose (bool): If True, print detailed information about each task being migrated
    """
    print("Starting task migration...")
    if dry_run:
        print("[DRY RUN] No actual data will be migrated")
    
    # Build the query
    tasks_query = GameTask.objects.all()
    if section_filter:
        tasks_query = tasks_query.filter(company_section=section_filter)
        print(f"Filtering tasks to company section: {section_filter}")
    
    # Get counts before migration
    total_tasks = tasks_query.count()
    print(f"Found {total_tasks} tasks to migrate")
    
    # Track counts for each section
    migrated_counts = {
        'r1d3': 0,
        'game_development': 0,
        'education': 0,
        'social_media': 0,
        'arcade': 0,
        'theme_park': 0,
        'other': 0,
        'skipped': 0,
        'error': 0
    }
    
    # Create a default user for tasks without a creator
    default_user = User.objects.first()
    if not default_user:
        print("Error: No users found in the system. Please create a user first.")
        return
    
    # Process tasks in batches
    task_count = 0
    batch_count = 0
    
    for task in tasks_query.iterator(chunk_size=batch_size):
        # Start a new transaction for each batch
        if task_count % batch_size == 0:
            if not dry_run:
                transaction.set_autocommit(False)
            batch_count += 1
            if verbose:
                print(f"\nProcessing batch {batch_count}...")
        
        task_count += 1
        
        try:
            # Common fields for all task types
            common_fields = {
                'title': task.title,
                'description': task.description,
                'task_type': task.task_type,
                'status': task.status,
                'priority': task.priority,
                'assigned_to': task.assigned_to,
                'due_date': task.due_date,
                'estimated_hours': task.estimated_hours,
                'actual_hours': task.actual_hours,
                'created_by': task.created_by if task.created_by else default_user,
                'created_at': task.created_at if hasattr(task, 'created_at') else timezone.now(),
                'updated_at': task.updated_at if hasattr(task, 'updated_at') else timezone.now(),
            }
            
            # Migrate based on company section
            company_section = task.company_section if task.company_section else 'other'
            
            if verbose:
                print(f"Processing task {task.id}: {task.title} (Section: {company_section})")
            
            if company_section == 'game_development':
                # Game development task
                if not dry_run:
                    GameDevelopmentTask.objects.create(
                        **common_fields,
                        game=task.game,
                        milestone=task.milestone,
                        gdd_section=task.gdd_section,
                        feature_id=getattr(task, 'feature_id', ''),
                        platform=getattr(task, 'platform', '')
                    )
                migrated_counts['game_development'] += 1
                
            elif company_section == 'education':
                # Education task
                if not dry_run:
                    EducationTask.objects.create(
                        **common_fields,
                        course_id=getattr(task, 'course_id', ''),
                        learning_objective=getattr(task, 'learning_objective', ''),
                        target_audience=getattr(task, 'target_audience', '')
                    )
                migrated_counts['education'] += 1
                
            elif company_section == 'social_media':
                # Social media task
                if not dry_run:
                    SocialMediaTask.objects.create(
                        **common_fields,
                        campaign_id=getattr(task, 'campaign_id', ''),
                        channel=getattr(task, 'channel', ''),
                        target_metrics=getattr(task, 'target_metrics', '')
                    )
                migrated_counts['social_media'] += 1
                
            elif company_section == 'arcade':
                # Arcade task
                if not dry_run:
                    ArcadeTask.objects.create(
                        **common_fields,
                        machine_id=getattr(task, 'machine_id', ''),
                        location=getattr(task, 'location', ''),
                        maintenance_type=getattr(task, 'maintenance_type', '')
                    )
                migrated_counts['arcade'] += 1
                
            elif company_section == 'theme_park':
                # Theme park task
                if not dry_run:
                    ThemeParkTask.objects.create(
                        **common_fields,
                        attraction_id=getattr(task, 'attraction_id', ''),
                        area=getattr(task, 'area', ''),
                        maintenance_type=getattr(task, 'maintenance_type', '')
                    )
                migrated_counts['theme_park'] += 1
                
            else:
                # General R1D3 task
                if not dry_run:
                    R1D3Task.objects.create(
                        **common_fields,
                        department=company_section
                    )
                migrated_counts['r1d3'] += 1
                
        except Exception as e:
            print(f"Error migrating task {task.id} - {task.title}: {str(e)}")
            migrated_counts['error'] += 1
            # Rollback this batch on error if not in dry run mode
            if not dry_run:
                transaction.rollback()
                transaction.set_autocommit(True)
        
        # Commit the batch if we've reached the batch size
        if not dry_run and task_count % batch_size == 0:
            transaction.commit()
            transaction.set_autocommit(True)
            print(f"Committed batch {batch_count} ({batch_size} tasks)")
    
    # Commit any remaining tasks in the last batch
    if not dry_run and task_count % batch_size != 0:
        transaction.commit()
        transaction.set_autocommit(True)
        print(f"Committed final batch ({task_count % batch_size} tasks)")
    
    # Print migration results
    print("\nMigration completed!")
    print(f"R1D3 tasks: {migrated_counts['r1d3']}")
    print(f"Game development tasks: {migrated_counts['game_development']}")
    print(f"Education tasks: {migrated_counts['education']}")
    print(f"Social media tasks: {migrated_counts['social_media']}")
    print(f"Arcade tasks: {migrated_counts['arcade']}")
    print(f"Theme park tasks: {migrated_counts['theme_park']}")
    print(f"Failed migrations: {migrated_counts['error']}")
    print(f"Total tasks processed: {task_count}")
    
    if dry_run:
        print("\n[DRY RUN] No actual data was migrated. Run without --dry-run to perform the actual migration.")

def main():
    parser = argparse.ArgumentParser(description='Migrate tasks from GameTask to specialized task models')
    parser.add_argument('--dry-run', action='store_true', help='Simulate migration without creating new tasks')
    parser.add_argument('--section', type=str, choices=['game_development', 'education', 'social_media', 'arcade', 'theme_park'], 
                        help='Only migrate tasks from this company section')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of tasks to process in each transaction')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information about each task being migrated')
    
    args = parser.parse_args()
    
    migrate_tasks(
        dry_run=args.dry_run,
        section_filter=args.section,
        batch_size=args.batch_size,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
