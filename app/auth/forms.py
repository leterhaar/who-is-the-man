from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Game

class UserRegistrationForm(FlaskForm):

    username = StringField(_l('What is your name?'), validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField(_l('Sign in'))

    def __init__(self, game=None):
        super().__init__()
        self.game = game

    def validate_username(self, name):
        ''' checks when joining a game that this username does not already exist in that game '''
        if self.game:
            if name.data in [x.username for x in self.game.players]:
                raise ValidationError(_l('This username already exists in this game, please use another'))


class CreateGameForm(FlaskForm):
    name = StringField(_l('How do you want to call your game?'), validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField(_l('Create game'))

    def validate_name(self, name):
        ''' checks if a game name is already existing '''
        game = Game.query.filter_by(name=name.data).first()
        if game is not None:
            raise ValidationError(_l('This name already exists, please use another'))
