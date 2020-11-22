import os

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, Campaign, World
from permissions import is_administrator, is_verified
from upload import allowed_file


worlds = Blueprint('worlds', __name__, url_prefix='/api/worlds')


@worlds.route('', methods=['GET'])
@jwt_required
@is_verified
def ListWorlds():
    return jsonify([world.to_dict() for world in World.query.all()])


@worlds.route('', methods=['POST'])
@jwt_required
@is_verified
def CreateWorld():
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        campaignName = Campaign.query.get(request.form['campaign_id']).name.replace(' ', '_')
        newWorld = World(
            request.form['name'] or None,
            f'/mediafiles/campaigns/{campaignName}/{secure_filename(file.filename)}',
            request.form['center_lat'],
            request.form['center_lng'],
            request.form['radius'],
            request.form['campaign_id'] or None
            )
        db.session.add(newWorld)
        db.session.commit()
        os.makedirs(f'/usr/src/app/mediafiles/campaigns/{campaignName}/{newWorld.name}', exist_ok=True)
        file.save(f'/usr/src/app{newWorld.image}')
        data = jsonify(newWorld.to_dict())
        data.status_code = 201
        return data
    except (IntegrityError, AttributeError) as error:
        return Response(error.args[0], status=400)


@worlds.route('/<id>', methods=['GET'])
@jwt_required
@is_verified
def RetrieveWorld(id=0):
    return jsonify(World.query.get_or_404(id).to_dict())


@worlds.route('/<id>', methods=['PATCH'])
@jwt_required
@is_administrator
def UpdateWorld(id=0):
    world = World.query.get_or_404(id)
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        world.name = request.form['name'] or None
        world.campaign_id = request.form['campaign_id'] or None
        campaignName = Campaign.query.get(world.campaign_id).name
        world.image = f'/mediafiles/campaigns/{campaignName}/{secure_filename(file.filename)}'
        world.center_lat = request.form['center_lat']
        world.center_lng = request.form['center_lng']
        world.radius = request.form['radius']
        db.session.commit()
        file.save(f'/usr/src/app{world.image}')
        os.mkdir(f'/usr/src/app/mediafiles/campaigns/{campaignName}/{world.name}')
        return jsonify(world.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@worlds.route('/q', methods=['GET'])
@jwt_required
@is_verified
def NameQuery():
    campaign_name = request.args.get('campaign')
    world_name = request.args.get('world')
    return jsonify(World.query.join(Campaign)
                   .filter(Campaign.name == campaign_name, World.name == world_name)
                   .first_or_404().to_dict())
