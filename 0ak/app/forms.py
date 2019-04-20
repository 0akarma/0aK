# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from app.models import Category


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class SettingForm(FlaskForm):
    head_title = StringField('Head Title', validators=[DataRequired(), Length(1, 70)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[Length(0, 100)])
    blog_author_name = StringField('Blog Author Name', validators=[DataRequired(), Length(1, 100)])
    blog_author_avator = StringField('Blog Author Avator', validators=[DataRequired(), Length(1, 100)])
    blog_author_description = StringField('Blog Author Description', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField()


class PostForm(FlaskForm):
    title = StringField('Title', validators=[Length(0, 150)])
    slug = StringField('Slug', validators=[DataRequired(), Length(1, 100)])
    timestamp = StringField('CreateTime', validators=[DataRequired(), Length(1, 20)])
    category = SelectField('Category', coerce=int, default=1)
    tags = StringField('Tags', validators=[DataRequired(), Length(1, 100)])
    poster = StringField('Poster_URL')
    desc = CKEditorField('Desc')
    Body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.cid, category.cname)
                                 for category in Category.query.order_by(Category.cid).all()]


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(cname=field.data).first():
            raise ValidationError('Name already in use.')


class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()
