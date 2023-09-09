from flask import redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class Upload(FlaskForm):
    status = RadioField('Status', choices=[('Public'),('Private')], validators=[DataRequired()])
    upload = FileField("Upload Image", validators=[FileRequired(), FileAllowed(['jpg','png','jpeg'],'Images only!')])
    submit = SubmitField("Generate")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please choose a different username.')
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Please use a different email address.')