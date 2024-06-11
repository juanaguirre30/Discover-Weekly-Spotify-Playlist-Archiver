# wsgi.py

# This file is used to configure PythonAnywhere to serve your Flask app.
# It tells PythonAnywhere where to find your app and how to run it.

import sys
path = '/home/juanaguirre158/<repository-directory>'
if path not in sys.path:
    sys.path.append(path)

from spotifyWeekly import app as application  # Replace 'your_flask_app' with the name of your Flask app file (e.g., app.py)
