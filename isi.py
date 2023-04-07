from app import *
from werkzeug.security import generate_password_hash, check_password_hash
app.app_context().push()

db.drop_all()
db.create_all()

user = User()
user.username = 'kentang'
user.password = generate_password_hash('goreng', method='sha256')
user.email = 'kentangtobat@gmail.com'

db.session.add(user)
db.session.commit()