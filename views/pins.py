from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

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
        newPin = Pin(
            json['position_x'], 
            json['position_y'], 
            Pin.Symbol(json['symbol']), 
            json['world_id'] or None,
            json['rank'],
            json['name'] or None,
            json['amount'],
            json['respawn'],
            json['notes'] or None
            )
        db.session.add(newPin)
        db.session.commit()
        newEdit = Edit(json['notes'], newPin.id, get_jwt_identity()['id'])
        db.session.add(newEdit)
        db.session.commit()
        data = jsonify(newPin.to_dict())
        data.status_code = 201
        return data
    except IntegrityError as error:
        return Response(error.args[0], status=400)

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
        if pin.position_x != json['position_x'] or pin.position_y != json['position_y']:
            details += f'Position changed from {pin.position_x}/{pin.position_y} to {json["position_x"]}/{json["position_y"]}\n'
        pin.position_x = json['position_x']
        pin.position_y = json['position_y']
        if pin.symbol != json['symbol']:
            details += f'Symbol changed from {pin.symbol.value} to {json["symbol"]}\n'
            pin.symbol = Pin.Symbol(json['symbol'])
        if pin.rank != json['rank']:
            details += f'Rank changed from {pin.rank} to {json["rank"]}\n'
            pin.rank = json['rank']
        if pin.name != json['name']:
            details += f'Name changed from {pin.name} to {json["name"]}]n'
            pin.name = json['name']
        if pin.amount != json['amount']:
            details += f'Amount changed from {pin.amount} to {json["amount"]}\n'
            pin.amount = json['amount']
        if pin.respawn != json['respawn']:
            details += f'Respawn changed from {pin.respawn} to {json["respawn"]}\n'
            pin.respawn = json['respawn']
        if pin.notes != json['notes']:
            details += f'Notes changed from {pin.notes} to {json["notes"]}\n'
            pin.notes = json['notes']
        db.session.commit()
        newEdit = Edit(details, pin.id, get_jwt_identity()['id'])
        db.session.add(newEdit)
        db.session.commit()
        return jsonify(pin.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)

@pins.route('/<id>', methods=['DELETE'])
@jwt_required
@is_administrator
def DeletePin(id=0):
    pin = Pin.query.get_or_404(id)
    db.session.delete(pin)
    db.session.commit()
    return Response('pin deleted', status=200)
