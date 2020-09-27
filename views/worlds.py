from flask import current_app, Blueprint, jsonify, request, Response

from models import db, World

worlds = Blueprint('worlds', __name__, url_prefix='/api/worlds')

@worlds.route('', methods=['GET'])
def ListWorlds():
    return jsonify([world.to_dict() for world in World.query.all()])

@worlds.route('', methods=['POST'])
def CreateWorld():
    json = request.json
    try:
        newWorld = World(json['name'], json['image'], json['campaign']['id'])
        db.session.add(newWorld)
        db.session.commit()
        return Response("success", status=201, mimetype='application/json')
    except:
        return Response("error", status=400, mimetype='application/json')

@worlds.route('/<id>', methods=['GET'])
def RetrieveWorld(id=0):
    return jsonify(World.query.get_or_404(id).to_dict())

@worlds.route('/<id>', methods=['PATCH'])
def UpdateWorld(id=0):
    world = World.query.get_or_404(id)
    try:
        json = request.json
        world.name = json['name']
        world.image = json['image']
        world.campaign_id = json['campaign']['id']
        db.session.commit()
        return jsonify(world.to_dict())
    except:
        return Response('error', status=400, mimetype='application/json')