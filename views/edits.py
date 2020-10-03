from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from models import db, Edit
from permissions import is_administrator, is_member

edits = Blueprint('edits', __name__, url_prefix='/api/edits')

@edits.route('', methods=['GET'])
@jwt_required
@is_member
def ListEdits():
    return jsonify([edit.to_dict() for edit in Edit.query.all()])

@edits.route('', methods=['POST'])
@jwt_required
@is_member
def CreateEdit():
    json = request.json
    try:
        newEdit = Edit(
            json['details'] or None, 
            json['pin_id'] or None, 
            get_jwt_identity()['id']
            )
        db.session.add(newEdit)
        db.session.commit()
        data = jsonify(newEdit.to_dict())
        data.status_code = 201
        return data
    except IntegrityError as error:
        return Response(error.args[0], status=400)

@edits.route('/<id>', methods=['GET'])
@jwt_required
@is_member
def RetrieveEdit(id=0):
    return jsonify(Edit.query.get_or_404(id).to_dict())