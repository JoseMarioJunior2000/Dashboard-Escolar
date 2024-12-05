from flask import Flask
import os
from configuration import configure_all
from services.repository_instances import repository

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['SECRET_KEY'] = os.urandom(24) 

configure_all(app)

if __name__ == '__main__':
    with repository:
        app.run(debug=True)