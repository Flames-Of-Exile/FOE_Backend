from flask import current_app, Blueprint, jsonify, request, Response

from models import db, Pin

pins = Blueprint('pins', __name__, url_prefix='/api/pins')

@pins.route('', methods=['GET'])
def ListPins():
    return jsonify([pin.to_dict() for pin in Pin.query.all()])

@pins.route('', methods=['POST'])
def CreatePin():
    json = request.json
    try:
        newPin = Pin(json['position_x'], json['position_y'], json['symbol'], json['world']['id'])
        db.session.add(newPin)
        db.session.commit()
        return Response("success", status=201, mimetype='application/json')
    except:
        return Response("error", status=400, mimetype='application/json')

@pins.route('/<id>', methods=['GET'])
def RetrievePin(id=0):
    return jsonify(Pin.query.get_or_404(id).to_dict())

@pins.route('/<id>', methods=['PATCH'])
def UpdatePin(id=0):
    pin = Pin.query.get_or_404(id)
    try:
        json = request.json
        pin.position_x = json['position_x']
        pin.position_y = json['position_y']
        pin.symbol = json['symbol']
        pin.world_id = json['world']['id']
        db.session.commit()
        return jsonify(pin.to_dict())
    except:
        return Response('error', status=400, mimetype='application/json')