from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
from model.snake import AdminUser

# create admin api blueprint url prefix
admin_api = Blueprint('admin_api', __name__,
                   url_prefix='/api/admin')

# add cors headers
@admin_api.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers']= "*"
    header['Access-Control-Allow-Methods'] ="*"
    # Other headers can be added here if needed
    return response

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(admin_api)

# admin user api class
class AdminUserAPI:
    # Create (POST)  
    class _Create(Resource):
        # post method implementation
        def post(self):
            ''' Read data for json body '''
            print(request.get_data())
            body = request.get_json(force=True)
            print (body)
            name = body.get('name')
            uid = body.get('uid')
            password = body.get('password')
            
            ''' Avoid garbage in, error checking '''
            # validate name
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 210
            # validate uid
            if uid is None or len(uid) < 2:
                return {'message': f'AdminUser ID is missing, or is less than 2 characters'}, 210

            ''' #1: Key code block, setup AdminUser OBJECT '''
            uo = AdminUser(name=name, uid=uid)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None and len(password) > 7:
                uo.set_password(password)
            
            ''' #2: Key Code block to add AdminUser to database '''
            print("Creating AdminUser")
            # create AdminUser in database
            AdminUser = uo.create()
            # success returns json of AdminUser
            if AdminUser:
                print("AdminUser created successfully")
                createduserdata = AdminUser.read()
                print(createduserdata)
                userdatajson = jsonify(createduserdata)
                print(userdatajson)
                response = make_response(userdatajson, 200)
                return response
            # failure returns error
            return {'message': f'Processed {name}, either a format error or AdminUser ID {uid} is duplicate'}, 210

    # Update (Put)
    class _Update(Resource):
        # put implementation
        def put(self):
            ''' Read data for json body '''
            print(request.get_data())
            body = request.get_json(force=True)
            print (body)
            name = body.get('name')
            adminUserId = body.get('uid')
            password = body.get('password')
            id = body.get('id')
            print(adminUserId)
            ''' #1: Key code block, fetch existing AdminUser OBJECT '''
            adminUser = AdminUser.getAdminUserById(id)
            # validate name
            if adminUser is None:
                return {'message': f'AdminUser account not found for userid{adminUserId}'}, 210
            
            ''' Avoid garbage in, error checking '''
            # validate name
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 210
            else:
                adminUser.name = name

            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None and len(password) > 7:
                adminUser.set_password(password)
            
            ''' #2: Key Code block to add AdminUser to database '''
            print("Updating AdminUser")
            # create AdminUser in database
            adminUser = AdminUser.update(adminUser)
            
            # success returns json of AdminUser
            if adminUser:
                print("AdminUser updated successfully")
                updatedAdminUserData = adminUser.read()
                print(updatedAdminUserData)
                userdatajson = jsonify(updatedAdminUserData)
                print(userdatajson)
                response = make_response(userdatajson, 200)
                return response
            # failure returns error
            return {'message': f'Processed {name}, either a format error or AdminUser ID {adminUserId} is incorrect'}, 210

    # read (GET)
    class _Read(Resource):
        # get implementation
        def get(self):
            users = AdminUser.query.all()    # read/extract all users from database
            json_ready = [adminUser.read() for adminUser in users]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps

    # login (get) implementation
    class _Login(Resource):
        # creates a login implementation and does password authentication
        def get(self):
            adminUserId = request.args.get("uid")
            plainTxtPass = request.args.get("password")
            print("Authenticating AdminUser id: " + adminUserId)
            print("Authenticating password : " + plainTxtPass)

            if adminUserId == "":
                 return {'valid':False, 'message': f'adminUser ID not provided.'}, 210
            else:
                adminUser = AdminUser.getAdminUserByLoginId(adminUserId)

                if (adminUser is None):
                    return {'valid':False, 'message': f'Admin User with ID: ('+adminUserId+') not found.'}, 210
                
                if (AdminUser.validateUserPassword(adminUser, plainTxtPass)):
                    return {'valid':True, 'name': adminUser._name, 'uid': adminUserId, 'id': adminUser.id, 'message': 'Admin Login successful.'}, 200
                else:
                    return {'valid':False, 'message': f'Authentication failed for Admin User with ID: ('+adminUserId+'). Incorrect password.'}, 210

    # delete 
    class _Delete(Resource):
        # delete implementation
        def delete(self):
            adminUserId = request.args.get("id")
            print(adminUserId)

            if adminUserId == "":
                 return {'message': f'Admin User ID not provided.'}, 210
            else:
                adminUser = AdminUser.getAdminUserById(adminUserId)

                if (adminUser is None):
                    return {'message': f'Admin User with ID: ('+adminUserId+') not found.'}, 210
                
                adminUserName = adminUser._name
                print("deleting adminUser " + adminUserName)
                
                
                AdminUser.delete(adminUser)
                return {'message': f'Admin User \''+adminUserName+'\' ('+adminUserId+') deleted.'}, 200
            

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')
    api.add_resource(_Delete, '/delete')
    api.add_resource(_Update, '/update')
    api.add_resource(_Login, '/login')