from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.config['SCERET KEY'] = 'cwvwewrwbrbrbbbhunjnsuidueivireirebvh'
    app.secret_key = 'dsc324dwfgwewvvddsvdsvsdvbbfbeebevevefv'
    # Set session configuration for the app
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = 'session_data'
    # Initialize Flask-Session
    Session(app)
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    return app