from flask import current_app, Blueprint, jsonify, request, Response
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
        newCampaign = Campaign(request.form['name'], f'/mediafiles/{secure_filename(file.filename)}')
        file.save(f'/usr/src/app{newCampaign.image}')
        db.session.add(newCampaign)
        db.session.commit()
        data = jsonify(newCampaign.to_dict())
        data.status_code = 201
        return data
    except:
        return Response('error creating record', status=400)

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
        campaign.name = request.form['name']
        campaign.image = f'/mediafiles/{secure_filename(file.filename)}'
        file.save(f'/usr/src/app{campaign.image}')
        db.session.commit()
        return jsonify(campaign.to_dict())
    except:
        return Response('error updating record', status=400)