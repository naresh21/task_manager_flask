# coding=utf-8
"""
This file is used to get all configs related to App
"""
import os

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length, DataRequired

db = SQLAlchemy()
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target_sql_path = os.path.join(APP_ROOT, 'xls_data_db.db')


class User(UserMixin, db.Model):
    """
    This class is used for User table
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(10))
    latest_task = db.Column(db.String(10))


class Details(UserMixin, db.Model):
    """
    Table Structure of Details Table
    """
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(200))
    task_title = db.Column(db.String(50))
    milestone = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    estimated_hours = db.Column(db.String(50))
    qa = db.Column(db.String(200))
    developer = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    type = db.Column(db.String(50))
    description = db.Column(db.String(500))
    added_on = db.Column(db.String(10))


class LoginForm(FlaskForm):
    """
    This class is used for login form
    """
    username = StringField('Username', validators=[InputRequired(), Length(min=5, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=3, max=80)])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    """
    This class is used for registration form
    """
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Developer name as per ERP', validators=[InputRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=3, max=80)])
    role = SelectField('Role', choices=[('developer', 'Developer'), ('admin', 'Admin')], validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    """
    This class is used for change password form
    """
    current_password = PasswordField('Current Password', validators=[InputRequired(), Length(min=5, max=80)])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=5, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=5, max=80)])


def get_secret_key():
    """
    This is used to get secret key
    :return: returns secret key
    """
    return 'Thisissupposedtobesecret!'


def get_sql_path():
    """
    This is used to get database path
    :return: returns database path
    """
    return 'sqlite:///' + target_sql_path
