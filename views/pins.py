from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import db, Edit, Pin
from permissions import is_administrator, is_member

pins = Blueprint('pins', __name__, url_prefix='/api/pins')

@pins.route('', methods=['GET'])
@jwt_required
@is_member
def ListPins():
    return jsonify([pin.to_dict() for pin in Pin.query.all()])

@pins.route('', methods=['POST'])
@jwt_required
@is_member
def CreatePin():
    json = request.json
    try:
        newPin = Pin(json['position_x'], json['position_y'], json['symbol'], json['world_id'])
        db.session.add(newPin)
        db.session.commit()
        newEdit = Edit(json['details'], newPin.id, get_jwt_identity()['id'])
        db.session.add(newEdit)
        db.session.commit()
        data = jsonify(newPin.to_dict())
        data.status_code = 201
        return data
    except:
        return Response('error creating record', status=400)

@pins.route('/<id>', methods=['GET'])
@jwt_required
@is_member
def RetrievePin(id=0):
    return jsonify(Pin.query.get_or_404(id).to_dict())

@pins.route('/<id>', methods=['PATCH'])
@jwt_required
@is_member
def UpdatePin(id=0):
    pin = Pin.query.get_or_404(id)
    try:
        json = request.json
        details = ''
        if (pin.position_x != json['position_x'] or pin.position_y != json['position_y']):
            details += f'Position changed from {pin.position_x}/{pin.position_y} to {json["position_x"]}/{json["position_y"]}\n'
        pin.position_x = json['position_x']
        pin.position_y = json['position_y']
        if (pin.symbol != json['symbol']):
            details += f'Symbol changed from {pin.symbol} to {json["symbol"]}\n'
            pin.symbol = json['symbol']
        db.session.commit()
        newEdit = Edit(details, pin.id, get_jwt_identity()['id'])
        db.session.add(newEdit)
        db.session.commit()
        return jsonify(pin.to_dict())
    except:
        return Response('error updating record', status=400)