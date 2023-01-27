from flask import Blueprint

bp = Blueprint('hikes', __name__)

from app.hikes import routes
