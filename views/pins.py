from flask import current_app, Blueprint, jsonify, request, Response

from models import db, Pin

pins = Blueprint('pins', __name__, url_prefix='/api/pins')