from flask import current_app, Blueprint, jsonify, request, Response

from models import db, Edit

edits = Blueprint('edits', __name__, url_prefix='/api/edits')

@edits.route('', methods=['GET'])
def ListEdits():
    return jsonify([edit.to_dict() for edit in Edit.query.all()])

@edits.route('', methods=['POST'])
def CreateEdit():
    json = request.json
    #try:
    newEdit = Edit(json['details'], json['pin']['id'], json['user']['id'])
    db.session.add(newEdit)
    db.session.commit()
    return Response("success", status=201, mimetype='application/json')
    #except:
    #    return Response("error", status=400, mimetype='application/json')

@edits.route('/<id>', methods=['GET'])
def RetrieveEdit(id=0):
    return jsonify(Edit.query.get_or_404(id).to_dict())