from app.models import User, PrivacyOption
from app.auth.manager import UserManager


def test_password_is_hashed():
    u = User(username='susan')
    u.set_password('cat')
    assert not u.check_password('dog')
    assert u.check_password('cat')


def test_avatar_is_obtained():
    u = User(username='john', email='john@example.com')
    assert u.avatar(128) ==  ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128')


def test_user_can_be_added_by_anyone(dummy_db,user_alice):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice)
    assert alice


def test_public_user_can_be_followed(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.public)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)
    assert um.is_following_accepted(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)
    

def test_private_user_cannot_be_followed(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.private)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)
    a = um.is_following(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)


def test_friends_user_must_accept_follow_request(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)
    assert um.is_following(source_user=alice,target_user=bob)
    assert not um.is_following_accepted(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)

    um_bob = UserManager(session=dummy_db.session,user=bob)
    um_bob.accept_following(source_username=alice.username)
    assert um.is_following_accepted(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)


def test_switching_privacy_to_public_accepts_all_follow_requests(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.friends)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)
    assert um.is_following(source_user=alice,target_user=bob)
    assert not um.is_following_accepted(source_user=alice,target_user=bob)

    um_bob = UserManager(session=dummy_db.session,user=bob)
    um_bob.set_privacy(new_privacy=PrivacyOption.public)
    assert um.is_following_accepted(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)


def test_switching_privacy_to_private_removes_all_followers(dummy_db,user_alice,user_bob):
    um = UserManager(session=dummy_db.session)
    alice = um.add_user(**user_alice,privacy=PrivacyOption.public)
    bob = um.add_user(**user_bob,privacy=PrivacyOption.public)

    um_alice = UserManager(session=dummy_db.session,user=alice)
    um_alice.follow_user(target_username=bob.username)
    assert um.is_following_accepted(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)

    um_bob = UserManager(session=dummy_db.session,user=bob)
    um_bob.set_privacy(new_privacy=PrivacyOption.private)

    assert not um.is_following_accepted(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=alice,target_user=bob)
    assert not um.is_following(source_user=bob,target_user=alice)