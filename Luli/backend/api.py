from flask import session, request
from bson.objectid import ObjectId
#############################
#       API FUNCTIONS       #
#############################
'''
    List of Valid API Endpoints and Their Methods:
    ENDPOINT:                       METHODS:
    - /api/test                     GET
    - /api/get_hardware_id          GET
    - /api/set_hardware_id          POST
    - /api/update_settings          POST
    - /api/get_settings             GET
    - /api/get_humidity_data        GET
    - /api/get_uv_data              GET
    - /api/get_ph_data              GET
    - /api/get_temp_data            GET
    - /api/get_all_data             GET
    - /api/update_uv_data           POST
    - /api/update_ph_data           POST
    - /api/update_temp_data         POST
    - /api/update_humidity_data     POST
'''

# Do it all in a function here because we can pass it "app" which is the same "app" as main.py
# this way avoids circular imports and lets us clean up the main.py file and keep the API defined here

def register_api_routes(app, users_settings_collection, users_data_collection, users_collection):

    # API Login via username and password
    @app.route('/api/login', methods=['POST'])
    def api_login():
        username = request.json.get('username')
        password = request.json.get('password')
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['logged_in'] = True
            session['user_id'] = str(user['_id'])
            return "Logged in successfully."
        return "Invalid username or password."

    ## USER SETTINGS
    @app.route('/api/get_settings', methods=['GET'])
    def api_get_settings():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_settings = users_settings_collection.find_one({'user_id': user_id})
        if not user_settings:
            return "No settings found for this user."
        return user_settings['settings']

    @app.route('/api/update_settings', methods=['POST'])
    def api_update_settings():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_settings = users_settings_collection.find_one({'user_id': user_id})
        if not user_settings:
            users_settings_collection.insert_one({'user_id': user_id, 'settings': request.json})
        else:
            users_settings_collection.update_one({'user_id': user_id}, {'$set': {'settings': request.json}})
        return "Settings updated successfully."

    @app.route('/api/set_hardware_id', methods=['POST'])
    def api_set_hardware_id():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_credentials = users_collection.find_one({'user_id': user_id})
        if not user_credentials:
            users_collection.insert_one({'user_id': user_id, 'hardware_id': request.json})
        else:
            users_collection.update_one({'user_id': user_id}, {'$set': {'hardware_id': request.json}})
        return "Hardware ID updated successfully."
    
    @app.route('/api/get_hardware_id', methods=['GET'])
    def api_get_hardware_id():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_credentials = users_collection.find_one({'user_id': user_id})
        if not user_credentials:
            return "No hardware ID found for this user."
        return user_credentials['hardware_id']

    ## SENSOR READINGS - GET

    @app.route('/api/get_uv_data', methods=['GET'])
    def api_get_uv_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['uv_data']

    @app.route('/api/get_ph_data', methods=['GET'])
    def api_get_ph_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['ph_data']

    @app.route('/api/get_temp_data', methods=['GET'])
    def api_get_temp_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['temp_data']

    @app.route('/api/get_humidity_data', methods=['GET'])
    def api_get_humidity_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['humidity_data']

    @app.route('/api/get_all_data', methods=['GET'])
    def api_get_all_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data

    ## SENSOR READINGS - POST
    @app.route('/api/update_uv_data', methods=['POST'])
    def api_update_UV_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'uv_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'uv_data': request.json}})
        return "UV Data updated successfully."

    @app.route('/api/update_ph_data', methods=['POST'])
    def api_update_pH_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'ph_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'ph_data': request.json}})
        return "pH Data updated successfully."

    @app.route('/api/update_temp_data', methods=['POST'])
    def api_update_temp_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'temp_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'temp_data': request.json}})
        return "Temperature Data updated successfully."

    @app.route('/api/update_humidity_data', methods=['POST'])
    def api_update_humidity_data():
        if not session.get("logged_in"):
            return "You are not logged in."
        user_id = session.get("user_id")
        user_id = ObjectId(user_id)
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'humidity_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'humidity_data': request.json}})
        return "Humidity Data updated successfully."


    @app.route('/api/test', methods=['GET'])
    def api_test():
        return "API is working."