from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, SelectField, DecimalRangeField, DateField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange, InputRequired
from flask_babel import _, lazy_gettext as _l
from app.models import User, Trail
from datetime import datetime
from pathlib import Path

class TrailForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    dispname = StringField('Display name', validators=[DataRequired()])
    fullname = StringField('Full name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def fill_from_trail(self, trail):
        self.name.data = trail.name
        self.dispname.data = trail.dispname
        self.fullname.data = trail.fullname

    def validate_name(self, form):
        path = Path(f"app/data/{self.name.data}.csv")
        print(f"Checking if {path} exists")
        if not path.is_file():
            raise ValidationError(f"Coordinate file not found. Please make sure {path} exists before adding this trail.")
