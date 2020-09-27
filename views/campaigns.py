from flask import current_app, Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import db, Campaign
from permissions import is_administrator, is_member

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
    json = request.json
    try:
        newCampaign = Campaign(json['name'], json['image'])
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
    try:
        json = request.json
        campaign.name = json['name']
        campaign.image = json['image']
        db.session.commit()
        return jsonify(campaign.to_dict())
    except:
        return Response('error updating record', status=400)