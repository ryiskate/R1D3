import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # First test settings import
    from company_system import settings
    print("Successfully imported settings")
    
    # Then test wsgi import
    from company_system.wsgi import application
    print("Successfully imported WSGI application")
    
    # Check if application is callable
    if callable(application):
        print("WSGI application is callable")
    else:
        print("WSGI application is not callable")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
