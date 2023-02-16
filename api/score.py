from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime

from model.snake import Score

score_api = Blueprint('score_api', __name__,
                   url_prefix='/api/scores')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(score_api)

class ScoreAPI:        
    class _Create(Resource):
        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            score = body.get('score')
            if score is None:
                return {'message': f'Score is missing'}, 210
            # validate uid
            uid = body.get('uid')
            if uid is None or len(uid) < 1:
                return {'message': f'User ID is missing'}, 210
           
            so = Score(score=score, 
                      uid=uid)
            
            # create score in database
            scoreObj = so.create()
            # success returns json of user
            if scoreObj:
                return jsonify(scoreObj.read())
            # failure returns error
            return {'message': f'Processed {score}, either a format error or User ID {uid} is wrong'}, 210

    class _Read(Resource):
        def get(self):
            scores = Score.query.all()    # read/extract all users from database
            json_ready = [score.read() for score in scores]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')