#-*- coding:utf-8 -*-
from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField, URLField
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length

_required_text = 'necessary'

validators = {
    'email': [
        DataRequired(message=_required_text),
    ],
    'username': [
        DataRequired(message=_required_text),
        Length(min=2, max=18, message='user length from 2 to 8')
    ],
    'password': [
        DataRequired(message=_required_text),
        Regexp(regex=r'^[A-Za-z0-9@#$%^&+=_-]{6,18}$',message='wrong password format')
    ]
}

class LoginForm(Form):
    email = EmailField('mail', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    # recaptcha = RecaptchaField('验证码', validators=[DataRequired()])

class RegisterForm(Form):
    email = EmailField('mail', validators=validators['email'])
    username = StringField('user', validators=validators['username'])
    password = PasswordField('password', validators=validators['password'])
    repeat = PasswordField('repeat password', validators=validators['password'])

class BaseEntryForm(Form):
    title = StringField('name', validators=[DataRequired(message=_required_text)])
    type = StringField('catelogue', validators=[DataRequired(message=_required_text)])

class ProfileForm(Form):
    username = StringField('username', validators=validators['username'])
    location = StringField('area', validators=[Length(max=64)])
    website = URLField('Homepage', validators=[Length(max=256)])
    introduction = TextAreaField('Introduction', validators=[Length(max=1024)])
