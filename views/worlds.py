from flask import current_app, Blueprint, jsonify, request, Response

from models import db, World

worlds = Blueprint('worlds', __name__, url_prefix='/api/worlds')