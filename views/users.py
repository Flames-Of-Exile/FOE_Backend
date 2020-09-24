from flask import current_app, Blueprint, jsonify, request, Response

from models import db, User

users = Blueprint('users', __name__, url_prefix='/api/users')

@users.route('/', methods=['GET'])
def ListUsers():
    return jsonify([user.to_dict() for user in User.query.all()])

@users.route('/', methods=['POST'])
def CreateUser():
    json = request.json
    try:
        newUser = User(json['username'], json['password'], json['email'])
        db.session.add(newUser)
        db.session.commit()
        return Response("success", status=201, mimetype='application/json')
    except:
        return Response("error", status=400, mimetype='application/json')