from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import Email, DataRequired, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('What is your name?', validators=[Email(), DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
                    Regexp('^[_a-zA-Z][_0-9a-zA-Z\.]*$', 0, 'Usernames must have only letters, numbers, dots or '
+                   'underscores')])
    password = PasswordField('Password', validators=[
                    DataRequired(), EqualTo('password2', message='Passwords must equal')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def valid_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def valid_username(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Username already in use')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(),
                                                             EqualTo('new_password2', message='Passwords must equal')])
    new_password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update password')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    submit = SubmitField('Reset password')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New password', validators=[DataRequired(),
                                                             EqualTo('new_password2', message='Passwords must equal')])
    new_password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Reset password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New email', validators=[Email(), DataRequired(), Length(1, 64)])
    password = PasswordField('Origin password', validators=[DataRequired()])
    submit = SubmitField('Update email')

    def valid_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
