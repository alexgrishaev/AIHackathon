"""
WSGI entry point for the application.
This file can be used for deployment on Render.com or other platforms.
It sets up the Python path correctly and then imports the Chainlit handlers.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
print(f"WSGI: Added {project_root} to Python path")

# Import the main Chainlit app
from chainlit_app import *

# This empty file will be found by Chainlit and all handlers from
# chainlit_app.py will be registered automatically
