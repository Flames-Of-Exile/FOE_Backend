import hashlib
from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token, jwt_required

from models import db, User

users = Blueprint('users', __name__, url_prefix='/api/users')

@users.route('', methods=['GET'])
def ListUsers():
    return jsonify([user.to_dict() for user in User.query.all()])

@users.route('', methods=['POST'])
@jwt_required
def CreateUser():
    json = request.json
    try:
        newUser = User(json['username'], hashlib.md5(json['password'].encode()).hexdigest(), json['email'])
        db.session.add(newUser)
        db.session.commit()
        data = jsonify(newUser.to_dict())
        data.status_code = 201
        return data
    except:
        return Response("error", status=400, mimetype='application/json')

@users.route('/login', methods=['POST'])
def Login():
    json = request.json
    try:
        user = User.query.filter_by(username=json['username']).first()
        if (user.password == hashlib.md5(json['password'].encode()).hexdigest()):
            data = user.to_dict()
            data['token'] = create_access_token(identity=data)
            return jsonify(data)
        else:
            return Response('error', status=400, mimetype='application/json')
    except:
        return Response('error', status=400, mimetype='application/json')
