#########################################
#           Luli Hydroponics            #
#      Backend Code made with Flask    #
#########################################


from flask import Flask, render_template, request, redirect, url_for, flash
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv




relative_static_path = "../frontend/static"
relative_templates_path = "../frontend/templates"

# MongoDB connection setup
mongodb_connection_string = 'mongodb://localhost:27017'
# brew services start mongodb/brew/mongodb-community
client = MongoClient(mongodb_connection_string)
db = client['user_credentials']  
users = db.users  

app = Flask(__name__,
            static_url_path='', 
            static_folder=relative_static_path,
            template_folder=relative_templates_path )

load_dotenv() # Load .env file data
app.secret_key = os.getenv("luli_secret_key") # Load secret key into flask app
os.environ.pop('luli_secret_key', None) # Delete secret key from environment variables

@app.route('/')
def serve_welcome_page():
    return "Welcome!"

@app.route('/Create_Account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists in the database
        if users.find_one({'username': username}):
            flash('Username already exists. Choose a different one.', 'error')
            return redirect(url_for('login'))
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        # Insert new user into the database
        print(f"INSERTING: {username}::{hashed_password} into {users}")
        users.insert_one({'username': username, 'password': hashed_password})
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('serve_welcome_page')) 
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
        user_document = users.find_one({'username': username})
        
        if user_document:
            # A document for the user exists, now check the password
            stored_hash = user_document['password']
            if check_password_hash(stored_hash, password):
                # The hash matches the password provided
                # Login is successful
                # (Here you'd set up the user session and redirect to the next page)
                flash('Login successful!', 'success')
                return redirect(url_for('serve_welcome_page'))  # Assuming you have a dashboard route
            else:
                # The hash does not match the password provided
                flash('Login failed. Incorrect password.', 'error')
        else:
            # No user document with that username exists
            flash('Login failed. Username not found.', 'error')
        
        # For both cases above, if login failed, redirect back to login page
        return redirect(url_for('login'))
    
    # If it's a GET request, just render the login page
    return app.send_static_file('login.html')


if __name__ == "__main__":
    ### How to run this file ###
    """
    1. Create a virtualenv and install packages
        $ pip3 install virtualenv           [ only run this once]
        $ virtualenv venv                   [ this create a virtual python environment called "venv"]
        $ activate venv/bin/activate        [ mac only, this is how to enable the venv so it doesnt install packages to your global python]
        $ pip install -r requirements.txt   [ this installs the necessary modules for the code to run (i.e. Flask)]
    2. cd Luli/backend
    3. python main.py
    3. View the url in the output           [ usually http://127.0.0.1:5000 ]
    4. Open it in browser
    """


    print("Starting Flask server...")
    app.run(debug=True)