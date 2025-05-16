"""
Simple script to verify that our Python path setup works correctly.
"""

import os
import sys

# Print current Python path
print("Current Python path:")
for path in sys.path:
    print(f" - {path}")

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
print(f"\nAdded {project_root} to Python path")

# Try importing from app package
try:
    from app.models.models import User
    print("\nSuccessfully imported User from app.models.models")
    print(f"User class: {User}")
except ImportError as e:
    print(f"\nFailed to import from app package: {e}")

# Try importing other modules
try:
    from app.database.connection import get_db
    print("\nSuccessfully imported get_db from app.database.connection")
except ImportError as e:
    print(f"\nFailed to import from app.database: {e}")

print("\nTest complete!")
