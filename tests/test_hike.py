from app.models import User, Trail, Hike, AuthorizationException, FileMissingException, LoggedInException, LocationException
from app.hikes.manager import HikeManager
from app.trails.manager import TrailManager
import pytest


def test_logged_in_user_can_add_hike(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add_all([regular_user,admin_user])
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm = HikeManager(session=dummy_db.session,user=regular_user)
    hike = hm.add_hike(trail_id=trail.id, km_start=0, km_end=5)
    assert hike


def test_anonymous_user_cannot_add_hike(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add_all([regular_user,admin_user])
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm = HikeManager(session=dummy_db.session)
    with pytest.raises(LoggedInException):
        hike = hm.add_hike(trail_id=trail.id, km_start=0, km_end=5)


def test_logged_in_user_can_delete_own_hike(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add_all([regular_user,admin_user])
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm = HikeManager(session=dummy_db.session,user=regular_user)
    hike = hm.add_hike(trail_id=trail.id, km_start=0, km_end=5)
    
    hm.delete_hike(id=hike.id)
    hikes = Hike.query.all()
    assert not hikes


def test_user_cannot_delete_another_users_hike(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add_all([regular_user,admin_user])
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm1 = HikeManager(session=dummy_db.session,user=admin_user)
    hike = hm1.add_hike(trail_id=trail.id, km_start=0, km_end=5)

    hm2 = HikeManager(session=dummy_db.session,user=regular_user)
    with pytest.raises(AuthorizationException):
        hm2.delete_hike(id=hike.id)


def test_logged_in_user_can_edit_own_hike(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm = HikeManager(session=dummy_db.session,user=admin_user)
    hike = hm.add_hike(trail_id=trail.id, km_start=0, km_end=5)

    hike = hm.edit_hike(id=hike.id,new_km_end=20)
    assert hike.km_end == 20


def test_user_cannot_edit_another_users_hike(dummy_db,admin_user,regular_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm1 = HikeManager(session=dummy_db.session,user=admin_user)
    hike = hm1.add_hike(trail_id=trail.id, km_start=0, km_end=5)

    hm2 = HikeManager(session=dummy_db.session,user=regular_user)
    with pytest.raises(AuthorizationException):
        hike = hm2.edit_hike(id=hike.id,new_km_end=20)


def test_user_cannot_add_hike_with_wrong_endpoints(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm = HikeManager(session=dummy_db.session,user=admin_user)
    with pytest.raises(LocationException):
        hike = hm.add_hike(trail_id=trail.id, km_start=0, km_end=1000)

    with pytest.raises(LocationException):
        hike = hm.add_hike(trail_id=trail.id, km_start=-100, km_end=5)


def test_user_cannot_edit_hike_with_wrong_endpoints(dummy_db,admin_user,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    hm = HikeManager(session=dummy_db.session,user=admin_user)
    hike = hm.add_hike(trail_id=trail.id, km_start=0, km_end=10)

    with pytest.raises(LocationException):
        hm.edit_hike(id=hike.id, new_km_end=1000)
 
    with pytest.raises(LocationException):
        hm.edit_hike(id=hike.id, new_km_start=1000)
 