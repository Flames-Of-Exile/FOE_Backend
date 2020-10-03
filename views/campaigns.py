from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from models import db, Campaign
from permissions import is_administrator, is_member
from upload import allowed_file


campaigns = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')

@campaigns.route('', methods=['GET'])
@jwt_required
@is_member
def ListCampaigns():
    return jsonify([campaign.to_dict() for campaign in Campaign.query.all()])

@campaigns.route('', methods=['POST'])
@jwt_required
@is_administrator
def CreateCampaign():
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        newCampaign = Campaign(request.form['name'] or None, f'/mediafiles/{secure_filename(file.filename)}')
        if (request.form['is_default'] == "true"):
            old_default = Campaign.query.filter_by(is_default=True).all()
            for camp in old_default:
                camp.is_default=False
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
@is_member
def RetrieveCampaign(id=0):
    return jsonify(Campaign.query.get_or_404(id).to_dict())

@campaigns.route('/<id>', methods=['PATCH'])
@jwt_required
@is_administrator
def UpdateCampaign(id=0):
    campaign = Campaign.query.get_or_404(id)
    if 'file' not in request.files:
        return Response('no file found', status=400)
    file = request.files['file']
    if not allowed_file(file.filename):
        return Response('invalid file type', status=400)
    try:
        campaign.name = request.form['name'] or None
        if (request.form['is_default'] == "true"):
            old_default = Campaign.query.filter_by(is_default=True).all()
            for camp in old_default:
                camp.is_default=False
            campaign.is_default = True
        campaign.image = f'/mediafiles/{secure_filename(file.filename)}'
        db.session.commit()
        file.save(f'/usr/src/app{campaign.image}')
        return jsonify(campaign.to_dict())
    except IntegrityError as error:
        return Response(error.args[0], status=400)

@campaigns.route('/latest', methods=['GET'])
@jwt_required
@is_member
def GetLatest():
    campaign = Campaign.query.filter_by(is_default=True).first()
    if campaign is not None:
        return jsonify(campaign.to_dict())
    return Response('no default campaign found', status=404)