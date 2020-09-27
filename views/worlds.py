from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required

from models import db, World
from permissions import is_administrator, is_member

worlds = Blueprint('worlds', __name__, url_prefix='/api/worlds')

@worlds.route('', methods=['GET'])
@jwt_required
@is_member
def ListWorlds():
    return jsonify([world.to_dict() for world in World.query.all()])

@worlds.route('', methods=['POST'])
@jwt_required
@is_administrator
def CreateWorld():
    json = request.json
    try:
        newWorld = World(json['name'], json['image'], json['campaign']['id'])
        db.session.add(newWorld)
        db.session.commit()
        data = jsonify(newWorld.to_dict())
        data.status_code = 201
        return data
    except:
        return Response('error creating record', status=400)

@worlds.route('/<id>', methods=['GET'])
@jwt_required
@is_member
def RetrieveWorld(id=0):
    return jsonify(World.query.get_or_404(id).to_dict())

@worlds.route('/<id>', methods=['PATCH'])
@jwt_required
@is_administrator
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
        return Response('error updating record', status=400)