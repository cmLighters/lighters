# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_pagedown.fields import PageDownField

from ..models import Role, User

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('您的姓名', validators=[Length(0, 64)])
    location = StringField('您的住址', validators=[Length(0, 64)])
    about_me = TextAreaField('个人介绍')
    submit = SubmitField('提交')


class AdminEditProfileForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    confirmed = BooleanField('账户已确认？')
    role = SelectField('用户等级', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('个人介绍')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(AdminEditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [ (role.id, role.name) for role in Role.query.order_by(Role.name).all() ]
        self.user = user

    def valid_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def valid_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被占用')


class PostForm(FlaskForm):
    title = StringField('请输入文章标题', validators=[Length(0, 128)])
    content = PageDownField('请输入文章内容', validators=[DataRequired()], id='post-form-content')
    submit = SubmitField('提交', id='post-form-submit')


class CommentForm(FlaskForm):
    content = TextAreaField('', validators=[DataRequired()],
                            render_kw={'placeholder': '说点什么', 'rows': 4, 'style': 'background-color: #eee;',
                                       'onpropertychange': "this.style.posHeight=this.scrollHeight "
    })
    submit = SubmitField('提交')
