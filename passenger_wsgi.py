# passenger_wsgi.py

import sys, os

# 1. Projektverzeichnis in sys.path aufnehmen
project_home = os.path.dirname(__file__)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 2. Virtuelle Umgebung aktivieren
activate_env = os.path.join(project_home, 'venv', 'bin', 'activate')
with open(activate_env) as f:
    code = compile(f.read(), activate_env, 'exec')
    exec(code, {'__file__': activate_env})

# 3. Flask-App importieren
from logbook_server import app as application
