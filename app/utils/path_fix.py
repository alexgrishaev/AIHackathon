"""
This file helps with Python path issues by ensuring the project root
is in the Python path so that imports like 'from app.models.xyz' work correctly.

Usage:
Import this at the beginning of your entry point scripts:

import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""

import os
import sys

# Get the project root directory (parent directory of this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to Python path if not already there
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
