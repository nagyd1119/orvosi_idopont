from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import models

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://instance/idopontfoglalo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

db = SQLAlchemy(app)

from models import *


if __name__ == '__main__':
    app.run()
