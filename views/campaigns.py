from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, Campaign
from permissions import is_administrator, is_verified
from upload import allowed_file


campaigns = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


@campaigns.route('', methods=['GET'])
@jwt_required
@is_verified
def ListCampaigns():
    return jsonify([campaign.to_dict() for campaign in Campaign.query.filter_by(is_archived=False)
                    .order_by(Campaign.is_default.desc(), Campaign.id.desc()).all()])


@campaigns.route('', methods=['POST'])
@jwt_required
@is_verified
def CreateCampaign():
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        newCampaign = Campaign(request.form['name'] or None, f'/mediafiles/{secure_filename(file.filename)}')
        if request.form['is_default'] == 'true':
            old_default = Campaign.query.filter_by(is_default=True).all()
            for camp in old_default:
                camp.is_default = False
            newCampaign.is_default = True
        db.session.add(newCampaign)
        db.session.commit()
        file.save(f'/usr/src/app{newCampaign.image}')
        data = jsonify(newCampaign.to_dict())
        data.status_code = 201
        return data
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@campaigns.route('/<id>', methods=['GET'])
@jwt_required
@is_verified
def RetrieveCampaign(id=0):
    return jsonify(Campaign.query.get_or_404(id).to_dict())


@campaigns.route('/<id>', methods=['PATCH'])
@jwt_required
@is_administrator
def UpdateCampaign(id=0):
    campaign = Campaign.query.get_or_404(id)
    try:
        json = request.json
        campaign.name = json['name'] or None
        campaign.is_archived = json['is_archived']
        if json['is_default'] is True:
            old_default = Campaign.query.filter_by(is_default=True).all()
            for camp in old_default:
                camp.is_default = False
            campaign.is_default = True
        else:
            campaign.is_default = False
        db.session.commit()
        return jsonify(campaign.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)


@campaigns.route('/q', methods=['GET'])
@jwt_required
@is_verified
def NameQuery():
    name = request.args.get('name')
    return jsonify(Campaign.query.filter_by(name=name).first_or_404().to_dict())


@campaigns.route('/archived', methods=['GET'])
@jwt_required
@is_verified
def ListArchived():
    return jsonify([campaign.to_dict() for campaign in Campaign.query.filter_by(is_archived=True)
                    .order_by(Campaign.id.desc()).all()])
