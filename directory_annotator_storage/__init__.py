import os
from flask import Flask
from flask_cors import CORS

from directory_annotator_storage.constants_config import (
    SODUCO_SETTINGS, SECRET_KEY_PATH, TOKENS, DEBUG_TOKEN)


def _load_secret_tokens(path_secret_key):
    tokens = []
    if path_secret_key and os.path.exists(path_secret_key):
        with open(path_secret_key, 'r') as tokens_file:
            for line in tokens_file.readlines():
                # Remove trailing whitespace
                line = line.rstrip()
                # Remove comments and empty lines
                if not line.startswith('#') and len(line) > 0:
                    tokens.append(line)
    return tokens


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app,
         headers=['Content-Type', 'Authorization'], 
         expose_headers='Authorization')

    # Main configuration
    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile("config.py", silent=True)
        app.config.from_envvar(SODUCO_SETTINGS, silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)
        app.logger.warning("Got test configuration; ignoring configuration from env var 'SODUCO_SETTINGS'.")
    
    # Authentication configuration
    path_secret_key = app.config.get(SECRET_KEY_PATH, None)
    tokens = _load_secret_tokens(path_secret_key)
    app.config[TOKENS] = tokens

    if app.debug or app.testing:
        tokens.append(DEBUG_TOKEN)
        app.logger.warning(f"Adding debug token {DEBUG_TOKEN} to authorized tokens.")

    # Apply the blueprints to the app
    from directory_annotator_storage import health_check
    app.register_blueprint(health_check.bp)
    from directory_annotator_storage import directories
    app.register_blueprint(directories.bp)

    return app
