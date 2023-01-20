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