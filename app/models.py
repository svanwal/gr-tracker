from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import PickleType
import csv
from enum import Enum


class PrivacyOption(Enum):
    public = "public"
    friends = "friends"
    private = "private"


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('accepted', db.Boolean, default=False),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    hikes = db.relationship('Hike', backref='walker', lazy='dynamic')
    about_me = db.Column(db.String(140))
    privacy = db.Column(db.Enum(PrivacyOption), nullable=False, default=PrivacyOption.public)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_following(self, target_user):
        following = Following.query.where(Following.source_id==self.id).where(Following.target_id==target_user.id).one_or_none()
        if following:
            return True
        return False

    def is_following_accepted(self, target_user):
        following = Following.query.where(Following.source_id==self.id).where(Following.target_id==target_user.id).one_or_none()
        if following and following.accepted:
            return True
        return False

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accepted = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, source_id, target_id, accepted=False):
        self.source_id = source_id
        self.target_id = target_id
        self.accepted = accepted

    def __repr__(self):
        return f"User <{self.source_id}> is following user <{self.target_id}>, accepted: {self.accepted}"


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Trail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    dispname = db.Column(db.String(30), unique=True, nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    length = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    hikes = db.relationship('Hike', backref='path', lazy='dynamic')

    def __init__(self, name, dispname, fullname):
        self.name = name
        self.dispname = dispname
        self.fullname = fullname
        self.calculate_length()
        
    def calculate_length(self):
        geometry = self.get_geometry()
        length = geometry.distances[-1]
        self.length = round(10*length)/10
        
    def __repr__(self):
        return f"<Trail {self.name}: {self.fullname} (spans {self.length} km)>"

    @property
    def filename(self):
        return f"app/data/{self.name.lower()}.csv"

    def fill_from_form(self, form):
        self.name = form.name.data
        self.dispname = form.dispname.data
        self.fullname = form.fullname.data
        self.calculate_length()

    def get_geometry(self):
        return TrailGeometry(trail=self)

    def get_coordinate_range(self, km_start, km_end):
        geometry = self.get_geometry()
        dcum_start = min(geometry.distances, key=lambda x:abs(x-km_start))
        i_start = geometry.distances.index(dcum_start)
        dcum_end = min(geometry.distances, key=lambda x:abs(x-km_end))
        i_end = geometry.distances.index(dcum_end)
        return geometry.coordinates[i_start:i_end]


class TrailGeometry():
    def __init__(self,trail):
        with open(trail.filename, newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            data = list(reader)
        coordinates = [[float(row[1]),float(row[0])] for row in data]
        distances = [float(row[3]) for row in data]
        center = coordinates[int(len(coordinates)/2)]
        self.coordinates = coordinates
        self.distances = distances
        self.center = center


class Hike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trail_id = db.Column(db.Integer, db.ForeignKey('trail.id'))
    timestamp = db.Column(db.Date, default=datetime.utcnow)
    km_start = db.Column(db.Float, nullable=False)
    km_end = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"<Hike by user {self.user_id} on trail {self.trail_id}, km {self.km_start} to {self.km_end}>"

    def fill_from_form(self, form):
        self.timestamp = form.timestamp.data
        self.km_start = form.km_start.data
        self.km_end = form.km_end.data
        self.update_distance()

    def update_distance(self):
        self.distance = round(abs(self.km_start - self.km_end),1)


class AuthorizationException(Exception):
    def __init__(self):
        self.message = "You are not authorized to perform this action."


class FileMissingException(Exception):
    def __init__(self):
        self.message = "This action cannot be performed because a file is missing."


class LoggedInException(Exception):
    def __init__(self):
        self.message = "You must be logged in to perform that action."


class LocationException(Exception):
    def __init__(self):
        self.message = "One of the hike endpoints is invalid."


class ExistenceException(Exception):
    def __init__(self):
        self.message = "Database entry not found."