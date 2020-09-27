from flask import current_app, Blueprint, jsonify, request, Response

from models import db, Campaign

campaigns = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')

@campaigns.route('', methods=['GET'])
def ListCampaigns():
    return jsonify([campaign.to_dict() for campaign in Campaign.query.all()])

@campaigns.route('', methods=['POST'])
def CreateCampaign():
    json = request.json
    try:
        newCampaign = Campaign(json['name'], json['image'])
        db.session.add(newCampaign)
        db.session.commit()
        return Response("success", status=201, mimetype='application/json')
    except:
        return Response("error", status=400, mimetype='application/json')

@campaigns.route('/<id>', methods=['GET'])
def RetrieveCampaign(id=0):
    return jsonify(Campaign.query.get_or_404(id).to_dict())

@campaigns.route('/<id>', methods=['PATCH'])
def UpdateCampaign(id=0):
    campaign = Campaign.query.get_or_404(id)
    try:
        json = request.json
        campaign.name = json['name']
        campaign.image = json['image']
        db.session.commit()
        return jsonify(campaign.to_dict())
    except:
        return Response('error', status=400, mimetype='application/json')