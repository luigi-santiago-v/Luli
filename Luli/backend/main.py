#########################################
#           Luli Hydroponics            #
#      Backend Code made with Flask    #
#########################################


from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime


relative_static_path = "../frontend/static"
relative_templates_path = "../frontend/templates"

# MongoDB connection setup
mongodb_connection_string = 'mongodb://localhost:27017'
# brew services start mongodb/brew/mongodb-community

client = MongoClient(mongodb_connection_string) 
DATABASE = client['user_data']  
users_collection = DATABASE.credentials
users_messages_collection = DATABASE.messages
users_settings_collection = DATABASE.settings
users_data_collection = DATABASE.data

app = Flask(__name__,
            static_url_path='', 
            static_folder=relative_static_path,
            template_folder=relative_templates_path )

load_dotenv() # Load .env file data
app.secret_key = os.getenv("luli_secret_key") # Load secret key into flask app
os.environ.pop('luli_secret_key', None) # Delete secret key from environment variables


app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS.
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent client-side JS from accessing the cookie.
#app.config['PERMANENT_SESSION_LIFETIME'] = 600  # Session lifetime in seconds or use timedelta for more precision.


# Import the function to register API routes after the app instance is created
from api import register_api_routes

# Call the register function with the app object to set up the api endpoints
register_api_routes(app, users_data_collection=users_data_collection, users_settings_collection=users_settings_collection, users_collection=users_collection)

#################
#   HOMEPAGE    #
#################
@app.route('/')
def serve_welcome_page():
    return app.send_static_file('Luli.html')


#######################
#   CREATE ACCOUNT    #
#######################
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists in the database
        if users_collection.find_one({'username': username}):
            return "Username already exists. Choose a different one."
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        current_time = datetime.now()
        result = users_collection.insert_one({
            'first_name': first_name, 
            'last_name': last_name,
            'username': username, 
            'password': hashed_password, 
            'created': current_time
        })
        
        # Retrieve the new user's ID
        new_user_id = result.inserted_id
        
        # Initialize empty entries in other collections
        users_settings_collection.insert_one({'user_id': new_user_id, 'settings': {}})
        users_data_collection.insert_one({'user_id': new_user_id, 'data': {}})
        users_messages_collection.insert_one({'user_id': new_user_id, 'messages': {}})
        
        return redirect(url_for('login'))
    else:
        # Serve the static HTML file for the account creation form
        return app.send_static_file('CreateAccount.html')

##############
#   LOGIN    #
##############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_document = users_collection.find_one({'username': username})

        if user_document and check_password_hash(user_document.get('password'), password):
            # Login successful
            session["logged_in"] = True
            session["username"] = username
            session["user_id"] = str(user_document['_id'])
            users_collection.update_one({'_id': user_document['_id']}, {'$set': {'last_login': datetime.now()}})
            return redirect(url_for('serve_welcome_page'))
        else:
            # Incorrect credentials, redirect with error message
            return redirect(url_for('login', msg='Incorrect credentials.'))
    else:
        # Serve the login page
        return app.send_static_file('Login.html')

###############
#   LOGOUT    #
###############
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

######################
#   CONTROL PANEL    #
######################
@app.route('/control_panel')
def control_panel():
    user_id = session.get('user_id')
    if user_id:
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        device_id = user_data.get('device_id') if user_data else None
        if device_id:
            return render_template('control_panel.html', device_id=device_id)
        else:
            return "Device ID not found", 404
    else:
        return "User not authenticated", 401


#########################
#   PLANTS + SENSORS    #
#########################
@app.route('/plants')
def plants():
    # Retrieve the document by its ID or another query
    # Check session, get user id, retrieve sensor data
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    sensor_data_document = users_data_collection.find_one({'user_id': ObjectId(user_id)})
    
    # Extract sensor data from the document
    sensor_data = sensor_data_document['sensor_data']

    # Here we assume that 'sensor_data' is structured with the latest reading as the last entry
    # If it's structured differently, you will need to adjust the logic to get the latest or desired sensor reading
    latest_sensor_data = list(sensor_data.values())[-1] if sensor_data else {}

    # Render the HTML page with the sensor data
    # The HTML file 'plants.html' should be in the 'templates' folder of your Flask application
    return render_template('Plants.html', sensor_data=latest_sensor_data)
   
##############
#   FORUM    #
##############
@app.route('/forum')
def forum():
    return app.send_static_file('Forum.html')




if __name__ == "__main__":
    ### How to run this file ###
    """
    1. Create a virtualenv and install packages
        $ pip3 install virtualenv           [ only run this once ]
        $ virtualenv venv                   [ this create a virtual python environment called "venv" ]
        $ activate venv/bin/activate        [ mac only, this is how to enable the venv so it doesnt install packages to your global python ]
        $ pip install -r requirements.txt   [ this installs the necessary modules for the code to run (i.e. Flask) ]
    2. cd Luli/backend
    3. Make sure MongoDB is running         [ On Mac: brew services start mongodb-community ]
    4. python main.py
    5. View the url in the output           [ If running locally: http://127.0.0.1:9696 ]
    6. Open it in browser
    """


    print("Starting Flask server...")
    app.run(debug=True, port=9696, host="0.0.0.0")
