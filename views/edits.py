from flask import current_app, Blueprint, jsonify, request, Response

from models import db, Edit

edits = Blueprint('edits', __name__, url_prefix='/api/edits')