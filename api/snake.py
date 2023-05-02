from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from model.snake import User

snake_api = Blueprint('snake_api', __name__,
                   url_prefix='/api/gamers')

# add cors headers
@snake_api.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers']= "*"
    header['Access-Control-Allow-Methods'] ="*"
    # Other headers can be added here if needed
    return response

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(snake_api)

# implement gamer / user api
class UserAPI:
    # create gamer
    class _Create(Resource):
        # post implementation
        def post(self):
            ''' Read data for json body '''
            print(request.get_data())
            body = request.get_json(force=True)
            print (body)
            name = body.get('name')
            uid = body.get('uid')
            password = body.get('password')
            dob = body.get('dob')
            difficultyLevel = body.get('level')
            
            ''' Avoid garbage in, error checking '''
            # validate name
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 210
            # validate uid
            if uid is None or len(uid) < 2:
                return {'message': f'User ID is missing, or is less than 2 characters'}, 210

            ''' #1: Key code block, setup USER OBJECT '''
            uo = User(name=name, uid=uid, level=difficultyLevel)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None and len(password) > 7:
                uo.set_password(password)
            # convert to date type
            if dob is not None:
                try:
                    uo.dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except:
                    return {'message': f'Date of birth format error {dob}, must be yyyy-mm-dd'}, 210
            
            ''' #2: Key Code block to add user to database '''
            print("Creating user")
            # create user in database
            user = uo.create()
            # success returns json of user
            if user:
                print("User created successfully")
                createduserdata = user.read()
                print(createduserdata)
                userdatajson = jsonify(createduserdata)
                print(userdatajson)
                response = make_response(userdatajson, 200)
                return response
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {uid} is duplicate'}, 210

    # update user / gamer
    class _Update(Resource):
        # put implementation
        def put(self):
            ''' Read data for json body '''
            print(request.get_data())
            body = request.get_json(force=True)
            print (body)
            name = body.get('name')
            gamerid = body.get('uid')
            password = body.get('password')
            dob = body.get('dob')
            difficultyLevel = body.get('level')
            id = body.get('id')
            print(gamerid)
            ''' #1: Key code block, fetch existing USER OBJECT '''
            gamer = User.getUserByUserId(gamerid)
            # validate name
            if gamer is None:
                return {'message': f'User account not found for userid{gamerid}'}, 210
            
            gamer.level = difficultyLevel
            
            ''' Avoid garbage in, error checking '''
            # validate name
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 210
            else:
                gamer.name = name

            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None and len(password) > 7:
                gamer.set_password(password)
            
            # convert to date type
            #if dob is not None:
            #    try:
            #        gamer.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            #   except:
            #       return {'message': f'Date of birth format error {dob}, must be mm-dd-yyyy'}, 210
            
            ''' #2: Key Code block to add user to database '''
            print("Updating user")
            # create user in database
            gamer = User.update(gamer)
            # success returns json of user
            if gamer:
                print("User updated successfully")
                updatedGamerData = gamer.read()
                print(updatedGamerData)
                userdatajson = jsonify(updatedGamerData)
                print(userdatajson)
                response = make_response(userdatajson, 200)
                return response
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {gamerid} is incorrect'}, 210

    # get users
    class _Read(Resource):
        # get implementation
        def get(self):
            gamerid = request.args.get("id")
            print(gamerid)

            # if id is present in the request params, then read that user's data
            # otherwise read all userss
            if gamerid is None or len(gamerid) == 0:
                users = User.query.all()    # read/extract all users from database
                json_ready = [user.read() for user in users]  # prepare output in json
                return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps
            else:
                gamer = User.getUserById(gamerid)
                return jsonify(gamer.read()) 
            
    # get users' scores
    class _Scores(Resource):
        # get implementation
        def get(self):
            scoresData = User.getAllScores()  # read/extract all users from database
            scores = []
            for user, score in scoresData:
                #print ("Name: {} Score: {} Date Played: {}".format(user._name,str(score.score), score.dateplayed))
                sc = {"name": user._name, "score":str(score.score), "dateplayed": score.dateplayed.strftime('%Y-%m-%d')}
                scores.append(sc)
            
            return jsonify(scores)  # jsonify creates Flask response object, more specific to APIs than json.dumps

    # login implementation
    class _Login(Resource):
        def get(self):
            gamerid = request.args.get("uid")
            plainTxtPass = request.args.get("password")
            print("Authenticating user id: " + gamerid)
            print("Authenticating password : " + plainTxtPass)

            if gamerid == "":
                 return {'valid':False, 'message': f'Gamer ID not provided.'}, 210
            else:
                gamer = User.getUserByUserId(gamerid)

                if (gamer is None):
                    return {'valid':False, 'message': f'Gamer with ID: ('+gamerid+') not found.'}, 210
                
                if (User.validateUserPassword(gamer, plainTxtPass)):
                    score = User.getHighScore(gamer.id)
                    if (score is None):
                        highscore = 0
                    else:
                        highscore = User.getHighScore(gamer.id).score
                    return {'valid':True, 'dob': gamer._dob.strftime('%Y-%m-%d'), 'name': gamer._name, 'uid': gamerid, 'id': gamer.id, 'level': gamer._level,'highscore': highscore, 'message': 'Login successful.'}, 200
                else:
                    return {'valid':False, 'message': f'Authentication failed for gamer with ID: ('+gamerid+'). Incorrect password.'}, 210

    # delete users 
    class _Delete(Resource):
        def delete(self):
            gamerid = request.args.get("id")
            print(gamerid)

            if gamerid == "":
                 return {'message': f'Gamer ID not provided.'}, 210
            else:
                gamer = User.getUserById(gamerid)

                if (gamer is None):
                    return {'message': f'Gamer with ID: ('+gamerid+') not found.'}, 210
                
                gamerName = gamer._name
                print("deleting gamer " + gamerName)
                
                #json_ready = [team.read()]
                User.delete(gamer)
                return {'message': f'Gamer \''+gamerName+'\' ('+gamerid+') deleted.'}, 200
            

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')
    api.add_resource(_Delete, '/delete')
    api.add_resource(_Update, '/update')
    api.add_resource(_Login, '/login')
    api.add_resource(_Scores, '/scores')