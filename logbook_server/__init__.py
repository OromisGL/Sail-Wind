import os

from flask import Flask
from .db import init_app
import threading


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config["UPLOAD_FOLDER"] = 'uploads'
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")),
        

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import track
    app.register_blueprint(track.bp)
    app.add_url_rule('/', endpoint='track.map')
    
    # make the register for the Data Fetch here
    from .map_utils import map_utils_bp, weather_updater
    app.register_blueprint(map_utils_bp, url_prefix='/track')
    
    # make a injection for the frontend to loop over the lake Data
    from .map_utils import get_lake_data
    get_lake_data(app)
    
    threading.Thread(target=weather_updater, daemon=True).start()
    
    return app