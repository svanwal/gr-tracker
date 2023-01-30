import pytest
from app import db, create_app
import os
from flask import Flask
from app.models import User
from config import TestConfig

@pytest.fixture()
def dummy_db():
    os.environ['DATABASE_URL'] = 'sqlite:///test_db.sqlite'
    app = create_app(config_class=TestConfig)
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
    return user

@pytest.fixture()
def admin_user():
    user = User(username="admin", email="admin@gmail.com",is_admin=True)
    user.set_password("password")
    return user

@pytest.fixture()
def dummy_existing_trail():
    return{
        "name":"existingtrail",
        "dispname":"TestTrail",
        "fullname":"A Trail for Testing",
    }

@pytest.fixture()
def dummy_nonexisting_trail():
    return{
        "name":"nonexistingtrail",
        "dispname":"TestTrail",
        "fullname":"A Trail for Testing",
    }

@pytest.fixture()
def anonymous_user():
    return None
