import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from company_system import settings
    print("Successfully imported settings")
except Exception as e:
    print(f"Error importing settings: {e}")
    import traceback
    traceback.print_exc()
