from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, DateField, SelectField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange
from flask_babel import _, lazy_gettext as _l
from app.models import User, Trail
from datetime import datetime


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class EditTrailForm(FlaskForm):
    displayname = StringField('Display name', validators=[DataRequired()])
    fullname = StringField('Full name', validators=[DataRequired()])
    length = FloatField('Length', validators=[DataRequired(),NumberRange(min=0)])
    filename = StringField('Filename', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_displayname="", original_fullname="", original_length=0, original_filename="", *args, **kwargs):
        super(EditTrailForm, self).__init__(*args, **kwargs)
        self.original_displayname = original_displayname
        self.original_fullname = original_fullname
        self.original_length = original_length
        self.original_filename = original_filename
        

class HikeForm(FlaskForm):
    trail = SelectField('Trail', validators=[DataRequired()])
    timestamp = DateField('Date', validators=[DataRequired()])
    km_start = FloatField('Start km', validators=[DataRequired()])
    km_end = FloatField('End km', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, og_timestamp=datetime.utcnow, og_km_start=99, og_km_end=101, *args, **kwargs):
        super(HikeForm, self).__init__(*args, **kwargs)
        self.og_timestamp = og_timestamp
        self.og_km_start = og_km_start
        self.og_km_end = og_km_end
        self.trail.choices = [(t.id, t.displayname) for t in Trail.query.order_by(Trail.displayname).all()]