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
users_settings_collection = DATABASE.settings
users_data_collection = DATABASE.data

app = Flask(__name__,
            static_url_path='', 
            static_folder=relative_static_path,
            template_folder=relative_templates_path )

load_dotenv() # Load .env file data
app.secret_key = os.getenv("luli_secret_key") # Load secret key into flask app
os.environ.pop('luli_secret_key', None) # Delete secret key from environment variables

# Import the function to register API routes after the app instance is created
from api import register_api_routes

# Call the register function with the app object to set up the api endpoints
register_api_routes(app, users_data_collection=users_data_collection, users_settings_collection=users_settings_collection, users_collection=users_collection)

@app.route('/')
def serve_welcome_page():
    return app.send_static_file('Luli.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists in the database
        if users_collection.find_one({'username': username}):
            #return flash('Username already exists. Choose a different one.', 'error')
            return "Username already exists. Choose a different one."
            
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        # Insert new user into the database
        print(f"INSERTING: {username}::{hashed_password} into {users_collection}")
        current_time = datetime.now()
        users_collection.insert_one({'username': username, 'password': hashed_password, 'created':current_time})
        
        
        #flash('Account created successfully!', 'success')
        return redirect(url_for('login'))  
        
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Create Account">
        </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the username and password from the submitted form
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the username
        user_document = users_collection.find_one({'username': username})
        user_mongo_id = user_document['_id']
            

        if user_document:
            # A document for the user exists, now check the password
            stored_hash = user_document.get('password')
            if check_password_hash(stored_hash, password):
                # The hash matches the password provided
                # Login is successful
                flash('Login successful!', 'success')
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = str(user_document['_id'])
                users_collection.update_one({'_id': user_mongo_id}, {'$set': {'last_login': datetime.now()}})
                return redirect(url_for('serve_welcome_page')) 
            else:
                # The hash does not match the password provided
                # Don't tell the user the password was wrong, just say the credentials were incorrect
                #   prevents account enumeration attacks
                return flash("Incorrect credentials.", "error")
        else:
            # No user document with that username exists
            # Don't tell the user the username was wrong, just say the credentials were incorrect
            #   prevents account enumeration attacks
            return flash("Incorrect credentials.", "error")
    # If it's a GET request, just render the login page
    return app.send_static_file('Luli.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))








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
