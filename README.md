

# Setup development environment on linux
1. Create venv ```python -m venv .```
2. Activate venv ```source bin/active.fish```
3. Install dependencies ```pip install .[test] ```
4. Start mongodb ```docker compose up -d```
5. Export mongodb connection string ```set -x MONGO_URI mongodb://root:example@localhost:27017```
6. Start flask ```flask --app logbook_server/ run --debug```

