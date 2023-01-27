from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, SelectField, DecimalRangeField, DateField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange, InputRequired
from flask_babel import _, lazy_gettext as _l
from app.models import User, Trail, Hike
from datetime import datetime
from pathlib import Path


class HikeForm(FlaskForm):
    timestamp = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    km_start = FloatField('Start km', validators=[InputRequired()])
    km_end = FloatField('End km', validators=[InputRequired()])
    submit = SubmitField('Submit')

    def __init__(self, trail_id, *args, **kwargs):
        super(HikeForm, self).__init__(*args, **kwargs)
        self.trail_id = trail_id

    def validate_km_start(self, form):
        t = Trail.query.where(Trail.id==self.trail_id).one()
        if self.km_start.data > t.length or self.km_start.data < 0:
            raise ValidationError(f"The {t.displayname} has a length of {t.length} km, so this value must be between 0 and {t.length}")

    def validate_km_end(self, form):
        t = Trail.query.where(Trail.id==self.trail_id).one()
        if self.km_end.data > t.length or self.km_end.data < 0:
            raise ValidationError(f"The {t.displayname} has a length of {t.length} km, so this value must be between 0 and {t.length}")

    def fill_from_hike(self, hike):
        self.timestamp.data = hike.timestamp
        self.km_start.data = hike.km_start
        self.km_end.data = hike.km_end


class TrailSelectionForm(FlaskForm):
    trail = SelectField('Trail', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(TrailSelectionForm, self).__init__(*args, **kwargs)
        self.trail.choices = [(t.id, t.dispname) for t in Trail.query.order_by(Trail.name).all()]