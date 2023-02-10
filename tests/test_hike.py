from app.models import User, Trail, Hike, AuthorizationException, FileMissingException, LoggedInException, LocationException
from app.hikes.manager import HikeManager
from app.trails.manager import TrailManager
from app.auth.manager import UserManager, PrivacyOption
import pytest

# Testing hike CRUD

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

# Testing Hike retrieval with privacy in mind

def test_anonymous_only_retrieves_public_hikes(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.friends)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.private)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    hm_anon = HikeManager(session=dummy_db.session)
    hikes = hm_anon.list_hikes()
    assert hike_alice in hikes
    assert not hike_bob in hikes
    assert not hike_charlie in hikes

    hike = hm_anon.list_hikes(hike_id=hike_alice.id)
    assert hike

    hike = hm_anon.list_hikes(hike_id=hike_bob.id)
    assert not hike

    hike = hm_anon.list_hikes(hike_id=hike_charlie.id)
    assert not hike

def test_user_can_retrieve_own_hikes(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.private)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.private)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.public)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    hikes = hm_alice.list_hikes(username=alice.username)
    assert hike_alice in hikes
    assert hike_bob not in hikes
    assert hike_charlie not in hikes

    hike = hm_alice.list_hikes(hike_id=hike_alice.id)
    assert hike
    
def test_user_can_retrieve_hikes_of_public_users(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.friends)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.private)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)
    hikes = hm_charlie.list_hikes()
    assert hike_alice in hikes
    assert not hike_bob in hikes
    assert hike_charlie in hikes

    hike = hm_charlie.list_hikes(hike_id=hike_alice.id)
    assert hike
    hike = hm_charlie.list_hikes(hike_id=hike_bob.id)
    assert not hike
    hike = hm_charlie.list_hikes(hike_id=hike_charlie.id)
    assert hike


def test_user_cannot_retrieve_hikes_of_unaccepted_friends_user(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.friends)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.private)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)

    hikes = hm_alice.list_hikes()
    assert hike_alice in hikes
    assert not hike_bob in hikes
    assert not hike_charlie in hikes
    
    hike = hm_alice.list_hikes(hike_id=hike_alice.id)
    assert hike
    hike = hm_alice.list_hikes(hike_id=hike_bob.id)
    assert not hike
    hike = hm_alice.list_hikes(hike_id=hike_charlie.id)
    assert not hike

def test_user_can_retrieve_hikes_of_accepted_friends_user(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.friends)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.private)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)

    um_bob = UserManager(session=dummy_db.session,user=bob)
    um_bob.accept_following(source_username=alice.username)

    hikes = hm_alice.list_hikes()
    assert hike_alice in hikes
    assert hike_bob in hikes
    assert not hike_charlie in hikes

    hike = hm_alice.list_hikes(hike_id=hike_alice.id)
    assert hike
    hike = hm_alice.list_hikes(hike_id=hike_bob.id)
    assert hike
    hike = hm_alice.list_hikes(hike_id=hike_charlie.id)
    assert not hike

    
def test_user_cannot_retrieve_hikes_of_private_user(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.public)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.private)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    hikes = hm_alice.list_hikes()
    assert hike_alice in hikes
    assert hike_bob in hikes
    assert not hike_charlie in hikes

    hike = hm_alice.list_hikes(hike_id=hike_alice.id)
    assert hike
    hike = hm_alice.list_hikes(hike_id=hike_bob.id)
    assert hike
    hike = hm_alice.list_hikes(hike_id=hike_charlie.id)
    assert not hike


def test_user_cannot_retrieve_hikes_of_other_users_that_are_friends(dummy_db,admin_user,user_alice,user_bob,user_charlie,dummy_existing_trail):
    dummy_db.session.add(admin_user)
    dummy_db.session.commit()
    tm = TrailManager(session=dummy_db.session,user=admin_user)
    trail = tm.add_trail(**dummy_existing_trail)

    um_anon = UserManager(session=dummy_db.session)
    alice = um_anon.add_user(**user_alice,privacy=PrivacyOption.friends)
    bob = um_anon.add_user(**user_bob,privacy=PrivacyOption.friends)
    charlie = um_anon.add_user(**user_charlie,privacy=PrivacyOption.public)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)
    um_bob = UserManager(session=dummy_db.session,user=bob)
    um_bob.accept_following(source_username=alice.username)

    um_bob.follow_user(target_username=alice.username)
    um_alice.accept_following(source_username=bob.username)

    hm_alice = HikeManager(session=dummy_db.session,user=alice)
    hike_alice = hm_alice.add_hike(trail_id=trail.id, km_start=0, km_end=3)
    hm_bob = HikeManager(session=dummy_db.session,user=bob)    
    hike_bob = hm_bob.add_hike(trail_id=trail.id, km_start=6, km_end=9)
    hm_charlie = HikeManager(session=dummy_db.session,user=charlie)    
    hike_charlie = hm_charlie.add_hike(trail_id=trail.id, km_start=12, km_end=15)

    hikes = hm_charlie.list_hikes()
    assert not hike_alice in hikes
    assert not hike_bob in hikes
    assert hike_charlie in hikes

    hike = hm_charlie.list_hikes(hike_id=hike_alice.id)
    assert not hike
    hike = hm_charlie.list_hikes(hike_id=hike_bob.id)
    assert not hike
    hike = hm_charlie.list_hikes(hike_id=hike_charlie.id)
    assert hike
