import os
import sys

# Add the project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    from core.wsgi import application
    print("Successfully loaded WSGI application!")
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    import traceback
    traceback.print_exc()