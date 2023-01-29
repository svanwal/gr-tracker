from app.models import User, Trail, AuthorizationException, FileMissingException
from app.trails.manager import TrailManager
import pytest


def test_admin_user_can_add_existing_trail(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)
    assert trail


def test_regular_user_cannot_add_existing_trail(dummy_db,regular_user,dummy_existing_trail):
    dummy_db.session.add(regular_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=regular_user)
    with pytest.raises(AuthorizationException):
        trail = tm.add_trail(**dummy_existing_trail)


def test_admin_user_cannot_add_nonexisting_trail(dummy_db,admin_user,dummy_nonexisting_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=admin_user)
    with pytest.raises(FileMissingException):
        trail = tm.add_trail(**dummy_nonexisting_trail)


def test_admin_user_can_delete_trail(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)
    assert trail
    tm.delete_trail(name=trail.name)
    trails = Trail.query.all()
    assert not trails


def test_regular_user_cannot_delete_trail(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm_admin = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm_admin.add_trail(**dummy_existing_trail)
    assert trail
    tm_regular = TrailManager(session=dummy_db.session,actor=regular_user)
    with pytest.raises(AuthorizationException):
        tm_regular.delete_trail(name=trail.name)


def test_admin_user_can_add_existing_trail(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)
    assert trail

    
def test_admin_user_can_edit_trail(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)
    assert trail
    tm.edit_trail(id=trail.id,new_dispname="new_dispname")
    trail = Trail.query.one()
    assert trail.dispname == "new_dispname"


def test_admin_user_cannot_edit_trail_with_missing_file(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)
    assert trail
    with pytest.raises(FileMissingException):
        tm.edit_trail(id=trail.id,new_name="nonexistingtrail")


def test_regular_user_cannot_edit_trail(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm_admin = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm_admin.add_trail(**dummy_existing_trail)
    assert trail
    tm_regular = TrailManager(session=dummy_db.session,actor=regular_user)
    with pytest.raises(AuthorizationException):
        tm_regular.edit_trail(id=trail.id,new_dispname="new_dispname")


def test_anyone_can_list_trails(dummy_db,admin_user,anonymous_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm_admin = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm_admin.add_trail(**dummy_existing_trail)
    tm_anonymous = TrailManager(session=dummy_db.session,actor=anonymous_user)
    trails = tm_anonymous.list_trails()
    assert len(trails) == 1


def test_anyone_can_list_single_trail(dummy_db,admin_user,anonymous_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm_admin = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm_admin.add_trail(**dummy_existing_trail)
    tm_anonymous = TrailManager(session=dummy_db.session,actor=anonymous_user)
    queried_trail = tm_anonymous.list_trails(name=trail.name)
    assert queried_trail.name == trail.name


def test_listing_missing_trail_returns_none(dummy_db,admin_user,anonymous_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm_admin = TrailManager(session=dummy_db.session,actor=admin_user)
    trail = tm_admin.add_trail(**dummy_existing_trail)
    tm_anonymous = TrailManager(session=dummy_db.session,actor=anonymous_user)
    queried_trail = tm_anonymous.list_trails(name="nonexistingtrail")
    assert not queried_trail
