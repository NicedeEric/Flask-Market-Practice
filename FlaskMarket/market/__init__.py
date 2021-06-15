from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import stripe
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SECRET_KEY'] = '126059605bb3b26263f9a46e'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
# when decorated login_required, this login_view will direct which page should the user go
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'
from market import routes