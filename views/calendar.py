from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
import logging
import os
import sys
import datetime
import pytz
from datetime import timedelta

from models import db, Event
from permissions import is_administrator, is_verified, is_discord_bot


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log.addHandler(handler)
BOT_URL = os.getenv('BOT_URL') + '/bot'
VERIFY_SSL = os.getenv('VERIFY_SSL')
timezone = pytz.utc

calendar = Blueprint('calendar', __name__, url_prefix='/api/calendar')

@calendar.route('', methods=['GET'])
@jwt_required
@is_verified
def get_all_events():
    events = Event.query.order_by(Event.active.desc()).order_by(Event.date).all()
    for event in events:
        event.date = timezone.localize(event.date)
        log.info(f'{event.name}:{event.date}')
    return jsonify([event.to_dict() for event in events])

@calendar.route('', methods=['POST'])
@jwt_required
@is_administrator
def create_new_event():
    if 'name' not in request.json:
        return Response('name not found', status=400)
    if 'game' not in request.json:
        return Response('game not found', status=400)
    if 'date' not in request.json:
        return Response('when not found', status=400)
    if 'note' not in request.json:
        return Response('note not found', status=400)
    event = request.json
    log.info(event['date'])
    log.info(type(event['date']))
    new_event = Event(event['name'], event['game'], event['date'], event['note'])
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

@calendar.route('/<id>', methods=['PATCH'])
@jwt_required
@is_administrator
def alter_event(id):
    event = Event.query.filter_by(id=id).first_or_404()
    json = request.json
    if 'name' in json:
        event.name = json['name']
    if 'game' in json:
        event.game = json['game']
    if 'date' in json:
        event.date = json['date']
        log.info(event.date)
    if 'note' in json:
        event.note = json['note']
    log.info(json['date'])
    db.session.commit()
    data = jsonify(event.to_dict())
    data.status_code = 201
    return data

@calendar.route('/<id>', methods=['DELETE'])
@jwt_required
@is_administrator
def remove_event(id):
    event = Event.query.filter_by(id=id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    data = jsonify(event.to_dict())
    data.status_code = 204
    return data

@calendar.route('/getevents', methods=['GET'])
@jwt_required
@is_discord_bot
def notify_events():
    day = datetime.datetime.now()
    log.info(day)
    events = Event.query.filter_by(active=True).all()
    todays_events = []
    for event in events:
        if event.date.date() < day.date():
            event.active = False
        elif event.date < day + timedelta(hours=24):
            # event.date = pytz.utc(event.date)
            todays_events.append(event.to_dict())
    db.session.commit()
    data = jsonify(todays_events)
    data.status_code = 200
    return data
