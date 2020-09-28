from flask import current_app, Blueprint, jsonify, request, Response
from werkzeug.utils import secure_filename

from models import db, Campaign
from upload import allowed_file

campaigns = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')

@campaigns.route('', methods=['GET'])
def ListCampaigns():
    return jsonify([campaign.to_dict() for campaign in Campaign.query.all()])

@campaigns.route('', methods=['POST'])
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
        return Response("success", status=201, mimetype='application/json')
    except:
        return Response("error", status=400, mimetype='application/json')

@campaigns.route('/<id>', methods=['GET'])
def RetrieveCampaign(id=0):
    return jsonify(Campaign.query.get_or_404(id).to_dict())

@campaigns.route('/<id>', methods=['PATCH'])
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
        return Response('error', status=400, mimetype='application/json')