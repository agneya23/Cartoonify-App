from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    remaining_credits = db.Column(db.Integer)
    images = db.relationship('Image', backref='author', lazy='dynamic')

    def __repr__(self):
        return "<User {}>".format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), index=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(8), index=True)

    def __repr__(self):
        return "<Image {}>".format(self.url)
    
@login.user_loader
def load_user(id): # Not understood this function
    return User.query.get(int(id))