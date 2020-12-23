from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
import logging
import sys

from models import db, Event
from permissions import is_administrator, is_verified

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)

calendar = Blueprint('calendar', __name__, url_prefix='/api/calendar')

@calendar.route('', methods=['GET'])
@jwt_required
@is_verified
def get_all_events():
    return jsonify([event.to_dict() for event in Event.query.all()])

@calendar.route('', methods=['POST'])
@jwt_required
@is_administrator
def create_new_event():
    if 'name' not in request.json:
        return Response('name not found', status=401)
    if 'game' not in request.json:
        return Response('game not found', status=402)
    if 'when' not in request.json:
        return Response('when not found', status=403)
    if 'note' not in request.json:
        return Response('note not found', status=405)
    event = request.json
    new_event = Event(event['name'], event['game'], event['when'], event['note'])
    db.session.add(new_event)
    db.session.commit()
    data = jsonify(new_event.to_dict())
    data.status_code = 201
    return data
    # except IntegrityError as error:
    #     return Response(error.args[0], status=400)
    # except KeyError as error:
    #     log.info(error)
    #     return Response(error.args[0], status=418)