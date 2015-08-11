import os
import sys

# We run the app
from app import app as application
print(sys.version)
application.config['DEBUG'] = True