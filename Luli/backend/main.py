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

def custom_flash(message, category, return_page):
    # Create a response object that redirects the user to the specified page.
    # The 'return_page' parameter should be the endpoint name as a string
    response = make_response(redirect(url_for(return_page)))

    # Set two cookies in the response: one for the flash message text and another for the category of the message.
    # These cookies are temporary and should be read and then cleared by the client-side code once displayed to the user.
    response.set_cookie('flash_message', message)
    response.set_cookie('flash_category', category)

    # Return the modified response object, which now includes the redirection and the set cookies.
    return response

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
    return app.send_static_file('Luli.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists in the database
        if users.find_one({'username': username}):
            return custom_flash('Username already exists. Choose a different one.', 'error', 'login')
            
        
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        # Insert new user into the database
        print(f"INSERTING: {username}::{hashed_password} into {users}")
        current_time = datetime.now()
        users.insert_one({'username': username, 'password': hashed_password, 'created':current_time})
        
        return custom_flash('Account created successfully!', 'success', 'serve_welcome_page')
        
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
        user_mongo_id = user_document['_id']
            

        if user_document:
            # A document for the user exists, now check the password
            stored_hash = user_document.get('password')
            if check_password_hash(stored_hash, password):
                # The hash matches the password provided
                # Login is successful
                # (Here you'd set up the user session and redirect to the next page)
                # NOTE: flash not implemented yet because current HTML is not a Flask template
                ##flash('Login successful!', 'success')
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = str(user_document['_id'])
                users.update_one({'_id': user_mongo_id}, {'$set': {'last_login': datetime.now()}})
                return redirect(url_for('serve_welcome_page')) 
            else:
                # The hash does not match the password provided
                # Don't tell the user the password was wrong, just say the credentials were incorrect
                #   prevents account enumeration attacks
                return custom_flash("Incorrect credentials.", "error", "login")
        else:
            # No user document with that username exists
            # Don't tell the user the username was wrong, just say the credentials were incorrect
            #   prevents account enumeration attacks
            return custom_flash("Incorrect credentials.", "error", "login")
    # If it's a GET request, just render the login page
    return app.send_static_file('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


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