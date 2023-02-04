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


def test_user_can_retrieve_own_hikes():
    pass


def test_anonymous_only_retrieves_public_hikes():
    pass


def test_user_can_retrieve_hikes_of_public_user():
    pass


def test_user_cannot_retrieve_hikes_of_unaccepted_friends_user():
    pass


def test_user_can_retrieve_hikes_of_accepted_friends_user():
    pass

 
def test_user_cannot_retrieve_hikes_of_private_user():
    pass




# def test_hikes_by_user_on_trail_can_be_listed(dummy_db,admin_user,regular_user,dummy_existing_trail,dummy_existing_trail2):
#     dummy_db.session.add_all([admin_user,regular_user])
#     dummy_db.session.commit()
#     tm = TrailManager(session=dummy_db.session,user=admin_user)
#     trail1 = tm.add_trail(**dummy_existing_trail)
#     trail2 = tm.add_trail(**dummy_existing_trail2)

#     hm_admin = HikeManager(session=dummy_db.session,user=admin_user)
#     hike1 = hm_admin.add_hike(trail_id=trail1.id, km_start=0, km_end=2)
#     hike2 = hm_admin.add_hike(trail_id=trail1.id, km_start=4, km_end=6)
#     hike3 = hm_admin.add_hike(trail_id=trail2.id, km_start=8, km_end=10)

#     hm_user = HikeManager(session=dummy_db.session,user=regular_user)
#     hike4 = hm_user.add_hike(trail_id=trail1.id, km_start=1, km_end=3)
#     hike5 = hm_user.add_hike(trail_id=trail1.id, km_start=5, km_end=7)
#     hike6 = hm_user.add_hike(trail_id=trail2.id, km_start=9, km_end=11)

#     hikes = hm_user.list_hikes_by_user_on_trail(user_id=regular_user.id, trail_id=trail1.id)

#     assert hike1 not in hikes
#     assert hike2 not in hikes
#     assert hike3 not in hikes
#     assert hike4 in hikes
#     assert hike5 in hikes
#     assert hike6 not in hikes
