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

    team = db.Column(db.SmallInteger)

    notifications = db.relationship('Notification',
                                    backref='user',
                                    lazy='dynamic')

    def avatar(self, size=128):
        ''' Returns URL for Gravatar '''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def add_notification(self, name, data):
        #self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def is_host(self):
        return self.role == current_app.config['ROLES']['HOST']

    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), index=True)

    created = db.Column(db.DateTime, default=datetime.utcnow)

    players = db.relationship('User', backref='game', lazy='dynamic')

    settings = db.relationship('Setting', backref='game', lazy='dynamic')

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

    def setting(self, key, value=None):
        if value is None:
            return Setting.query.filter_by(game=self, key=key).first().value
        s = Setting(game=self, key = key, value = value)
        db.session.add(s)

    def __repr__(self):
        return f'<Game {self.name}>'

class Setting(db.Model):
    ''' class to store settings per game '''

    # define fields
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    key = db.Column(db.String(128))
    value = db.Column(db.String(128))

    def __repr__(self):
        return f'<Setting {self.key} for {self.game.name}>'

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
