# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import Email, DataRequired, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)],
                        render_kw={'placeholder':'邮箱'})
    password = PasswordField('', validators=[DataRequired()], render_kw={'placeholder': '密码'})
    remember_me = BooleanField('记住密码')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)],
                        render_kw={'placeholder': '请输入注册邮箱'})
    username = StringField('', validators=[DataRequired(), Length(2, 20),
                    Regexp('^[_a-zA-Z][_0-9a-zA-Z\.]*$', 0, '昵称只能由字母，下划线，英文点号和数字构成')],
                        render_kw={'placeholder': '请输入昵称，2到20个字符'})
    password = PasswordField('', validators=[
                    DataRequired(), EqualTo('password2', message='密码必须一致')],
                        render_kw={'placeholder': '请输入密码'})
    password2 = PasswordField('', validators=[DataRequired()],
                        render_kw={'placeholder': '请再次输入密码'})
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('用户名已被占用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('', validators=[DataRequired()], render_kw={'placeholder': '旧的登录密码'})
    new_password = PasswordField('', validators=[DataRequired(),EqualTo('new_password2', message='新的密码必须一致')],
                                 render_kw={'placeholder': '新密码'})
    new_password2 = PasswordField('', validators=[DataRequired()], render_kw={'placeholder': '请再次输入新密码'})
    submit = SubmitField('修改密码')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)],
                        render_kw={'placeholder': '请输入注册时使用的邮箱地址'})
    submit = SubmitField('重置密码')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('', validators=[DataRequired(), EqualTo('new_password2', message='密码必须一致')],
                                render_kw={'placeholder': '请输入新的登录密码'})
    new_password2 = PasswordField('', validators=[DataRequired()],
                                render_kw={'placeholder': '请再次输入新的登录密码'})
    submit = SubmitField('重置密码')


class ChangeEmailForm(FlaskForm):
    password = PasswordField('', validators=[DataRequired()],
                                render_kw={'placeholder': '请输入现在邮箱的登录密码'})
    email = StringField('', validators=[Email('电子邮箱格式错误'), DataRequired(), Length(1, 64)],
                                render_kw={'placeholder': '请输入要修改的新的邮箱'})
    submit = SubmitField('修改邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
