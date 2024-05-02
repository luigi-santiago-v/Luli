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
    - /api/get_tank_data            GET
    - /api/get_all_data             GET
    - /api/update_uv_data           POST
    - /api/update_ph_data           POST
    - /api/update_temp_data         POST
    - /api/update_humidity_data     POST
    - /api/update_tank_data         POST
    - /api/update_all_sensor_data  POST
    - /api/update_manual_override   POST
    - /api/get_manual_override      GET
'''

# Do it all in a function here because we can pass it "app" which is the same "app" as main.py
# this way avoids circular imports and lets us clean up the main.py file and keep the API defined here



def register_api_routes(app, users_settings_collection, users_data_collection, users_collection):
    # This dictionary will store the manual override commands for each device by its ID
    device_override_commands = {}


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
        print(f"Validating Device ID: {device_id}")  # Debug output
        # Ensure device ID is provided
        if device_id is None:
            return False, None, jsonify({'message': 'X-Device-ID is required'}), 400
        
        # Ensure device ID is a valid hexadecimal and correct length
        if len(device_id) != 16 or not all(c in '0123456789abcdefABCDEF' for c in device_id):
            return False, None, jsonify({'message': 'Invalid X-Device-ID format'}), 400
        if device_id is None:
            return False, None, 'X-Device-ID is required', 400

        if not isinstance(device_id, str):
            print("Device ID is not a string")  # Debug output
            return False, None, 'Invalid X-Device-ID format', 400


        valid_chars = set("0123456789abcdefABCDEF")
        if not all(char in valid_chars for char in device_id):
            print(f"Device ID contains non-hex characters: {device_id}")  # Debug output
            return False, None, 'Invalid X-Device-ID format', 400

        user = users_collection.find_one({"device_id": device_id})
        
        if user is None:
            print(f"Device ID {device_id} not found in database")  # Debug output
            return False, None, 'Unauthorized - Device not recognized', 401

        return True, ensure_object_id(user['_id']), 'Authentication Successful', 200

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
    @app.route('/api/get_settings/<device_id>', methods=['GET'])
    def api_get_settings(device_id):
        user = users_collection.find_one({'device_id': device_id})
        if not user:
            return jsonify({'error': 'No user found for this device.'}), 404

        user_id = user['_id']
        user_settings = users_settings_collection.find_one({'user_id': ObjectId(user_id)})
        if not user_settings:
            return jsonify({'error': 'No settings found for this user.'}), 404

        # Convert ObjectId to string if needed
        user_settings = {k: str(v) if isinstance(v, ObjectId) else v for k, v in user_settings.items()}
        return jsonify(user_settings)


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

    @app.route('/api/get_light_data', methods=['GET'])
    @require_api_key
    def api_get_light_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            #return "No data found for this user."
            return jsonify({'message': 'No data found for this user'}), 404
        return user_data['light']

    @app.route('/api/get_ph_data', methods=['GET'])
    @require_api_key
    def api_get_ph_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            #return "No data found for this user."
            return jsonify({'message': 'No data found for this user'}), 404
        return user_data['ph']

    @app.route('/api/get_temp_data', methods=['GET'])
    @require_api_key
    def api_get_temp_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            #return "No data found for this user."
            return jsonify({'message': 'No data found for this user'}), 404
        return user_data['temp']

    @app.route('/api/get_humidity_data', methods=['GET'])
    @require_api_key
    def api_get_humidity_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            #return "No data found for this user."
            return jsonify({'message': 'No data found for this user'}), 404
        return user_data['humidity']
    
    @require_api_key
    def api_get_tank_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            #return "No data found for this user."
            return jsonify({'message': 'No data found for this user'}), 404
        return user_data['tank']

    @app.route('/api/get_all_data', methods=['GET'])
    @require_api_key
    def api_get_all_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            #return "No data found for this user."
            return jsonify({'message': 'No data found for this user'}), 404
        return user_data

    ## SENSOR READINGS - POST
    @app.route('/api/update_light_data', methods=['POST'])
    @require_api_key
    def api_update_light_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'light': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'light': request.json}})
        #return "Light Data updated successfully."
        return jsonify({'message': 'Light Data updated successfully'}), 200

    @app.route('/api/update_ph_data', methods=['POST'])
    @require_api_key
    def api_update_pH_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'ph': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'ph': request.json}})
        #return "pH Data updated successfully."
        return jsonify({'message': 'pH Data updated successfully'}), 200

    @app.route('/api/update_temp_data', methods=['POST'])
    @require_api_key
    def api_update_temp_data(user_id):
        temp_data = request.get_json().get('temp')
        if temp_data is None:
            return jsonify({'message': 'No temperature data provided'}), 400
        
        timestamp = datetime.now().isoformat().replace('.', ':')
        update_result = users_data_collection.update_one(
            {'_id': user_id},
            {'$set': {f'sensor_data.{timestamp}.temp': temp_data}},
            upsert=True
        )
        
        if update_result.modified_count == 0:
            return jsonify({'message': 'Temperature data update failed'}), 500

        return jsonify({'message': 'Temperature Data updated successfully'}), 200

    @app.route('/api/update_humidity_data', methods=['POST'])
    @require_api_key
    def api_update_humidity_data(user_id):
        humidity_data = request.get_json().get('humidity')
        if humidity_data is None:
            return jsonify({'message': 'No humidity data provided'}), 400
        
        timestamp = datetime.now().isoformat().replace('.', ':')
        update_result = users_data_collection.update_one(
            {'_id': user_id},
            {'$set': {f'sensor_data.{timestamp}.humidity': humidity_data}},
            upsert=True
        )
        
        if update_result.modified_count == 0:
            return jsonify({'message': 'Humidity data update failed'}), 500

        return jsonify({'message': 'Humidity Data updated successfully'}), 200

    @app.route('/api/update_tank_data', methods=['POST'])
    @require_api_key
    def api_update_tank_data(user_id):
        user_data = users_data_collection.find_one({'user_id': user_id})
        if not user_data:
            users_data_collection.insert_one({'user_id': user_id, 'tank': request.json})
        else:
            users_data_collection.update_one({'user_id': user_id}, {'$set': {'tank': request.json}})
        #return "Tank Data updated successfully."
        return jsonify({'message': 'Tank Data updated successfully'}), 200


    @app.route('/api/update_all_sensor_data', methods=['POST'])
    @require_api_key
    def update_all_sensor_data(user_id):
        sensor_data = request.get_json()
        if not sensor_data:
            return jsonify({'message': 'No sensor data provided'}), 400
        
        # Generate a timestamp for the current data entry
        timestamp = datetime.datetime.now().isoformat().replace('.', ':')
        print(f"TIMESTAMP IS: {timestamp}")

        # Update the user's sensor data, adding the new data under the current timestamp
        update_result = users_data_collection.update_one(
            {"_id": user_id},
            {"$set": {f"sensor_data.{timestamp}": sensor_data}},
            upsert=True
        )

        if update_result.matched_count == 0:
            # If no document was found and updated, create a new one
            users_data_collection.insert_one({'_id': user_id, 'sensor_data': {timestamp: sensor_data}})

        # Return a successful response
        return jsonify({'message': 'All sensor data updated successfully', 'timestamp': timestamp}), 200

    
    @app.route('/api/test', methods=['GET'])
    def api_test():
        return "API is working."
    
    @app.route('/api/update_manual_override/<device_id>', methods=['POST'])
    def update_manual_override(device_id):
        content = request.json
        if device_id not in device_override_commands:
            device_override_commands[device_id] = {}
        print(f"Received {content} for {device_id}")
        device_override_commands[device_id].update(content)
        return jsonify(success=True, commands=device_override_commands[device_id]), 200

    @app.route('/api/get_manual_override/<device_id>', methods=['GET'])
    def get_manual_override(device_id):
        commands = device_override_commands.get(device_id, {})
        # Clear the commands after they have been fetched
        device_override_commands[device_id] = {}
        return jsonify(commands), 200