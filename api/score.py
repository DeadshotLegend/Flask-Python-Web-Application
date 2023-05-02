from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from sqlalchemy import desc 
from model.snake import Score, User
score_api = Blueprint('score_api', __name__,
                   url_prefix='/api/scores')

# add cors headers
@score_api.after_request 
def after_request(response):
    header = response.headers
    # add cross origin headers
    header['Access-Control-Allow-Origin']  = '*'
    header['Access-Control-Allow-Headers'] = "*"
    header['Access-Control-Allow-Methods'] = "*"
    return response

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(score_api)

# scores api class
class ScoreAPI:
    # create new score
    class _Create(Resource):
        # post implementation
        def post(self):
            ''' Read data for json body '''
            print("The request: " + request.get_data(as_text=True))
            
            try:
                # check if the request body is JSON
                body = request.get_json(force=True)
                score = body.get('score')
                uid = body.get('uid')
            except:
                # if not JSON, then maybe it is passed as URL params
                score = request.args.get('score')
                uid = request.args.get('uid')
            
            # validating request data
            # make an empty response
            response = make_response()
            
            # validate score
            if score is None:
                return {'message': f'Score is missing'}, 210
            
            # validate uid
            if uid is None:
                return {'message': f'UserID is missing'}, 210
           
            # create score object with request data
            so = Score(score=score, id=uid)
            
            # create score in database
            scoreObj = so.create()

            # success returns json of user
            if scoreObj:
                return jsonify(scoreObj.read())
            
            # failure returns error
            return {'message': f'Processed {score}, either a format error or User ID {uid} is wrong'}, 210
    
    # read scores
    class _Read(Resource):
        # get implementation
        def get(self):
            # if user id is present in request, then return result for the single user
            userID = request.args.get("userID")
            if (userID):
                print("Querying scores for userID: " + userID)
                scores = Score.getScoresForUser(userID=userID)
            else:
                print("Querying all scores")
                # limit scores to top 50 results to avoid sending too much data to view
                scores = Score.query.order_by(desc(Score.score)).limit(50)    # read/extract all users from database

            json_ready = [score.read() for score in scores]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps

    # delete scores
    class _Delete(Resource):
        #delete implementation
        def delete(self):
            userID = request.args.get("userID")
            print(userID)

            if userID == "":
                 return {'message': f'Gamer ID not provided.'}, 210
            else:
                gamer = User.getUserById(userID)

                if (gamer is None):
                    return {'message': f'Gamer with ID: ('+userID+') not found.'}, 210
                
                gamerName = gamer._name
                print("deleting gamer scores " + gamerName)
                
                Score.deleteUserScores(userID = userID)
                
                return {'message': f'Scores for Gamer \''+gamerName+'\' ('+userID+') deleted.'}, 200
       
    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')
    api.add_resource(_Delete, '/delete')