from flask import current_app, Blueprint, jsonify, request, Response

from models import db, User

users = Blueprint('users', __name__, url_prefix='/api/users')

@users.route('', methods=['GET'])
def ListUsers():
    return jsonify([user.to_dict() for user in User.query.all()])

@users.route('', methods=['POST'])
def CreateUser():
    json = request.json
    try:
        newUser = User(json['username'], json['password'], json['email'])
        db.session.add(newUser)
        db.session.commit()
        return Response("success", status=201, mimetype='application/json')
    except:
        return Response("error", status=400, mimetype='application/json')

@users.route('/<id>', methods=['GET'])
def RetrieveUser(id=0):
    return jsonify(User.query.get_or_404(id).to_dict())

@users.route('/<id>', methods=['PATCH'])
def UpdateUser(id=0):
    user = User.query.get_or_404(id)
    try:
        json = request.json
        user.username = json['username']
        user.password = json['password']
        user.email = json['email']
        db.session.commit()
        return jsonify(user.to_dict())
    except:
        return Response('error', status=400, mimetype='application/json')