from flask_wtf import FlaskForm
from flask import current_app
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_babel import _, lazy_gettext as _l

class SettingsForm(FlaskForm):

    num_rounds = IntegerField(label=_l('Number of cards'), default=3, description=_l('How many cards does each player write?'),
                              validators=[DataRequired(), NumberRange(min=1, max=10)])

    round_time = IntegerField(label=_l('Duration of rounds'), default=30,
                             description=_l('How many seconds does each round take?'), validators=[DataRequired(), NumberRange(min=10, max=120)])

    num_cards = IntegerField(label=_l('Number of rounds'), default=3,
                             description=_l('How many rounds do you want to play?'), validators=[DataRequired(), NumberRange(min=1, max=20)])


    submit = SubmitField(_l("Next"))


class SelectTeamsForm(FlaskForm):

    # empty form - fields are added in route 
    submit = SubmitField(_l('Start game!'))
