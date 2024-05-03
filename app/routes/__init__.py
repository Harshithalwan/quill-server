
from flask import Blueprint

# Create a Blueprint instance for main routes
main_bp = Blueprint('main', __name__)

# Import routes from main_routes.py to register with main_bp
from .main_routes import *

# Create a Blueprint instance for API routes
api_bp = Blueprint('api', __name__)

# Import routes from api_routes.py to register with api_bp
from .api_routes import *