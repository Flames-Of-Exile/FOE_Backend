import hashlib
from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

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
        newUser = User(
            json['username'] or None, 
            hashlib.md5(json['password'].encode()).hexdigest() or None, 
            json['email'] or None
            )
        db.session.add(newUser)
        db.session.commit()
        data = {}
        data['user'] = newUser.to_dict()
        data['token'] = create_access_token(identity=newUser.to_dict())
        data = jsonify(data)
        data.set_cookie('refresh_token', create_refresh_token(identity=newUser.to_dict()), httponly=True)
        data.status_code = 201
        return data
    except IntegrityError as error:
        return Response(error.args[0], status=400)

@users.route('/login', methods=['POST'])
def Login():
    json = request.json
    try:
        user = User.query.filter_by(username=json['username']).first()
        if (user.password == hashlib.md5(json['password'].encode()).hexdigest()):
            data = {}
            data['user'] = user.to_dict() 
            data['token'] = create_access_token(identity=user.to_dict())
            response = jsonify(data)
            response.set_cookie('refresh_token', create_refresh_token(identity=user.to_dict()), httponly=True)
            return response
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
    if (get_jwt_identity()['id'] != int(id)):
        return Response('can only update your own account', status=403)
    try:
        json = request.json
        if 'password' in json.keys():
            user.password = hashlib.md5(json['password'].encode()).hexdigest() or None
        user.email = json['email'] or None
        user.theme = User.Theme(json['theme']) or None
        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)

@users.route('/<id>', methods=['PUT'])
@jwt_required
@is_administrator
def AdminUpdateUser(id=0):
    user = User.query.get_or_404(id)
    try:
        json = request.json
        user.password = hashlib.md5(json['password'].encode()).hexdigest() or None
        user.email = json['email'] or None
        user.is_active = json['is_active']
        user.role = User.Role(json['role']) or None
        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)

@users.route('/refresh', methods=['GET'])
def RefreshSession():
    refresh_token = request.cookies.get('refresh_token')
    user = decode_token(refresh_token)['identity']

    data = {}
    data['user'] = user
    data['token'] = create_access_token(identity=user)
    return jsonify(data)

@users.route('/logout', methods=['GET'])
def Logout():
    response = Response("")
    response.delete_cookie('refresh_token')
    return response