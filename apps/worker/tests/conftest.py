import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up any test-wide fixtures here if needed
