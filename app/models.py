from app import db
from flask_login import UserMixin
from app import login
from hashlib import md5
from datetime import datetime
from time import time
import jwt
from flask import current_app
import json

class User(UserMixin, db.Model):
    ''' User model '''
    id = db.Column(db.Integer, primary_key = True)

    # User Name
    username = db.Column(db.String(128), index=True)

    # Last seen
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    role = db.Column(db.SmallInteger)

    notifications = db.relationship('Notification',
                                    backref='user',
                                    lazy='dynamic')

    # Function to set the password
    def set_password(self, password):
        ''' generates password hash '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        ''' checks password against stored hash '''
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.configconfig['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.configconfig['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def avatar(self, size=128):
        ''' Returns URL for Gravatar '''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), index=True)

    created = db.Column(db.DateTime, default=datetime.utcnow)

    players = db.relationship('User', backref='game', lazy='dynamic')

    def set_host(self, user):
        ''' adds a host to the game '''
        if not user in self.players:
            self.players.append(user)
        user.role = current_app.config['ROLES']['HOST']
        db.session.add(user)

    def get_host(self):
        ''' returns the host '''
        for u in self.players:
            if u.role == current_app.config['ROLES']['HOST']:
                return u

    def get_join_token(self, expires_in=600):
        return jwt.encode(
            {'join_game': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_join_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['join_game']
        except:
            return
        return Game.query.get(id)

    def __repr__(self):
        return f'<Game {self.name}>'


# User loader for Flask Login module
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
