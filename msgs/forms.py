from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class ConversationForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    submit = SubmitField()


class MessageForm(FlaskForm):
    content = StringField(validators=[DataRequired()])
    submit = SubmitField()
