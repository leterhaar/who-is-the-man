from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class RegistrationForm(FlaskForm):

    username = StringField(_l('What is your name?'), validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField(_l('Sign in'))
