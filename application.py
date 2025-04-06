import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app

# Create the application instance
application = create_app()

# This is needed for Gunicorn
app = application

if __name__ == '__main__':
    application.run() 