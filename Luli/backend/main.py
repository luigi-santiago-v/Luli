#########################################
#           Luli Hydroponics            #
#      Backend Code made with Flask    #
#########################################


from flask import Flask, render_template
import os

relative_static_path = "../frontend/static"


relative_templates_path = "../frontend/templates"



app = Flask(__name__,
            static_url_path='', 
            static_folder=relative_static_path,
            template_folder=relative_templates_path )

@app.route('/')
def serve_welcome_page():
    return "Welcome!"

@app.route('/Login') # This line says "When the user goes to {our_URL}/Login, run the next function"
def serve_login():
    print(f"Serving: {os.path.join(relative_static_path, 'Login.html')}")
    return app.send_static_file('Login.html')


if __name__ == "__main__":
    ### How to run this ###
    """
    1. Create a virtualenv and install packages
        $ pip3 install virtualenv           [ only run this once]
        $ virtualenv venv                   [ this create a virtual python environment called "venv"]
        $ activate venv/bin/activate        [ mac only, this is how to enable the venv so it doesnt install packages to your global python]
        $ pip install -r requirements.txt   [ this installs the necessary modules for the code to run (i.e. Flask)]
    2. python main.py
    3. View the url in the output           [ usually http://127.0.0.1:5000 ]
    4. Open it in browser
    """


    print("Starting Flask server...")
    app.run(debug=True)