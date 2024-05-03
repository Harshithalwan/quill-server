
from flask import Flask
from .routes.main_routes import main_bp
from .routes.api_routes import api_bp
from .socketio.socketio_config import socketio

def create_app():
    # Create the Flask app instance
    app = Flask(__name__)

    # Configuration settings (optional)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Initialize Socket.IO
    socketio.init_app(app)
    app.debug = True
    return app