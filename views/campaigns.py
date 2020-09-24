from flask import current_app, Blueprint, jsonify, request, Response

from models import db, Campaign

campaigns = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')