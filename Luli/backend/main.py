#########################################
#           Luli Hydroponics            #
#      Backend Code made with Flask    #
#########################################


from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
import uuid



# Get the absolute path to the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Construct the absolute paths to 'static' and 'templates' folders
absolute_static_path = os.path.join(BASE_DIR, '..', 'frontend', 'static')
absolute_templates_path = os.path.join(BASE_DIR, '..', 'frontend', 'templates')
absolute_user_images_path = os.path.join(BASE_DIR, '..', 'frontend', 'static', 'USER_IMAGES')

# Normalize the paths to remove any relative path components (like '..')
absolute_static_path = os.path.normpath(absolute_static_path)
absolute_templates_path = os.path.normpath(absolute_templates_path)
absolute_user_images_path = os.path.normpath(absolute_user_images_path)


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
            static_folder=absolute_static_path,
            template_folder=absolute_templates_path )

load_dotenv() # Load .env file data
app.secret_key = os.getenv("luli_secret_key") # Load secret key into flask app
os.environ.pop('luli_secret_key', None) # Delete secret key from environment variables


app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS.
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent client-side JS from accessing the cookie.
app.config['IMAGE_UPLOAD_FOLDER'] = absolute_user_images_path
app.config['PROFILE_PIC_FOLDER'] = os.path.join(absolute_static_path, 'PROFILE_PICS')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max size
# Ensure the directory exists
os.makedirs(app.config['IMAGE_UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROFILE_PIC_FOLDER'], exist_ok=True)

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
        profile_pic = request.files['profile_pic']
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
            'created': current_time,
            'friends': []  # Initialize an empty list for friends
        })
        
        # Retrieve the new user's ID
        new_user_id = result.inserted_id

        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            # Standardize the file extension
            if filename.lower().endswith('.jpeg'):
                filename = filename[:-5] + '.jpg'  # Change extension from .jpeg to .jpg

            filename = username + '.jpg'  # Rename the file to username.jpg
            profile_pic_path = os.path.join(app.config['PROFILE_PIC_FOLDER'], filename)
            profile_pic.save(profile_pic_path)
        
        # Retrieve all existing users to add to the new user's friend list, excluding the new user themselves
        all_users = users_collection.find({'_id': {'$ne': new_user_id}}, {'_id': 1, 'username': 1})
        friends_list = [{'username': user['username'], 'user_id': str(user['_id'])} for user in all_users]
        
        # Add existing users to the new user's friend list
        users_collection.update_one({'_id': new_user_id}, {'$set': {'friends': friends_list}})
        
        # Also add this new user to existing users' friends lists
        users_collection.update_many({'_id': {'$ne': new_user_id}}, {'$push': {'friends': {'username': username, 'user_id': str(new_user_id)}}})

        # Initialize empty entries in other collections
        users_settings_collection.insert_one({'user_id': new_user_id, 'settings': {}})
        users_data_collection.insert_one({'user_id': new_user_id, 'data': {}})
        users_messages_collection.insert_one({'user_id': new_user_id, 'messages': {}})
        
        return redirect(url_for('login'))
    else:
        # Serve the static HTML file for the account creation form
        return app.send_static_file('CreateAccount.html')
    
def allowed_profile_pic(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}

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
            return redirect(url_for('plants'))
        else:
            # Incorrect credentials, redirect with error message
            return redirect(url_for('login', msg='Incorrect credentials.'))
    else:
        # Serve the login page
        return app.send_static_file('Luli.html')

###############
#   LOGOUT    #
###############
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


#########################
#   PLANTS + SENSORS    #
#########################
@app.route('/plants')
def plants():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    sensor_data_document = users_data_collection.find_one({'user_id': ObjectId(user_id)})

    if sensor_data_document and 'sensor_data' in sensor_data_document:
        sensor_data = sensor_data_document['sensor_data']
        latest_sensor_data = list(sensor_data.values())[-1] if sensor_data else {}
    else:
        # Default empty data if there's no sensor data available
        latest_sensor_data = {
            'light': 'N/A',
            'temp': 'N/A',
            'humidity': 'N/A',
            'ph': 'N/A',
            'tank': 'N/A'
        }

    return render_template('Plants.html', sensor_data=latest_sensor_data)
   
##############
#   FORUM    #
##############
@app.route('/forum')
def forum():
    posts = list(users_messages_collection.find())
    return render_template('Forum.html', posts=posts)


@app.route('/add_post', methods=['POST'])
def add_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user_document = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    if not user_document:
        return "User not found", 404

    message = request.form.get('message')
    image = request.files.get('image')
    
    post = {'user_id': session['user_id'], 
            'name': user_document.get('first_name'), 
            'message': message, 
            'created': datetime.now()}

    if image and allowed_file(image.filename):
        try:
            # Generate a unique filename using UUID
            unique_filename = str(uuid.uuid4())
            file_extension = os.path.splitext(secure_filename(image.filename))[1]
            filename = unique_filename + file_extension
            # The relative path for use in HTML src attribute
            relative_image_path = os.path.join('USER_IMAGES', filename)
            # The absolute path to save the image file
            absolute_image_path = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename)
            # Save the image
            image.save(absolute_image_path)
            # Add image path to the post dictionary
            post['image_path'] = relative_image_path  # Store the relative path, not absolute
            print(f"Image saved with unique filename {filename}")
        except Exception as e:
            print(f"Failed to save image: {e}")
            return "Failed to save image", 500

    # Insert the post (with the image path if there's an image) into the database
    users_messages_collection.insert_one(post)
    return redirect(url_for('forum')) 


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    # Check if there is an extension in the filename and if the extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


###############
#   FRIENDS   #
###############
@app.route('/friends')
def friends():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    user_id = session['user_id']
    user_document = users_collection.find_one({'_id': ObjectId(user_id)})

    if 'friends' in user_document:
        # Extract the user_id of each friend and convert to ObjectId
        friend_ids = [ObjectId(friend['user_id']) for friend in user_document['friends']]
        friends = users_collection.find({'_id': {'$in': friend_ids}})
        friends_list = list(friends)  # Convert cursor to list for passing to template
        return render_template('Friends.html', friends=friends_list)
    else:
        # Handle case where no friends are stored or the field is missing
        return render_template('Friends.html', friends=[])




#################
#   SETTINGS    #
#################
@app.route('/save_settings', methods=['POST'])
def save_settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    water_interval = request.form.get('water_interval')
    led_duration = request.form.get('led_duration')
    pump_duration = request.form.get('pump_duration')
    # ... other settings values

    users_settings_collection.update_one(
        {'user_id': ObjectId(user_id)},
        {'$set': {
            'water_interval': water_interval,
            'led_duration': led_duration,
            'pump_duration': pump_duration
            # ... other settings
        }},
        upsert=True
    )
    return redirect(url_for('settings_page'))


@app.route('/settings')
def settings_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    settings = users_settings_collection.find_one({'user_id': ObjectId(user_id)})
    print("GOT SETTINGS: ", settings)
    if settings is None:
        # Set defaults if no settings are found
        print("settings is None!")
        settings = {
            'water_interval': '12',
            'led_duration': '12',
            'pump_duration': '5',
            # Include defaults for any other settings
        }
    else:
        # If settings exist, remove MongoDB's _id before passing to template
        settings.pop('_id', None)
    
    return render_template('settings.html', settings=settings)

@app.route('/download_settings/<friend_id>')
def download_settings(friend_id):
    print("SAVING SETTINGS FROM FRIEND: ", friend_id)
    settings = users_settings_collection.find_one({'user_id': ObjectId(friend_id)})
    if settings:
        del settings['_id']  # Remove the MongoDB ID before sending
        return jsonify(settings)
    # Now get current user's document
    user_id = session['user_id']
    user_settings = users_settings_collection.find_one({'user_id': ObjectId(user_id)})
    # Now overwrite user_settings with settings from friend
    # But don't overwrite the user_id
    user_settings.update(settings)
    return jsonify({'error': 'Settings not found'}), 404


#################
# CONTROL PANEL #
#################
@app.route('/control_panel')
def control_panel():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    device_id = user_data.get('device_id') if user_data else None
    if device_id:
        return render_template('ControlPanel.html', device_id=device_id)
    else:
        return "Device ID not found", 404



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
