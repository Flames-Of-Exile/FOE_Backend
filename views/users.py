import re

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt_identity, jwt_required
from passlib.hash import sha256_crypt
from sqlalchemy.exc import IntegrityError

from discord_token import confirm_token, generate_confirmation_token
from models import db, User
from permissions import is_administrator, is_discord_bot, is_member

users = Blueprint('users', __name__, url_prefix='/api/users')


@users.route('', methods=['GET'])
@jwt_required
@is_member
def ListUsers():
    return jsonify([user.to_dict() for user in User.query.all()])


@users.route('', methods=['POST'])
def CreateUser():
    json = request.json
    validation_result = PassComplexityCheck(json['password'])
    if validation_result['password_ok'] is False:
        response = jsonify(validation_result)
        response.status_code = 400
        return response
    try:
        newUser = User(
            json['username'] or None,
            sha256_crypt.encrypt(json['password']) or None
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
        if sha256_crypt.verify(json['password'], user.password):
            data = {}
            data['user'] = user.to_dict()
            data['token'] = create_access_token(identity=user.to_dict())
            response = jsonify(data)
            response.set_cookie('refresh_token', create_refresh_token(identity=user.to_dict()), httponly=True)
            return response
        else:
            return Response('invalid username/password', status=400)
    except (IntegrityError, AttributeError):
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
            user.password = sha256_crypt.encrypt(json['password']) or None
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
    if get_jwt_identity()['id'] == int(id):
        return Response('cannot update your own account', status=403)
    try:
        json = request.json
        if ('password' in json.keys()):
            user.password = sha256_crypt.encrypt(json['password'])
        user.is_active = json['is_active']
        user.role = User.Role(json['role']) or None
        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@users.route('/refresh', methods=['GET'])
def RefreshSession():
    refresh_token = request.cookies.get('refresh_token')
    user = User.query.get(decode_token(refresh_token)['identity']['id'])
    user = user.to_dict()

    data = {}
    data['user'] = user
    data['token'] = create_access_token(identity=user)
    return jsonify(data)


@users.route('/logout', methods=['GET'])
def Logout():
    response = Response("")
    response.delete_cookie('refresh_token')
    return response


@users.route('/confirm', methods=['POST'])
@jwt_required
@is_discord_bot
def ConfirmDiscord():
    json = request.json
    user = User.query.filter_by(username=json['username']).first_or_404()
    token = json['token']
    if user.discord_confirmed is True:
        return Response('user has already confirmed their discord', status=400)
    username = confirm_token(token)
    if username == user.username:
        try:
            user.discord_confirmed = True
            user.discord = json['discord']
            db.session.commit()
            return jsonify(user.to_dict())
        except IntegrityError as error:
            return Response(error.args[0], status=400)
    return Response('invalid user/token', status=400)


@users.route('/discord-token', methods=['GET'])
@jwt_required
def ResendConfirmation():
    user = User.query.get(get_jwt_identity()['id'])
    if user.discord_confirmed is True:
        return Response('user has already confirmed their discord', status=400)
    token = generate_confirmation_token(user.username)
    return jsonify({'token': token})


@users.route('/discord/<discord_id>', methods=['GET'])
@jwt_required
@is_discord_bot
def GetUserByDiscord(discord_id=0):
    user = User.query.filter_by(discord=discord_id).first_or_404()
    return jsonify(user.to_dict())


@users.route('/password-reset/<discord_id>', methods=['PATCH'])
@jwt_required
@is_discord_bot
def ResetPassword(discord_id=0):
    user = User.query.filter_by(discord=discord_id).first_or_404()
    json = request.json
    validation_result = PassComplexityCheck(json['password'])
    if validation_result['password_ok'] is False:
        response = jsonify(validation_result)
        response.status_code = 400
        return response
    try:
        user.password = sha256_crypt.encrypt(json['password'])
        db.session.commit()
        return jsonify(user.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)


def PassComplexityCheck(password):
    # calculating the length
    length_error = (len(password) < 8)

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"\W", password) is None

    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    return {
        'password_ok': password_ok,
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
    }
