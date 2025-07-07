"""
Test script to check the milestone context processor.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_system.settings')
django.setup()

# Import the context processor
from core.context_processors import milestone_info
from projects.game_models import GameMilestone

# First, let's check if we have any in-progress milestones in the database
print("\n=== CHECKING DATABASE FOR IN-PROGRESS MILESTONES ===")
try:
    in_progress_milestones = GameMilestone.objects.filter(status='in_progress')
    print(f"Found {in_progress_milestones.count()} milestones with status='in_progress':")
    for m in in_progress_milestones:
        print(f"  - {m.title} (Game: {m.game.title}, Status: {m.status})")
except Exception as e:
    print(f"Error querying database: {str(e)}")

# Create a mock request
class MockRequest:
    def __init__(self):
        self.path = '/test/'

# Call the context processor
print("\n=== CALLING CONTEXT PROCESSOR ===")
request = MockRequest()
context = milestone_info(request)

# Print all context keys
print("\n=== CONTEXT KEYS ===")
print(f"Available keys in context: {', '.join(context.keys())}")

# Print the results
print("\n=== CONTEXT PROCESSOR TEST RESULTS ===")
print(f"milestone_title: {context.get('milestone_title')}")
print(f"game_title: {context.get('game_title')}")
print(f"phase_name: {context.get('phase_name')}")
print(f"phase_type: {context.get('phase_type')}")
print(f"phase_order: {context.get('phase_order')}")

print(f"\nin_progress_milestone: {context.get('in_progress_milestone')}")
if context.get('in_progress_milestone'):
    milestone = context['in_progress_milestone']
    print(f"  title: {milestone.title}")
    print(f"  game: {milestone.game.title}")
    print(f"  status: {milestone.status}")
    print(f"  due_date: {milestone.due_date}")
else:
    print("  No in_progress_milestone object in context")

print(f"\ncompany_phase: {context.get('company_phase')}")
if context.get('company_phase'):
    phase = context['company_phase']
    print(f"  name: {phase.name}")
    print(f"  phase_type: {phase.phase_type}")
    print(f"  order: {phase.order}")
else:
    print("  No company_phase object in context")

print("\n=== DEBUG INFO ===")
if context.get('debug_info'):
    for key, value in context['debug_info'].items():
        print(f"  {key}: {value}")

print("\n=== END OF TEST ===\n")

def test_milestone_context():
    pass

if __name__ == "__main__":
    test_milestone_context()
