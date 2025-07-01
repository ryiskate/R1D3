"""
Example WSGI configuration file for PythonAnywhere.
Copy this content to your WSGI file on PythonAnywhere.
"""
import os
import sys
from pathlib import Path

# Add your project directory to the sys.path
path = '/home/R1D3/R1D3'
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(path) / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Set up Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'company_system.settings'

# Import Django and set up the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
