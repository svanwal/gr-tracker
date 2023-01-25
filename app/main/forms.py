from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, SelectField, DecimalRangeField, DateField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange, InputRequired
from flask_babel import _, lazy_gettext as _l
from app.models import User, Trail
from datetime import datetime
from pathlib import Path


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

    def __init__(self, text="Submit"):
        self.submit = text


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



class HikeForm(FlaskForm):
    trail = SelectField('Trail', validators=[DataRequired()])
    timestamp = DateField('Date', validators=[DataRequired()])
    km_start = FloatField('Start km', validators=[InputRequired()])
    km_end = FloatField('End km', validators=[InputRequired()])
    submit = SubmitField('Submit')

    def __init__(self, og_timestamp=datetime.utcnow, og_km_start=99, og_km_end=101, *args, **kwargs):
        super(HikeForm, self).__init__(*args, **kwargs)
        self.og_timestamp = og_timestamp
        self.og_km_start = og_km_start
        self.og_km_end = og_km_end
        self.trail.choices = [(t.id, t.dispname) for t in Trail.query.order_by(Trail.name).all()]

    def set_trail(self, trail_id):
        self.trail.data = trail_id

    def validate_km_start(self, form):
        trail_id = self.trail.data
        t = Trail.query.where(Trail.id==trail_id).one()
        if self.km_start.data > t.length or self.km_start.data < 0:
            raise ValidationError(f"The {t.displayname} has a length of {t.length} km, so this value must be between 0 and {t.length}")

    def validate_km_end(self, form):
        trail_id = self.trail.data
        t = Trail.query.where(Trail.id==trail_id).one()
        if self.km_end.data > t.length or self.km_end.data < 0:
            raise ValidationError(f"The {t.displayname} has a length of {t.length} km, so this value must be between 0 and {t.length}")