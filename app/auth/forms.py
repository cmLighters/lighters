# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import Email, DataRequired, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)])
    username = StringField('昵称', validators=[DataRequired(), Length(1, 64),
                    Regexp('^[_a-zA-Z][_0-9a-zA-Z\.]*$', 0, '昵称只能由字母，下划线，英文点号和数字构成')])
    password = PasswordField('密码', validators=[
                    DataRequired(), EqualTo('password2', message='密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('用户名已被占用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧的密码', validators=[DataRequired()])
    new_password = PasswordField('新的密码', validators=[DataRequired(),
                                                             EqualTo('new_password2', message='新的密码必须一致')])
    new_password2 = PasswordField('再次输入新密码', validators=[DataRequired()])
    submit = SubmitField('修改密码')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('请输入您的注册邮箱', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)])
    submit = SubmitField('重置密码')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('新的密码', validators=[DataRequired(),
                                                             EqualTo('new_password2', message='密码必须一致')])
    new_password2 = PasswordField('请再次输入新的密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')


class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)])
    password = PasswordField('登录密码', validators=[DataRequired()])
    submit = SubmitField('修改邮箱')

    def valid_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
