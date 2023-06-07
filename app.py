import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from extensions import *
from blueprint import rentalblueprint,loginBlueprint,mobilBlueprint,transaksiBlueprint,invoiceBlueprint
from models import User

UPLOAD_FOLDER = 'static\img'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=\
    'sqlite:///'+os.path.join(basedir,'rental.db')
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config['SECRET_KEY']= 'ndaktauapa'

db.init_app(app)
migrate.init_app(app,db = db)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.register_blueprint(rentalblueprint) 
app.register_blueprint(loginBlueprint) 
app.register_blueprint(mobilBlueprint) 
app.register_blueprint(transaksiBlueprint) 
app.register_blueprint(invoiceBlueprint) 


if __name__ == "__main__":
    app.run(debug =True)