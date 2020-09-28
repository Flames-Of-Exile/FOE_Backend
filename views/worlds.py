from flask import current_app, Blueprint, jsonify, request, Response
from werkzeug.utils import secure_filename

from models import db, World
from upload import allowed_file

worlds = Blueprint('worlds', __name__, url_prefix='/api/worlds')

@worlds.route('', methods=['GET'])
def ListWorlds():
    return jsonify([world.to_dict() for world in World.query.all()])

@worlds.route('', methods=['POST'])
def CreateWorld():
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        newWorld = World(request.form['name'], f'/mediafiles/{secure_filename(file.filename)}', request.form['campaign_id'])
        file.save(f'/usr/src/app{newWorld.image}')
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
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        world.name = request.form['name']
        world.image = f'/mediafiles/{secure_filename(file.filename)}'
        world.campaign_id = request.form['campaign_id']
        file.save(f'/usr/src/app{world.image}')
        db.session.commit()
        return jsonify(world.to_dict())
    except:
        return Response('error', status=400, mimetype='application/json')