import cloudinary
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:Admin123%40@localhost/garadb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 5
app.secret_key = "ekdbhjkq"

cloudinary.config(cloud_name='dvfuzolim',
                  api_key='111592365327791',
                  api_secret='fa0Wq3HWyQcM_XOSQQhZmjqBLaw')

db = SQLAlchemy(app)
login = LoginManager(app)