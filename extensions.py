from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import and_,or_,not_
from sqlalchemy.orm import join
from flask_login import UserMixin
import os
from flask_login import LoginManager
from PyPDF2 import PdfWriter, PdfReader,PageObject
from PyPDF2.generic import AnnotationBuilder
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
migrate=Migrate()
login_manager = LoginManager()