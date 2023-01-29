import pytest
from app import db, create_app
import os
from flask import Flask
os.environ['DATABASE_URL'] = 'sqlite://'

@pytest.fixture()
def fakedb():
    app = create_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()
    app_context.pop()

@pytest.fixture()
def regular_user():
    user = User(username="user", email="user@gmail.com",is_admin=False)
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture()
def admin_user():
    user = User(username="admin", email="admin@gmail.com",is_admin=True)
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    return user