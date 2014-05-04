import os
import sys

# add this directory to the Python search path
sys.path.append(os.path.dirname(__file__))

from server import app as application
