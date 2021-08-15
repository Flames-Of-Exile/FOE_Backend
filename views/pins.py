from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from models import db, Edit, Pin, User
from permissions import is_verified

pins = Blueprint('pins', __name__, url_prefix='/api/pins')


@pins.route('', methods=['GET'])
@jwt_required
@is_verified
def ListPins():
    return jsonify([pin.to_dict() for pin in Pin.query.all()])


@pins.route('', methods=['POST'])
@jwt_required
@is_verified
def CreatePin():
    json = request.json
    try:
        newPin = Pin(
            json['position_x'],
            json['position_y'],
            Pin.Symbol(json['symbol']),
            Pin.Resource(json['resource']),
            json['world_id'] or None,
            json['rank'],
            json['name'],
            json['amount'],
            json['respawn'],
            json['notes'],
            json['x_cord'],
            json['y_cord']
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
@is_verified
def RetrievePin(id=0):
    return jsonify(Pin.query.get_or_404(id).to_dict())


@pins.route('/<id>', methods=['PATCH'])
@jwt_required
@is_verified
def UpdatePin(id=0):
    pin = Pin.query.get_or_404(id)
    user = get_jwt_identity()
    if (User.Role(user['role']) not in [User.Role.ADMIN, User.Role.VERIFIED]) and (user['id'] != pin.edits[0].user_id):
        return Response('only the creator or an admin can edit a pin', status=403)
    try:
        json = request.json
        details = ''
        PROPERTY_LIST = ['position_x', 'position_y', 'symbol', 'resource', 'rank', 'name',
                         'amount', 'respawn', 'notes', 'x_cord', 'y_cord']
        for prop in PROPERTY_LIST:
            old_value = getattr(pin, prop)
            enum = False
            if hasattr(old_value, 'value'):
                old_value = old_value.value
                enum = True
            if old_value != json[prop]:
                details += f'{prop} changed from {old_value} to {json[prop]}\n'
                if enum is True:
                    if json[prop] in [item.value for item in Pin.Symbol]:
                        setattr(pin, prop, Pin.Symbol(json[prop]))
                    elif json[prop] in [item.value for item in Pin.Resource]:
                        setattr(pin, prop, Pin.Resource(json[prop]))
                else:
                    setattr(pin, prop, json[prop])
        db.session.commit()
        newEdit = Edit(details, pin.id, get_jwt_identity()['id'])
        db.session.add(newEdit)
        db.session.commit()
        return jsonify(pin.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@pins.route('/<id>', methods=['DELETE'])
@jwt_required
@is_verified
def DeletePin(id=0):
    pin = Pin.query.get_or_404(id)
    creator_id = pin.edits[0].user_id
    user = get_jwt_identity()
    if User.Role(user['role']) == User.Role.ADMIN or user['id'] == creator_id:
        db.session.delete(pin)
        db.session.commit()
        return Response('pin deleted', status=200)
    return Response('only the creator or an admin can delete a pin', status=403)
