from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from models import db, Guild
from permissions import is_administrator, is_discord_bot

guilds = Blueprint('guilds', __name__, url_prefix='/api/guilds')


@guilds.route('', methods=['GET'])
def ListGuilds():
    guild_list = [Guild.query.filter_by(name='Flames of Exile').first().to_dict()]
    guild_list += [guild.to_dict() for guild in Guild.query.filter(Guild.name != 'Flames of Exile')
                   .order_by(Guild.is_active.desc(), Guild.name).all()]
    return jsonify(guild_list)


@guilds.route('', methods=['POST'])
@jwt_required
@is_administrator
def CreateGuild():
    json = request.json
    try:
        newGuild = Guild(json['name'])
        db.session.add(newGuild)
        db.session.commit()
        data = jsonify(newGuild.to_dict())
        data.status_code = 201
        return data
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@guilds.route('/<id>', methods=['GET'])
def RetrieveGuild(id=0):
    return jsonify(Guild.query.get_or_404(id).to_dict())


@guilds.route('/<id>', methods=['PATCH'])
@jwt_required
@is_administrator
def UpdateGuild(id=0):
    guild = Guild.query.get_or_404(id)
    if guild.name == 'Flames of Exile':
        return Response('no editing the main guild', status=400)
    json = request.json
    try:
        guild.name = json['name'] or None
        guild.is_active = json['is_active']
        db.session.add(guild)
        db.session.commit()
        return jsonify(guild.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@guilds.route('/q', methods=['GET'])
def NameQuery():
    name = request.args.get('name')
    return jsonify(Guild.query.filter_by(name=name).first_or_404().to_dict())


@guilds.route('/burn', methods=['PATCH'])
@jwt_required
@is_discord_bot
def burn_guild():
    guild = Guild.query.filter_by(name=request.json['guild']).first_or_404()
    guild.is_active = False
    db.session.commit()
    users = [int(user.discord) for user in guild.users]
    return jsonify(users)


@guilds.route('/unburn', methods=['PATCH'])
@jwt_required
@is_discord_bot
def unburn_guild():
    guild = Guild.query.filter_by(name=request.json['guild']).first_or_404()
    guild.is_active = True
    db.session.commit()
    users = [int(user.discord) for user in guild.users]
    return jsonify(users)
