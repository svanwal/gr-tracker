from flask import Blueprint

bp = Blueprint('trails', __name__)

from app.trails import routes
