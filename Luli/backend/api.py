from flask import request, jsonify
from bson.objectid import ObjectId
import datetime
from functools import wraps

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
    - /api/update_all_sensors_data  POST
'''

# Do it all in a function here because we can pass it "app" which is the same "app" as main.py
# this way avoids circular imports and lets us clean up the main.py file and keep the API defined here



def register_api_routes(app, users_settings_collection, users_data_collection, users_collection):
    def ensure_object_id(obj_id):
        if isinstance(obj_id, str):
            try:
                return ObjectId(obj_id)
            except Exception as e:
                print(f"Error converting string to ObjectId: {e}")
                return None  # or handle the error as needed
        elif isinstance(obj_id, ObjectId):
            return obj_id
        else:
            print("Invalid type for user ID.")
            return None  # or handle as needed
        
    def validate_API_key(device_id):
        # Device ID will look like:
        #device_id = request.headers.get('X-Device-ID')
        if device_id is None:
            return False, None, jsonify({'message': 'Device ID is required'}), 400

        user = users_data_collection.find_one({"device_id": device_id})
        if user is None:
            return False, None, jsonify({'message': 'Unauthorized - Device not recognized'}), 401
        
        return True, ensure_object_id(user['_id']), jsonify({'message': 'Authentication Successful'}), 200
    
    # Custom Decorator to require an API key on certain routes
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            valid_api_key, user_id, message, status_code = validate_API_key(request.headers.get('X-Device-ID'))
            if not valid_api_key:
                return jsonify({'message': message}), status_code
            return f(*args, **kwargs, user_id=user_id)
        return decorated_function
        
    # Custom test function to manually add data to the database
    def add_sensor_data(client, database_name, collection_name, document_id, sensor_data):
        # Access the MongoDB database
        db = client[database_name]
        collection = db[collection_name]
        
        # Timestamp as a string in ISO format, with colons replaced by underscores
        #timestamp = datetime.utcnow().isoformat().replace('.', ':') + '+00_00'
        timestamp = datetime.now().isoformat().replace('.', ':')

        # Update the document with new sensor data at the specified timestamp
        print(f"TIMESTAMP IS: {timestamp}")
        update_result = collection.update_one(
            {"_id": document_id},
            {"$set": {f"sensor_data.{timestamp}": sensor_data}},
            upsert=True
        )
        
        # Check the result of the update
        if update_result.upserted_id is not None:
            print(f"Document was created with ID: {update_result.upserted_id}")
        elif update_result.modified_count == 1:
            print("Update successful.")
        else:
            print("Update failed or no changes made.")

    

    ## USER SETTINGS
    @app.route('/api/get_settings', methods=['GET'])
    @require_api_key
    def api_get_settings(user_id):
        user_settings = users_settings_collection.find_one({'user_id': user_id})
        if not user_settings:
            return "No settings found for this user."
        return user_settings['settings']

    @app.route('/api/update_settings', methods=['POST'])
    @require_api_key
    def api_update_settings(user_id):
        user_settings = users_settings_collection.find_one({'user_id': user_id})
        if not user_settings:
            users_settings_collection.insert_one({'user_id': user_id, 'settings': request.json})
        else:
            users_settings_collection.update_one({'user_id': user_id}, {'$set': {'settings': request.json}})
        return "Settings updated successfully."

    @app.route('/api/set_hardware_id', methods=['POST'])
    def api_set_hardware_id():
        # Get the username and device_id passed in the request json:
        payload = request.get_json()
        username = payload.get('username')
        device_id = payload.get('device_id')
        user_credentials = users_collection.find_one({'username': username})
        if not user_credentials:
            return jsonify({'message': 'User not found'}), 404
        else:
            users_collection.update_one({'username': username}, {'$set': {'device_id': device_id}})
        return jsonify({'message': 'Hardware ID updated successfully'}), 200
    
    @app.route('/api/get_hardware_id', methods=['GET'])
    @require_api_key
    def api_get_hardware_id(user_id):
        user_credentials = users_collection.find_one({'user_id': user_id})
        if not user_credentials:
            return jsonify({'message': 'User not found'}), 404
        return user_credentials['hardware_id']

    ## SENSOR READINGS - GET

    @app.route('/api/get_uv_data', methods=['GET'])
    @require_api_key
    def api_get_uv_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['uv_data']

    @app.route('/api/get_ph_data', methods=['GET'])
    @require_api_key
    def api_get_ph_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['ph_data']

    @app.route('/api/get_temp_data', methods=['GET'])
    @require_api_key
    def api_get_temp_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['temp_data']

    @app.route('/api/get_humidity_data', methods=['GET'])
    @require_api_key
    def api_get_humidity_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data['humidity_data']

    @app.route('/api/get_all_data', methods=['GET'])
    @require_api_key
    def api_get_all_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            return "No data found for this user."
        return user_data

    ## SENSOR READINGS - POST
    @app.route('/api/update_uv_data', methods=['POST'])
    @require_api_key
    def api_update_UV_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'uv_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'uv_data': request.json}})
        return "UV Data updated successfully."

    @app.route('/api/update_ph_data', methods=['POST'])
    @require_api_key
    def api_update_pH_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'ph_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'ph_data': request.json}})
        return "pH Data updated successfully."

    @app.route('/api/update_temp_data', methods=['POST'])
    @require_api_key
    def api_update_temp_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'temp_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'temp_data': request.json}})
        return "Temperature Data updated successfully."

    @app.route('/api/update_humidity_data', methods=['POST'])
    @require_api_key
    def api_update_humidity_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'humidity_data': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'humidity_data': request.json}})
        return "Humidity Data updated successfully."
    
    @app.route('/api/update_all_sensor_data', methods=['POST'])
    @require_api_key
    def update_all_sensors_data(user_id):
        sensor_data = request.get_json()
        if not sensor_data:
            return jsonify({'message': 'No sensor data provided'}), 400
        # Update the document with new sensor data at the specified timestamp
        print(f"TIMESTAMP IS: {timestamp}")    
        timestamp = datetime.datetime.now().isoformat().replace('.', ':')
        # Check if the user already has sensor data
        if users_data_collection.count_documents({'_id': user_id, 'sensor_data': {'$exists': True}}) == 0:
            # If not, create a new document with sensor_data as a dictionary
            users_data_collection.insert_one({'_id': user_id, 'sensor_data': {timestamp: sensor_data}})
        else:
            # If sensor_data exists, update the existing document with new sensor data at the specified timestamp
            users_data_collection.update_one(
                {"_id": user_id},
                {"$set": {f"sensor_data.{timestamp}": sensor_data}},
                upsert=True
            )

        return "All sensor data updated successfully."
    

       


    @app.route('/api/test', methods=['GET'])
    def api_test():
        return "API is working."