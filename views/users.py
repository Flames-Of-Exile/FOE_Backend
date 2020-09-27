import hashlib
from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from models import db, User
from permissions import is_administrator, is_member

users = Blueprint('users', __name__, url_prefix='/api/users')

@users.route('', methods=['GET'])
@jwt_required
@is_member
def ListUsers():
    return jsonify([user.to_dict() for user in User.query.all()])

@users.route('', methods=['POST'])
def CreateUser():
    json = request.json
    try:
        newUser = User(json['username'], hashlib.md5(json['password'].encode()).hexdigest(), json['email'])
        db.session.add(newUser)
        db.session.commit()
        data = {}
        data['user'] = newUser.to_dict()
        data['token'] = create_access_token(identity=newUser.to_dict())
        data = jsonify(data)
        data.status_code = 201
        return data
    except:
        return Response('error creating record', status=400)

@users.route('/login', methods=['POST'])
def Login():
    json = request.json
    try:
        user = User.query.filter_by(username=json['username']).first()
        if (user.password == hashlib.md5(json['password'].encode()).hexdigest()):
            data = {}
            data['user'] = user.to_dict() 
            data['token'] = create_access_token(identity=user.to_dict())
            return jsonify(data)
        else:
            return Response('invalid username/password', status=400)
    except:
        return Response('invalid username/password', status=400)
      
@users.route('/<id>', methods=['GET'])
@jwt_required
@is_member
def RetrieveUser(id=0):
    return jsonify(User.query.get_or_404(id).to_dict())

@users.route('/<id>', methods=['PATCH'])
@jwt_required
def UpdateUser(id=0):
    user = User.query.get_or_404(id)
    if (get_jwt_identity()['id'] != id):
        return Response('can only update your own account', status=403)
    try:
        json = request.json
        user.password = hashlib.md5(json['password'].encode()).hexdigest()
        user.email = json['email']
        db.session.commit()
        return jsonify(user.to_dict())
    except:
        return Response('error updating record', status=400)

@users.route('/<id>', methods=['PUT'])
@jwt_required
@is_administrator
def AdminUpdateUser(id=0):
    user = User.query.get_or_404(id)
    try:
        json = request.json
        user.password = hashlib.md5(json['password'].encode()).hexdigest()
        user.email = json['email']
        user.is_active = json['is_active']
        user.role = User.Role(json['role'])
        db.session.commit()
        return jsonify(user.to_dict())
    except:
        return Response('error updating record', status=400)