from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import and_
from flask_login import UserMixin
import os



basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
migrate=Migrate()
